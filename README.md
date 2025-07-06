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
    screen -S [session name] /dev/tty.[name] 115200
    ```
    Replace `[session name]` and `[device name]` with the name of your session and Rubik Pi device respectively.

## Send a File
0. Activate a terminal session with the Rubik Pi device.
1. On the Rubik Pi, run:
    ```bash
    rz -b -y
    ```
2. In the terminal, run:
    ```bash
    screen -S iot -X exec '!!' sz -b -e path/to/file

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