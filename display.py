from periphery import GPIO
import time
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# resources
# https://www.donskytech.com/micropython-interfacing-with-ssd1306-oled-display/
# https://www.digikey.com/en/maker/projects/micropython-basics-load-files-run-code/fb1fcedaf11e4547943abfdd8ad825ce

BOOT_ATTEMPTS = 0
WIFI_ATTEMPTS = 0
# Rubik Pi pin layout: pin 3 = SDA (I2C1), pin 5 = SCL (I2C1)
# Using I2C1 for display communication (pins 3 and 5)

def toggle(gpio_pin) -> None:
    current_value = gpio_pin.read()
    gpio_pin.write(not current_value)

def clear(d) -> None:
    with canvas(d) as draw:
        pass  # Drawing nothing clears the display

def drawMicropythonLogo(d) -> None:
    with canvas(d) as draw:
        # Draw filled rectangle
        draw.rectangle((0, 0, 31, 31), fill=1)
        draw.rectangle((2, 2, 29, 29), fill=0)
        # Draw vertical lines
        for y in range(8, 30):
            draw.point((9, y), fill=1)
            draw.point((16, y), fill=1)
            draw.point((23, y), fill=1)
        for y in range(2, 24):
            draw.point((16, y), fill=1)
        # Draw small rectangle
        draw.rectangle((26, 24, 27, 27), fill=1)
        # Draw text
        draw.text((40, 0), 'MicroPython', fill=1)
        draw.text((40, 12), 'SSD1306', fill=1)
        draw.text((40, 24), 'OLED 128x64', fill=1)

def race_loop(d) -> None:
    count = 0
    while count < 32:
        with canvas(d) as draw:
            draw.text((4*count, 0), 'a', fill=1)
            draw.text((4*count, 16), 'b', fill=1)
            draw.text((4*count, 32), 'c', fill=1)
            draw.text((4*count, 48), 'd', fill=1)
        time.sleep(0.01)
        count += 1
    clear(d)

def audrey_loop(d) -> None:
    count = 0
    while count < 32:
        with canvas(d) as draw:
            draw.text((4*count, 0), 'a', fill=1)
            draw.text((4*count, 8), 'u', fill=1)
            draw.text((4*count, 16), 'd', fill=1)
            draw.text((4*count, 24), 'r', fill=1)
            draw.text((4*count, 32), 'e', fill=1)
            draw.text((4*count, 40), 'y', fill=1)
            draw.text((4*count, 48), '!', fill=1)
        time.sleep(0.01)
        count += 1
    clear(d)

# connect to wifi
# try to connect
    # if yes, flash twice for 0.5s and move on
    # if no, flash once and wait 1s to retry
        # after 10 tries, run a flashing loop

# LED functionality removed - focusing on display only

# setup oled connection
serial = i2c(port=1, address=0x3C)  # I2C port 1, typical SSD1306 address
display = ssd1306(serial)

# print message
# display.text('SSD1306 OLED', 0, 0) # x=0, y=0 (row 0)
# display.text('with', 0, 16) # x=0, y=16 (row 1)
# display.text('Micropython', 0, 32) # x=0, y=32 (row 2)
# display.text('abcdefghijklmnop', 0, 48) # x=0, y=48 (row 3)
# display.show() # x=4 pixels wide, y=16 pixels tall

try:
    while(1):
        audrey_loop(display)
except KeyboardInterrupt:
    print("Display stopped")
finally:
    print("Display cleanup complete")