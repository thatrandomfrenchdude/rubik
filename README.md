# Rubik Pi Developer Guide

This is my own personal guide to using the Rubik Pi device for various software projects. This guide assumes you have basic knowledge of terminal commands and Python.<br><br>

**Table of Contents**
- [A Note on My Development Environment](#a-note-on-my-development-environment)
- [Workflows](#workflows)
    - [Prequisites](#prequisites)
    - [Launch a Terminal Session](#launch-a-terminal-session)
    - [Set Up Wifi](#set-up-wifi)
    - [Send a File](#send-a-file)
    - [Check Resource Usage](#check-resource-usage)
    - [Storage](#storage)
    - [Return to Table of Contents](#table-of-contents)
- [Documentation Links](#documentation-links)

## A Note on My Development Environment
I am using either a Macbook Pro or Dell as a host machine to interface with the Rubik Pi device. See the below table for details.

|               | CPU                | RAM      | OS                  |
|---------------|--------------------|----------|----------------------|
| **Macbook Pro**   | M4 Max             | 64GB     | macOS Sequoia  |
| **Dell 7455**     | Snapdragon X Elite | 32GB     | Windows 11           |

## Workflows
Workflows for common tasks using linux commands. Both Windows and Linux commands are available in the [Rubik Pi Documentation](https://www.thundercomm.com/rubik-pi-3/en/docs/rubik-pi-3-user-manual/).

### Prequisites
These workflows assume the following prerequisites are met.

*Rubik Pi*
- The device is connected to the host machine via USB.
- A power supply is connected (can be the host machine).
- `lrzsz` and `vi` installed.

*Host Machine*
- A terminal application on the host machine (I use the built-in VS Code terminal).
- `lrzsz` and `screen` are installed.

### Launch a Host Machine Terminal Session on the Rubik Pi Device
Connect a terminal on the host machine to the Rubik Pi device using `screen`.
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
Configure the wifi connection on the Rubik Pi device.
1. [Launch a Rubik Pi terminal session](#launch-a-host-machine-terminal-session-on-the-rubik-pi-device) on the host machine.
2. use `vi` in the console to edit the wpa_supplicant.conf file:
    ```bash
    vi /etc/wpa_supplicant/wpa_supplicant.conf
    ```
3. Add your network details:
    ```config
    network={
        ssid="your_SSID"
        psk="your_password"
    }
    ```
    Note: press `i` to enter insert mode in `vi` and `Esc` to exit.
4. Save and exit the file by typing `:wq` and pressing `Enter`.
5. Restart the wifi interface:
    ```bash
    ifdown wlan0 && ifup wlan0
    ```

### Send a File from the Host Machine to the Rubik Pi
Send files written on the host machine to the Rubik Pi device using `lrzsz`.
1. [Launch a Rubik Pi terminal session](#launch-a-host-machine-terminal-session-on-the-rubik-pi-device) on the host machine.
2. In the Rubik Pi terminal session, prepare to receive a file by running:
    ```bash
    rz -b -y
    ```
2. On the host machine, in a separate terminal window, send the file using `sz`:
    ```bash
    screen -S session-name -X exec '!!' sz -b -e path/to/file

    # replace `session-name` with your screen session name
    # replace `path/to/file` with the path to the send file

    # Example:
    screen -S rubik-pi -X exec '!!' sz -b -e config.yaml

    # session-name: rubik-pi
    # path/to/file: config.yaml
    ```

### Check Resource Usage
Check the available RAM and storage on the Rubik Pi device.
1. [Launch a Rubik Pi terminal session](#launch-a-host-machine-terminal-session-on-the-rubik-pi-device) on the host machine.
2. In the terminal, run the following commands:
    ```bash
    # Check storage usage
    df -h

    # Check RAM usage
    free -h
    ```

## Documentation Links
- [Rubik Pi Documentation](https://www.thundercomm.com/rubik-pi-3/en/docs/rubik-pi-3-user-manual/)
- [Llama API Documentation](https://llama.developer.meta.com/docs/overview/)
- [GitHub Repo](https://github.com/thatrandomfrenchdude/rubik)
- [Hardware Diagram](https://www.thundercomm.com/rubik-pi-3/en/docs/rubik-pi-3-user-manual/1.0.0-a/peripherals-and-interfaces/)