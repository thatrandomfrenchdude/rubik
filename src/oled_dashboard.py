#!/usr/bin/env python3
"""
Unified IoT dashboard – displays on OLED or terminal with rich formatting.

Displays live system metrics on SSD1306 OLED display or terminal:
  • CPU temperature, CPU load, RAM usage
  • Ping latency to 8.8.8.8
  • Temperature trend visualization
  • Optional LED alert on high temperature

Hardware requirements (OLED mode):
  • Rubik Pi with SSD1306 OLED display on I2C1 (pins 3 & 5)
  • Power: pin 1 (3V3), Ground: pin 9

Dependencies: luma.oled, psutil, ping3, rich, gpiozero
"""

import time
import statistics
import warnings
from collections import deque

# Import OLED display functionality
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# Import terminal dashboard functionality
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich import box

# Import IoT dashboard functionality
import psutil
from ping3 import ping

# ───────────────────────── GPIO / LED Support ────────────────────────────────
# Many boards (or containers) don't have native GPIO.  We detect that situation
# and fall back to a "mock" pin factory – no scary warnings, no crash.
try:
    # Suppress gpiozero's pin-factory warnings **before** importing it
    warnings.filterwarnings("ignore", category=UserWarning, module="gpiozero")
    from gpiozero import Device, LED, CPUTemperature
    from gpiozero.pins.mock import MockFactory

    try:                       # real hardware?
        cpu_sensor = CPUTemperature()
        led = LED("LED")       # Pi's on-board ACT LED
    except Exception:          # not a Pi – swap to mock pins
        Device.pin_factory = MockFactory()
        cpu_sensor = None      # psutil fallback handles temp
        led = LED(17)          # mock LED (does nothing)
    led_available = True
except ImportError:            # gpiozero not installed
    cpu_sensor = None
    led_available = False

# ───────────────────────── Configuration ────────────────────────────────────
HOST = "8.8.8.8"
HISTORY = 30  # Full history for terminal, reduced for OLED
ALERT_TEMP = 65.0  # °C

# Setup
console = Console()
history = deque(maxlen=HISTORY)

# OLED Display setup (only initialize if needed)
def init_oled_display():
    """Initialize OLED display when needed."""
    serial = i2c(port=1, address=0x3C)  # I2C port 1, typical SSD1306 address
    return ssd1306(serial)

# ────────────────────────── Helper Functions ──────────────────────────────────
def read_cpu_temp() -> float | None:
    """Return CPU temperature in °C, or None if unavailable."""
    if cpu_sensor:
        return cpu_sensor.temperature
    # psutil fallback (works on most Linux systems with /sys/class/thermal)
    for temps in psutil.sensors_temperatures().values():
        for entry in temps:
            if "cpu" in (entry.label or "").lower() or entry.label == "":
                return entry.current
    return None

def sparkline(series):
    """Unicode temperature trend for terminal display."""
    blocks = []
    for t in series:
        if t is None:
            blocks.append(" ")
        elif t >= ALERT_TEMP:
            blocks.append("⣿")
        else:
            blocks.append("⡆")
    return "".join(blocks)

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

def build_table(temp, cpu, mem, rtt):
    """Build rich table for terminal display."""
    tbl = Table(title="🛰️  IoT Board Live Metrics", box=box.SIMPLE_HEAVY)
    add = tbl.add_row
    add("CPU Temp (°C)", f"{temp:.1f}" if temp else "N/A")
    add("CPU Load (%)", f"{cpu:.1f}")
    add("RAM Used (%)", f"{mem:.1f}")
    add(f"Ping {HOST} (ms)", f"{rtt:.1f}" if rtt else "N/A")
    add("Temp Trend", sparkline(history))
    return tbl

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
def run_dashboard(use_oled_display=True):
    """Main dashboard loop with display choice."""
    if use_oled_display:
        print("Starting OLED IoT Dashboard...")
        display = init_oled_display()
    else:
        print("Starting Terminal IoT Dashboard...")
    
    print("Press Ctrl+C to stop")
    
    try:
        if use_oled_display:
            # OLED display mode
            while True:
                # Collect metrics
                temp = read_cpu_temp()
                cpu = psutil.cpu_percent(interval=None)
                mem = psutil.virtual_memory().percent
                rtt = safe_ping(HOST)
                
                # Update history
                history.append(temp)
                
                # Draw on OLED display
                draw_dashboard(display, temp, cpu, mem, rtt)
                
                # LED alert if available
                if led_available:
                    (led.on() if temp and temp >= ALERT_TEMP else led.off())
                
                # Console output for debugging (optional)
                status = f"Temp: {format_temp(temp)}, CPU: {format_percentage(cpu)}, RAM: {format_percentage(mem)}, Ping: {format_ping(rtt)}"
                print(f"\r{status}", end="", flush=True)
                
                time.sleep(2)  # Update every 2 seconds
        else:
            # Terminal display mode with rich formatting
            with Live(console=console, auto_refresh=False) as live:
                while True:
                    temp = read_cpu_temp()
                    cpu = psutil.cpu_percent(interval=None)
                    mem = psutil.virtual_memory().percent
                    rtt = safe_ping(HOST)

                    history.append(temp)
                    live.update(Panel(build_table(temp, cpu, mem, rtt), border_style="cyan"),
                                refresh=True)

                    if led_available:
                        (led.on() if temp and temp >= ALERT_TEMP else led.off())

                    time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping dashboard...")
        if led_available:
            led.off()
        if use_oled_display:
            clear_display(display)
        print("Dashboard stopped")
    except Exception as e:
        print(f"\nError: {e}")
        if led_available:
            led.off()
        if use_oled_display:
            clear_display(display)
    finally:
        if use_oled_display:
            print("Display cleanup complete")
        print("[bold green]Bye![/bold green]")

if __name__ == "__main__":
    # Default to OLED display, set to False for terminal display
    USE_OLED_DISPLAY = True
    run_dashboard(use_oled_display=USE_OLED_DISPLAY)
