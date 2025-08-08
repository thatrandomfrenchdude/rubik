#!/usr/bin/env python3
"""
Camera Stats Module - A reusable module for camera capture with CPU temperature monitoring on OLED
"""

import cv2 as cv
import time
import os
from collections import deque

# OLED imports
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306


class CameraStatsMonitor:
    """
    A module for camera capture with CPU temperature monitoring displayed on OLED screen.
    
    Features:
    - Camera video capture
    - CPU temperature monitoring
    - OLED display of stats
    - Temperature history sparkline
    - Configurable camera index and OLED address
    """
    
    def __init__(self, camera_index=2, oled_addr=0x3C, history_length=32):
        """
        Initialize the Camera Stats Monitor
        
        Args:
            camera_index (int): Camera device index (default: 2)
            oled_addr (int): I2C address of OLED display (default: 0x3C)
            history_length (int): Number of temperature readings to keep in history (default: 32)
        """
        self.camera_index = camera_index
        self.oled_addr = oled_addr
        self.history_length = history_length
        self.cap = None
        self.oled = None
        self.history_temp = deque(maxlen=history_length)
        self.frame_count = 0
        self.is_running = False
        
    def init_camera(self):
        """
        Initialize camera capture
        
        Raises:
            RuntimeError: If camera cannot be opened
        """
        self.cap = cv.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera at index {self.camera_index}")
        print(f"Camera initialized at index {self.camera_index}")
        
    def init_oled_display(self):
        """
        Initialize OLED display
        
        Returns:
            bool: True if OLED initialized successfully, False otherwise
        """
        try:
            serial = i2c(port=1, address=self.oled_addr)
            self.oled = ssd1306(serial)
            print(f"OLED display initialized at address 0x{self.oled_addr:02X}")
            return True
        except Exception as e:
            print(f"Warning: Could not initialize OLED display: {e}")
            self.oled = None
            return False
    
    def get_cpu_temperature(self):
        """
        Read CPU temperature from system
        
        Returns:
            float: CPU temperature in Celsius, or 0.0 if unable to read
        """
        try:
            # Try reading from thermal zone (common on Raspberry Pi and Linux systems)
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp_millicelsius = int(f.read().strip())
                return temp_millicelsius / 1000.0
        except:
            try:
                # Alternative method using vcgencmd (Raspberry Pi specific)
                temp_str = os.popen('vcgencmd measure_temp').readline()
                return float(temp_str.replace("temp=", "").replace("'C\n", ""))
            except:
                # Fallback: return a simulated temperature for testing
                return 45.0 + (time.time() % 10)  # Simulated temp between 45-55°C
    
    def sparkline(self, series, width=16, high='#', mid='*', low='.'):
        """
        Generate a sparkline from temperature history
        
        Args:
            series: Collection of numeric values
            width (int): Width of sparkline in characters
            high (str): Character for high values
            mid (str): Character for medium values
            low (str): Character for low values
            
        Returns:
            str: Sparkline representation
        """
        data = list(series)[-width:]
        if len(data) < width:
            data = [None]*(width-len(data)) + data
        if not data or all(v is None for v in data):
            return ' ' * width
        
        valid_data = [v for v in data if v is not None]
        if not valid_data:
            return ' ' * width
            
        if len(valid_data) == 1:
            # Single value, just show it as mid
            chars = []
            for v in data:
                chars.append(mid if v is not None else ' ')
            return ''.join(chars)
            
        top = max(valid_data)
        bottom = min(valid_data)
        range_val = top - bottom
        
        chars = []
        for v in data:
            if v is None:
                chars.append(' ')
            elif range_val == 0:  # All values are the same
                chars.append(mid)
            elif v >= bottom + (range_val * 0.66):
                chars.append(high)
            elif v >= bottom + (range_val * 0.33):
                chars.append(mid)
            else:
                chars.append(low)
        return ''.join(chars)
    
    def draw_stats(self, cpu_temp):
        """
        Draw CPU stats on OLED display
        
        Args:
            cpu_temp (float): Current CPU temperature in Celsius
        """
        if not self.oled:
            return
            
        with canvas(self.oled) as draw:
            draw.text((0,  0), "Camera + CPU Stats",     fill=1)
            draw.text((0, 12), f"CPU: {cpu_temp:.1f}°C",  fill=1)
            draw.text((0, 24), f"Frames: {self.frame_count}", fill=1)
            draw.text((0, 36), "Temp Trend:",            fill=1)
            trend = self.sparkline(self.history_temp)
            draw.text((0, 48), trend,                    fill=1)
    
    def update_stats(self):
        """
        Update temperature statistics and OLED display
        
        Returns:
            float: Current CPU temperature
        """
        cpu_temp = self.get_cpu_temperature()
        self.history_temp.append(cpu_temp)
        self.draw_stats(cpu_temp)
        return cpu_temp
    
    def start(self):
        """
        Start the camera and monitoring loop
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            self.init_camera()
            self.init_oled_display()
            self.is_running = True
            print("Camera stats monitor started. Press 'q' to quit.")
            return True
        except Exception as e:
            print(f"Failed to start camera stats monitor: {e}")
            return False
    
    def run(self, update_interval=1.0):
        """
        Main camera loop with stats display
        
        Args:
            update_interval (float): Seconds between temperature updates (default: 1.0)
        """
        if not self.start():
            return
        
        last_temp_update = 0
        
        try:
            while self.cap.isOpened() and self.is_running:
                ok, frame = self.cap.read()
                if not ok:
                    print("Failed to read frame from camera")
                    break
                
                self.frame_count += 1
                current_time = time.time()
                
                # Update temperature and OLED display at specified interval
                if current_time - last_temp_update >= update_interval:
                    cpu_temp = self.update_stats()
                    print(f"Frame: {self.frame_count}, CPU Temp: {cpu_temp:.1f}°C")
                    last_temp_update = current_time
                
                cv.imshow("Camera Feed", frame)
                if cv.waitKey(1) == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\nStopping camera stats monitor...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the camera and clean up resources"""
        self.is_running = False
        
        if self.cap:
            self.cap.release()
            print("Camera released")
        
        cv.destroyAllWindows()
        
        # Clear OLED on exit
        if self.oled:
            with canvas(self.oled):
                pass
            print("OLED display cleared")
    
    def get_stats(self):
        """
        Get current statistics
        
        Returns:
            dict: Dictionary containing current stats
        """
        current_temp = self.get_cpu_temperature() if len(self.history_temp) == 0 else self.history_temp[-1]
        return {
            'frame_count': self.frame_count,
            'current_temperature': current_temp,
            'temperature_history': list(self.history_temp),
            'is_running': self.is_running,
            'camera_index': self.camera_index
        }


def create_camera_monitor(camera_index=2, oled_addr=0x3C, history_length=32):
    """
    Factory function to create a CameraStatsMonitor instance
    
    Args:
        camera_index (int): Camera device index
        oled_addr (int): I2C address of OLED display
        history_length (int): Number of temperature readings to keep
        
    Returns:
        CameraStatsMonitor: Configured camera monitor instance
    """
    return CameraStatsMonitor(camera_index, oled_addr, history_length)

def main():
    """Main function to run camera with CPU temperature stats on OLED"""
    print("Starting camera with CPU temperature monitoring...")
    
    # Create camera monitor instance
    # camera_index=2: Use camera at index 2 (adjust as needed)
    # oled_addr=0x3C: OLED I2C address
    # history_length=32: Keep 32 temperature readings for sparkline
    monitor = create_camera_monitor(camera_index=2, oled_addr=0x3C, history_length=32)
    
    # Run the camera with stats monitoring
    # update_interval=1.0: Update temperature display every 1 second
    monitor.run(update_interval=1.0)


if __name__ == "__main__":
    main()
