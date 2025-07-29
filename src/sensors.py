#!/usr/bin/env python3
"""
Sensors dashboard – displays MPU-6050 and BMP180 readings
on SSD1306 OLED (128×64).

Hardware (I2C bus 1):
  • GY-521 (MPU-6050) at 0x68
  • GY-68 (BMP180)   at 0x77
  • SDA=GPIO 2, SCL=GPIO 3, 3V3=Pin 1, GND=Pin 6

Dependencies: luma.oled, smbus2, mpu6050-raspberrypi, Adafruit-BMP
"""

# ──────── Shim smbus → smbus2 ────────
import sys
import smbus2
sys.modules['smbus'] = smbus2

import time
from collections import deque

# OLED imports
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# Sensor imports
from mpu6050 import mpu6050            # MPU-6050 wrapper
from Adafruit_BMP.BMP085 import BMP085  # Adafruit BMP085/BMP180 driver

# ───────────── Configuration ─────────────
OLED_ADDR   = 0x3C
HISTORY_LEN = 32
history_pressure = deque(maxlen=HISTORY_LEN)

def init_oled_display():
    """Initialize SSD1306 OLED on I2C bus 1."""
    serial = i2c(port=1, address=OLED_ADDR)
    return ssd1306(serial)

def init_sensors():
    """Create sensor instances on I2C bus 1."""
    accel = mpu6050(0x68, bus=1)
    baro  = BMP085(busnum=1)
    return accel, baro

# ───────────────────────── Helper Functions ─────────────────────────
def sparkline(series, width=16, high='#', mid='*', low='.'):
    """Generate a simple sparkline string for a numeric series."""
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

def draw_dashboard(device, ax, ay, az, pressure):
    """Render accelerometer and pressure data on the OLED."""
    with canvas(device) as draw:
        draw.text((0,  0), "Sensors Dashboard", fill=1)
        draw.text((0, 12), f"Ax:{ax: .2f}g",      fill=1)
        draw.text((64,12), f"Ay:{ay: .2f}g",      fill=1)
        draw.text((0, 24), f"Az:{az: .2f}g",      fill=1)
        draw.text((64,24), f"P:{pressure: .1f}hPa",fill=1)
        draw.text((0, 36), "P Trend:",            fill=1)
        trend = sparkline(history_pressure, width=16)
        draw.text((0, 48), trend,                 fill=1)

def run_dashboard():
    oled        = init_oled_display()
    accel, baro = init_sensors()
    try:
        while True:
            adata      = accel.get_accel_data()
            ax, ay, az = adata['x'], adata['y'], adata['z']
            pressure   = baro.read_pressure() / 100.0

            history_pressure.append(pressure)
            draw_dashboard(oled, ax, ay, az, pressure)
            time.sleep(1)
    except KeyboardInterrupt:
        with canvas(oled):
            pass

if __name__ == "__main__":
    run_dashboard()
