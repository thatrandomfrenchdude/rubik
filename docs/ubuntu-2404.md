# Ubuntu 24.04 Workflows

This document provides workflows for common tasks on the Rubik Pi device running Ubuntu 24.04.

**Table of Contents**
- [Prerequisites](#prerequisites)
- [Flashing the Rubik Pi Device with Ubuntu 24.04](#flashing-the-rubik-pi-device-with-ubuntu-2404)

## Prerequisites
These workflows assume the below prerequisites are met on the Rubik Pi device and host machine.

- A host machine running Windows, macOS, or Linux.
- A Rubik Pi device
- A USB keyboard and mouse
- An HDMI monitor and cable

## Flashing the Rubik Pi Device with Ubuntu 24.04
1. Clone the [QDL](https://github.com/linux-msm/qdl) flashing tool from GitHub.
2. Follow the [QDL instructions](https://github.com/linux-msm/qdl/blob/master/README.md) for your host machine OS to build the tool from source.
3. Download the Ubuntu 24.04 image for the Rubik Pi device from the [Thundercomm website](https://www.thundercomm.com/rubik-pi-3/en/docs/rubik-pi-3-user-manual/1.1.2/get-started#download-images).
4. In a terminal, navigate to the `ufs` directory of the FlatBuild folder containing the Ubuntu 24.04 image.
5. Put the Rubik Pi device into EDL mode by following [these instructions](https://www.thundercomm.com/rubik-pi-3/en/docs/rubik-pi-3-user-manual/1.1.2/get-started#flash-images). You can do it manually or using adb.
6. Flash the device using the instructions for your operating system in the [flashing instructions](https://www.thundercomm.com/rubik-pi-3/en/docs/rubik-pi-3-user-manual/1.1.2/get-started#flash-images).

    If you use MacOS like me, follow these steps:
    
    From within the `ufs` directory, run the following command to flash the device:
    ```bash
    ./path/to/qdl --storage ufs prog_firehose_ddr.elf rawprogram*.xml patch*.xml
    ```
    NOTE: This command uses relative paths. You should be in the `ufs` directory of the FlatBuild folder when running it and modify the qdl path accordingly.
7. Once the flashing process is complete, reboot the Rubik Pi device. It may take some time to boot up for the first time.

NOTE: When flashing the Rubik Pi device from Qualcomm Linux to Ubuntu 24.04 the first time, you may have some issues with the build (ex: the `/etc/apt/sources.list` file may not be populated). If this happens, reflash the build again and it should work.