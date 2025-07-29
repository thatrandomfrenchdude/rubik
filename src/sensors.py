#!/usr/bin/env python3
"""
Sensors dashboard – OLED + terminal live view for:
  • MPU-6050 3-axis accelerometer (Ax, Ay, Az)
  • BMP180 ambient temperature & pressure
  • Pressure trend sparkline
"""

# ──────── smbus2 Shim ────────
import sys
import smbus2
sys.modules['smbus'] = smbus2  # satisfy drivers requiring smbus

import time
from collections import deque

# OLED imports
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# Sensor imports
from mpu6050 import mpu6050      # MPU-6050 wrapper
from Adafruit_BMP.BMP085 import BMP085  # Adafruit BMP180 driver

# Terminal imports
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich import box

# ─────────── Config ───────────
OLED_ADDR       = 0x3C
HISTORY_LEN     = 32
history_pressure = deque(maxlen=HISTORY_LEN)

console = Console()

# ───────── Initialization ─────────
def init_oled_display():
    serial = i2c(port=1, address=OLED_ADDR)
    return ssd1306(serial)

def init_sensors():
    accel = mpu6050(0x68)      # MPU-6050 on /dev/i2c-1
    baro  = BMP085(busnum=1)   # BMP180 on /dev/i2c-1
    return accel, baro

# ───────── Helper Functions ─────────
def sparkline(series, width=16, high='#', mid='*', low='.'):
    data = list(series)[-width:]
    if len(data) < width:
        data = [None]*(width-len(data)) + data
    top = max((v for v in data if v is not None), default=0)
    avg = sum((v for v in data if v is not None), 0) / max(1, len([v for v in data if v is not None]))
    chars = []
    for v in data:
        if v is None:
            chars.append(' ')
        elif v >= top:
            chars.append(high)
        elif v >= avg:
            chars.append(mid)
        else:
            chars.append(low)
    return ''.join(chars)

def draw_dashboard(device, ax, ay, az, ambient, pressure):
    with canvas(device) as draw:
        draw.text((0,  0), "Sensors Dashboard",     fill=1)
        draw.text((0, 12), f"Ax:{ax: .2f}g",        fill=1)
        draw.text((64,12), f"Ay:{ay: .2f}g",        fill=1)
        draw.text((0, 24), f"Az:{az: .2f}g",        fill=1)
        draw.text((64,24), f"T:{ambient: .1f}C",    fill=1)
        draw.text((0, 36), f"P:{pressure: .1f}hPa", fill=1)
        draw.text((64,36), "Trend:",                fill=1)
        trend = sparkline(history_pressure)
        draw.text((0, 48), trend,                   fill=1)

def build_table(ax, ay, az, ambient, pressure):
    tbl = Table(title="🌡️ Sensors Live Metrics", box=box.SIMPLE_HEAVY)
    tbl.add_column("Metric", justify="left")
    tbl.add_column("Value", justify="right")
    tbl.add_row("Ax (g)",        f"{ax:.2f}")
    tbl.add_row("Ay (g)",        f"{ay:.2f}")
    tbl.add_row("Az (g)",        f"{az:.2f}")
    tbl.add_row("Temp (°C)",     f"{ambient:.1f}")
    tbl.add_row("Pressure (hPa)",f"{pressure:.1f}")
    tbl.add_row("P Trend",       sparkline(history_pressure))
    return tbl

# ───────── Main Loop ─────────
def run_dashboard():
    oled   = init_oled_display()
    accel, baro = init_sensors()

    with Live(console=console, auto_refresh=False) as live:
        try:
            while True:
                # Read sensors
                adata   = accel.get_accel_data()  # returns dict x,y,z
                ax, ay, az = adata['x'], adata['y'], adata['z']
                ambient  = baro.read_temperature() # °C
                pressure = baro.read_pressure() / 100.0  # Pa→hPa

                # Update history & displays
                history_pressure.append(pressure)
                draw_dashboard(oled, ax, ay, az, ambient, pressure)
                table = build_table(ax, ay, az, ambient, pressure)
                live.update(table, refresh=True)

                time.sleep(1)
        except KeyboardInterrupt:
            # Clear OLED on exit
            with canvas(oled):
                pass

if __name__ == "__main__":
    run_dashboard()
