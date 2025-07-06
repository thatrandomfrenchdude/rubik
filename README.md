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