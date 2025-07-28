from periphery import GPIO
import time

out_gpio = GPIO(559, "out")
in_gpio = GPIO(560, "in")

try:
    while True:
        try:
            out_gpio.write(True)
            pin_level = in_gpio.read()
            print(f"in_gpio level: {pin_level}")

            out_gpio.write(False)
            pin_level = in_gpio.read()
            print(f"in_gpio level: {pin_level}")

            time.sleep(1)

        except KeyboardInterrupt:
            out_gpio.write(False)
            break

except IOError:
    print("Error")

finally:
    out_gpio.close()
    in_gpio.close()