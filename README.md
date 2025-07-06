# Rubik Pi Guide

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