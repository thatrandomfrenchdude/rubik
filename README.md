# Rubik Pi Quick Guide

I am using an M4 Macbook Pro to interface with the Rubik Pi device.<br><br>
This guide assumes you have basic knowledge of terminal commands and Python.

**Table of Contents**
- [Launch a Terminal Session](#launch-a-terminal-session)
- [Send a File](#send-a-file)
- [Check Resource Usage](#check-resource-usage)
- [Documentation Links](#documentation-links)

## Launch a Terminal Session
1. In a terminal, run:
    ```bash
    screen -S session-name /dev/tty.device-name 115200
    ```
    Replace `session-name` and `device-name` with a name for your screen session and Rubik Pi device respectively.

    For example, if your Rubik Pi device is connected as `/dev/tty.usbserial-123456` and you want to name your session `rubik-pi`, run:
    ```bash
    screen -S rubik-pi /dev/tty.usbserial-123456 115200
    ```

2. Log in to the Rubik Pi device using your username and password.
    Default credentials are:
    - Username: `root`
    - Password: `rubikpi`

## Set Up Wifi
1. use `vi` in the console to edit the wpa_supplicant.conf file:
    ```bash
    vi /etc/wpa_supplicant/wpa_supplicant.conf
    ```
2. Add your network details:
    ```config
    network={
        ssid="your_SSID"
        psk="your_password"
    }
    ```
    Note: press `i` to enter insert mode in `vi` and `Esc` to exit. 
3. Save and exit the file by typing `:wq` and pressing `Enter`.
4. Restart the wifi interface:
    ```bash
    ifdown wlan0 && ifup wlan0
    ```

## Send a File
0. Activate a terminal session with the Rubik Pi device.
1. On the Rubik Pi, run:
    ```bash
    rz -b -y
    ```
2. In the terminal, run:
    ```bash
    screen -S session-name -X exec '!!' sz -b -e path/to/file
    ```
    Replace `session-name` and `path/to/file` with the screen session name and path to the file you want to send respectively.

    For example, to send `config.yaml` and assuming your screen session is named `rubik-pi`, run:
    ```bash
    screen -S rubik-pi -X exec '!!' sz -b -e config.yaml
    ```

## Check Resource Usage
### Storage
In a terminal, run:
```bash
df -h
```

### RAM
In a terminal, run:
```bash
free -h
```

## Documentation Links
- [Rubik Pi Documentation](https://www.thundercomm.com/rubik-pi-3/en/docs/rubik-pi-3-user-manual/)
- [Llama API Documentation](https://llama.developer.meta.com/docs/overview/)
- [GitHub Repo](https://github.com/thatrandomfrenchdude/rubik)
- [Hardware Diagram](https://www.thundercomm.com/rubik-pi-3/en/docs/rubik-pi-3-user-manual/1.0.0-a/peripherals-and-interfaces/)