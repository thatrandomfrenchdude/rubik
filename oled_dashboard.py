#!/usr/bin/env python3
"""
OLED IoT dashboard – combining iot_dashboard.py metrics with display.py OLED output.

Displays live system metrics on SSD1306 OLED display:
  • CPU temperature, CPU load, RAM usage
  • Ping latency to 8.8.8.8
  • Temperature trend visualization

Hardware requirements:
  • Rubik Pi with SSD1306 OLED display on I2C1 (pins 3 & 5)
  • Power: pin 1 (3V3), Ground: pin 9

Dependencies: luma.oled, psutil, ping3
"""

import time
import statistics
import warnings
from collections import deque

# Import OLED display functionality from display.py
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# Import IoT dashboard functionality from iot_dashboard.py
import psutil
from ping3 import ping

# ───────────────────────── Configuration ────────────────────────────────────
HOST = "8.8.8.8"
HISTORY = 20  # Reduced for OLED display space
ALERT_TEMP = 65.0  # °C

# OLED Display setup (from display.py)
serial = i2c(port=1, address=0x3C)  # I2C port 1, typical SSD1306 address
display = ssd1306(serial)

# Metrics history
history = deque(maxlen=HISTORY)

# ────────────────────────── Helper Functions ──────────────────────────────────
def read_cpu_temp() -> float | None:
    """Return CPU temperature in °C, or None if unavailable."""
    # psutil fallback (works on most Linux systems with /sys/class/thermal)
    for temps in psutil.sensors_temperatures().values():
        for entry in temps:
            if "cpu" in (entry.label or "").lower() or entry.label == "":
                return entry.current
    return None

def sparkline_mini(series, width=16):
    """Create a mini sparkline for OLED display using simple characters."""
    blocks = []
    if not series or len(series) == 0:
        return " " * width
    
    # Take last 'width' items and normalize
    recent = list(series)[-width:]
    if len(recent) < width:
        recent = [None] * (width - len(recent)) + recent
    
    for t in recent:
        if t is None:
            blocks.append(" ")
        elif t >= ALERT_TEMP:
            blocks.append("#")  # Hot
        elif t >= 50:
            blocks.append("*")  # Warm
        else:
            blocks.append(".")  # Cool
    return "".join(blocks)

def safe_ping(host: str, **kwargs):
    """Call ping3.ping() safely across different versions."""
    try:
        return ping(host, privileged=False, unit="ms", timeout=1, **kwargs)
    except TypeError:
        return ping(host, unit="ms", timeout=1, **kwargs)
    except Exception:
        return None

def format_temp(temp):
    """Format temperature for display."""
    if temp is None:
        return "N/A"
    return f"{temp:.1f}C"

def format_percentage(value):
    """Format percentage for display."""
    return f"{value:.1f}%"

def format_ping(rtt):
    """Format ping time for display."""
    if rtt is None:
        return "N/A"
    return f"{rtt:.0f}ms"

def draw_dashboard(d, temp, cpu, mem, rtt):
    """Draw the IoT dashboard on the OLED display."""
    with canvas(d) as draw:
        # Title
        draw.text((0, 0), "IoT Dashboard", fill=1)
        
        # Metrics - arranged in 4 lines after title
        draw.text((0, 12), f"CPU: {format_temp(temp)}", fill=1)
        draw.text((64, 12), f"Load: {format_percentage(cpu)}", fill=1)
        
        draw.text((0, 24), f"RAM: {format_percentage(mem)}", fill=1)
        draw.text((64, 24), f"Ping: {format_ping(rtt)}", fill=1)
        
        # Temperature trend line
        draw.text((0, 36), "Temp trend:", fill=1)
        trend = sparkline_mini(history, 16)
        draw.text((0, 48), trend, fill=1)
        
        # Alert indicator if temperature is high
        if temp and temp >= ALERT_TEMP:
            draw.text((90, 48), "HOT!", fill=1)

def clear_display(d):
    """Clear the OLED display."""
    with canvas(d) as draw:
        pass  # Drawing nothing clears the display

# ──────────────────────────── Main Dashboard Loop ──────────────────────────────
def run_dashboard():
    """Main dashboard loop."""
    print("Starting OLED IoT Dashboard...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Collect metrics (from iot_dashboard.py logic)
            temp = read_cpu_temp()
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            rtt = safe_ping(HOST)
            
            # Update history
            history.append(temp)
            
            # Draw on OLED display
            draw_dashboard(display, temp, cpu, mem, rtt)
            
            # Console output for debugging (optional)
            status = f"Temp: {format_temp(temp)}, CPU: {format_percentage(cpu)}, RAM: {format_percentage(mem)}, Ping: {format_ping(rtt)}"
            print(f"\r{status}", end="", flush=True)
            
            time.sleep(2)  # Update every 2 seconds
            
    except KeyboardInterrupt:
        print("\nStopping dashboard...")
        clear_display(display)
        print("Dashboard stopped")
    except Exception as e:
        print(f"\nError: {e}")
        clear_display(display)
    finally:
        print("Display cleanup complete")

if __name__ == "__main__":
    run_dashboard()
