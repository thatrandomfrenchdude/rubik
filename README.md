# Rubik Pi Developer Guide

This is my own personal guide to using the Rubik Pi device for various software projects. This guide assumes you have basic knowledge of terminal commands and Python.<br><br>

**Table of Contents**
- [A Note on My Development Environment](#a-note-on-my-development-environment)
- [Workflows](#workflows)
- [Documentation Links](#documentation-links)

## A Note on My Development Environment
I am using either a Macbook Pro or Dell as a host machine to interface with the Rubik Pi device. See the below table for details.

|               | CPU                | RAM      | OS                  |
|---------------|--------------------|----------|----------------------|
| **Macbook Pro**   | M4 Max             | 64GB     | macOS Sequoia  |
| **Dell 7455**     | Snapdragon X Elite | 32GB     | Windows 11           |

## Workflows
Workflows for common tasks. Below documentation contains linux commands. Windows and Linux commands are available in the [Rubik Pi Documentation](https://www.thundercomm.com/rubik-pi-3/en/docs/rubik-pi-3-user-manual/)

**Workflow Lookup Table:**
- [Launch a Terminal Session](#launch-a-terminal-session)
- [Set Up Wifi](#set-up-wifi)
- [Send a File](#send-a-file)
- [Check Resource Usage](#check-resource-usage)
- [Storage](#storage)
- [Return to Table of Contents](#table-of-contents)

### Launch a Host Machine Terminal Session on the Rubik Pi Device
Connect a terminal on the host machine to the Rubik Pi device using `screen`.

Prerequisites:
- `screen` installed on the host machine. On macOS, it is pre-installed.
- `lrzsz` installed on the Rubik Pi device. If not installed, install it using:
    ```bash
    opkg update
    opkg install lrzsz
    ```

1. Connect the Rubik Pi device to your host machine via USB.
2. Connect the power supply to the Rubik Pi device (can be the host machine).
3. In a terminal window, run:
    ```bash
    screen -S session-name /dev/tty.device-name 115200
    ```
    Replace `session-name` and `device-name` with a name for your screen session and Rubik Pi device respectively.

    For example, if your Rubik Pi device is connected as `/dev/tty.usbserial-123456` and you want to name your session `rubik-pi`, run:
    ```bash
    screen -S rubik-pi /dev/tty.usbserial-123456 115200
    ```
4. Log in to the Rubik Pi device using your username and password.
    Default credentials are:
    - Username: `root`
    - Password: `rubikpi`

### Set Up Wifi
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

### Send a File from the Host Machine to the Rubik Pi
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

### Check Resource Usage
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