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

# LED functionality removed - focusing on display only

# setup oled connection
serial = i2c(port=1, address=0x3C)  # I2C port 1, typical SSD1306 address
display = ssd1306(serial)

try:
    while(1):
        audrey_loop(display)
except KeyboardInterrupt:
    print("Display stopped")
finally:
    print("Display cleanup complete")