#!/usr/bin/env python3
"""
Sensors dashboard – displays MPU-6050 and BMP180 readings
on SSD1306 OLED (128×64).

Hardware (I2C bus 1):
  • GY-521 (MPU-6050) at 0x68
  • GY-68 (BMP180)   at 0x77
  • SDA=GPIO 2, SCL=GPIO 3, 3V3=Pin 1, GND=Pin 6

Dependencies: luma.oled, smbus2, mpu6050, Adafruit-BMP
"""

import time
from collections import deque

# OLED imports
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# Sensor imports
from mpu6050 import MPU6050            # MPU-6050 wrapper
from Adafruit_BMP.BMP085 import BMP085  # Adafruit BMP085/BMP180 driver

# ───────────────────────── Configuration ─────────────────────────────
OLED_ADDR    = 0x3C
HISTORY_LEN  = 32

# Rolling history for pressure trend
history_pressure = deque(maxlen=HISTORY_LEN)

# ───────────────────────── Initialization ───────────────────────────
def init_oled_display():
    """Initialize SSD1306 OLED on I2C bus 1."""
    serial = i2c(port=1, address=OLED_ADDR)
    return ssd1306(serial)

def init_sensors():
    """Create sensor instances."""
    accel = MPU6050(0x68)  # GY-521 MPU-6050
    baro  = BMP085()       # GY-68 BMP180 via Adafruit-BMP
    return accel, baro

# ───────────────────────── Helper Functions ─────────────────────────
def sparkline(series, width=16, high='#', mid='*', low='.'):
    """Generate a simple sparkline string for a numeric series."""
    data = list(series)[-width:]
    if len(data) < width:
        data = [None] * (width - len(data)) + data
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
        draw.text((0,  0), "Sensors Dashboard",     fill=1)
        draw.text((0, 12), f"Ax:{ax: .2f}g",       fill=1)
        draw.text((64,12), f"Ay:{ay: .2f}g",       fill=1)
        draw.text((0, 24), f"Az:{az: .2f}g",       fill=1)
        draw.text((64,24), f"P:{pressure: .1f}hPa",fill=1)
        draw.text((0, 36), "P Trend:",             fill=1)
        trend = sparkline(history_pressure, width=16)
        draw.text((0, 48), trend,                  fill=1)

# ───────────────────────── Main Loop ───────────────────────────────
def run_dashboard():
    oled        = init_oled_display()
    accel, baro = init_sensors()
    try:
        while True:
            # Read sensors
            adata = accel.get_accel_data()      # returns dict x, y, z
            ax, ay, az = adata['x'], adata['y'], adata['z']
            pressure   = baro.readPressure() / 100.0  # Pa → hPa via Adafruit-BMP

            # Update history and redraw
            history_pressure.append(pressure)
            draw_dashboard(oled, ax, ay, az, pressure)

            time.sleep(1)  # 1 s update interval
    except KeyboardInterrupt:
        # Clear display on exit
        with canvas(oled):
            pass

if __name__ == "__main__":
    run_dashboard()

# #!/usr/bin/env python3
# """
# Sensors dashboard – displays MPU-6050 and BMP180 readings
# on SSD1306 OLED (128×64).

# Hardware (I2C bus 1):
#   • GY-521 (MPU-6050) at 0x68
#   • GY-68 (BMP180)   at 0x77
#   • SDA=GPIO 2, SCL=GPIO 3, 3V3=Pin 1, GND=Pin 6

# Dependencies: luma.oled, smbus2, mpu6050, bmp180
# """

# import time
# from collections import deque

# # OLED imports
# from luma.core.interface.serial import i2c
# from luma.core.render import canvas
# from luma.oled.device import ssd1306

# # Sensor imports
# from mpu6050 import mpu6050      # MPU-6050 wrapper  [oai_citation:14‡GitHub](https://github.com/m-rtijn/mpu6050?utm_source=chatgpt.com)
# from bmp180 import BMP180        # BMP180 module  [oai_citation:15‡GitHub](https://github.com/m-rtijn/bmp180?utm_source=chatgpt.com)

# # ───────────────────────── Configuration ─────────────────────────────
# OLED_ADDR    = 0x3C
# HISTORY_LEN  = 32

# # Rolling history for pressure trend
# history_pressure = deque(maxlen=HISTORY_LEN)

# # ───────────────────────── Initialization ───────────────────────────
# def init_oled_display():
#     """Initialize SSD1306 OLED on I2C bus 1."""
#     serial = i2c(port=1, address=OLED_ADDR)
#     return ssd1306(serial)

# def init_sensors():
#     """Create sensor instances."""
#     accel = mpu6050(0x68)  # GY-521 MPU-6050  [oai_citation:16‡Instructables](https://www.instructables.com/How-to-Use-the-MPU6050-With-the-Raspberry-Pi-4/?utm_source=chatgpt.com)
#     baro  = BMP180()       # GY-68 BMP180  [oai_citation:17‡The Pi Hut](https://thepihut.com/blogs/raspberry-pi-tutorials/18025084-sensors-pressure-temperature-and-altitude-with-the-bmp180?srsltid=AfmBOoqz4x4YoKqajARik1GBwl4b0jEXmXY1kBursWe4iTnksOYwArKR&utm_source=chatgpt.com)
#     return accel, baro

# # ───────────────────────── Helper Functions ─────────────────────────
# def sparkline(series, width=16, high='#', mid='*', low='.'):
#     """Generate a simple sparkline string for a numeric series."""
#     data = list(series)[-width:]
#     if len(data) < width:
#         data = [None]*(width-len(data)) + data
#     top = max((v for v in data if v is not None), default=0)
#     avg = sum((v for v in data if v is not None), 0) / max(1, len([v for v in data if v is not None]))
#     chars = []
#     for v in data:
#         if v is None:
#             chars.append(' ')
#         elif v >= top:
#             chars.append(high)
#         elif v >= avg:
#             chars.append(mid)
#         else:
#             chars.append(low)
#     return ''.join(chars)

# def draw_dashboard(device, ax, ay, az, pressure):
#     """Render accelerometer and pressure data on the OLED."""
#     with canvas(device) as draw:
#         draw.text((0,  0), "Sensors Dashboard", fill=1)
#         draw.text((0, 12), f"Ax:{ax: .2f}g",      fill=1)
#         draw.text((64,12), f"Ay:{ay: .2f}g",      fill=1)
#         draw.text((0, 24), f"Az:{az: .2f}g",      fill=1)
#         draw.text((64,24), f"P:{pressure: .1f}hPa",fill=1)
#         draw.text((0, 36), "P Trend:",            fill=1)
#         trend = sparkline(history_pressure, width=16)
#         draw.text((0, 48), trend,                 fill=1)

# # ───────────────────────── Main Loop ───────────────────────────────
# def run_dashboard():
#     oled  = init_oled_display()
#     accel, baro = init_sensors()
#     try:
#         while True:
#             # Read sensors
#             adata    = accel.get_accel_data()   # returns dict x, y, z
#             ax, ay, az = adata['x'], adata['y'], adata['z']
#             pressure = baro.read_pressure()/100.0  # Pa→hPa

#             # Update history and redraw
#             history_pressure.append(pressure)
#             draw_dashboard(oled, ax, ay, az, pressure)

#             time.sleep(1)  # 1 s update interval
#     except KeyboardInterrupt:
#         # Clear display on exit
#         with canvas(oled) as draw:
#             pass

# if __name__ == "__main__":
#     run_dashboard()