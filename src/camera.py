#!/usr/bin/env python3
"""
Camera application with CPU temperature monitoring on OLED display
Uses the CameraStatsMonitor module for functionality
"""

from camera_stats_module import CameraStatsMonitor, create_camera_monitor


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