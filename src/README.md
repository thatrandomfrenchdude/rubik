# Rubik Pi Source Code Documentation

This directory contains Python scripts for the Rubik Pi device, featuring OLED display applications, sensor monitoring, and AI chatbot functionality.

## Table of Contents
- [Scripts Overview](#scripts-overview)
- [Hardware Requirements](#hardware-requirements)
- [Software Dependencies](#software-dependencies)
- [Setup Instructions](#setup-instructions)
- [Script Details](#script-details)
  - [audrey_display.py](#audrey_displaypy)
  - [oled_chatbot.py](#oled_chatbotpy)
  - [oled_dashboard.py](#oled_dashboardpy)
  - [sensors.py](#sensorspy)
- [Troubleshooting](#troubleshooting)

## Scripts Overview

| Script | Purpose | Hardware Required |
|--------|---------|-------------------|
| `audrey_display.py` | Animated text display demo | SSD1306 OLED |
| `oled_chatbot.py` | AI chatbot with OLED output | SSD1306 OLED, Internet |
| `oled_dashboard.py` | System metrics dashboard | SSD1306 OLED |
| `sensors.py` | MPU-6050 & BMP180 sensor monitoring | SSD1306 OLED, MPU-6050, BMP180 |

## Hardware Requirements

### Core Components
- **Rubik Pi device** with GPIO pins
- **SSD1306 OLED Display (128x64)** - I2C interface

### OLED Display Wiring (Required for all scripts)
- **SDA** → GPIO 2 (Pin 3) - I2C1 Data
- **SCL** → GPIO 3 (Pin 5) - I2C1 Clock  
- **VCC** → 3.3V (Pin 1) - Power
- **GND** → Ground (Pin 6) - Ground
- **I2C Address**: 0x3C (default for SSD1306)

### Additional Sensors (for sensors.py)
- **MPU-6050 (GY-521)** - 6-axis accelerometer/gyroscope
  - I2C Address: 0x68
  - Same I2C bus as OLED (pins 3 & 5)
- **BMP180 (GY-68)** - Barometric pressure sensor
  - I2C Address: 0x77
  - Same I2C bus as OLED (pins 3 & 5)

### Network Requirements (for oled_chatbot.py)
- WiFi connection for Llama API access
- Valid Llama API key in `config.yaml`

## Software Dependencies

Install all dependencies from the project root:

```bash
pip install -r requirements.txt
```

### Core Dependencies
- `luma.oled==3.14.0` - OLED display library
- `python-periphery==2.4.1` - GPIO control library
- `psutil==7.0.0` - System metrics library
- `ping3==4.0.8` - Network ping functionality
- `rich==14.0.0` - Terminal formatting
- `PyYAML==6.0.2` - YAML configuration parsing

### AI Chatbot Dependencies
- `openai==1.93.0` - Llama API client

### Sensor Dependencies (for sensors.py)
- `smbus2` - I2C bus communication
- `mpu6050-raspberrypi` - MPU-6050 wrapper library
- `Adafruit-BMP` - BMP180 pressure sensor library

## Setup Instructions

1. **Hardware Setup**
   - Connect the SSD1306 OLED display to I2C1 pins (3 & 5)
   - For sensors.py: Connect MPU-6050 and BMP180 to the same I2C bus
   - Ensure proper power (3.3V) and ground connections

2. **Software Setup**
   ```bash
   # Create virtual environment
   python3 -m venv rubik-env
   source rubik-env/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configuration (for oled_chatbot.py)**
   - Ensure `config.yaml` exists in the project root with your Llama API key
   - Configure WiFi on Rubik Pi for internet access

4. **I2C Setup**
   - Verify I2C is enabled on Rubik Pi
   - Check device detection: `i2cdetect -y 1`
   - Expected addresses: 0x3C (OLED), 0x68 (MPU-6050), 0x77 (BMP180)

## Script Details

### audrey_display.py

**Description**: Animated text display that scrolls "audrey!" across the OLED screen in a column format.

**Purpose**: Simple OLED demo and hardware testing.

**Requirements**:
- SSD1306 OLED display on I2C1
- `luma.oled`, `python-periphery`

**Usage**:
```bash
python audrey_display.py
```

**Features**:
- Continuous animation loop
- Character-by-character scrolling effect
- Clean display shutdown on interrupt

**Controls**:
- Press `Ctrl+C` to stop

---

### oled_chatbot.py

**Description**: AI-powered chatbot that displays conversations on the OLED screen with streaming text effects and auto-scrolling.

**Purpose**: Interactive AI assistant with visual feedback on OLED display.

**Requirements**:
- SSD1306 OLED display on I2C1
- Internet connection (WiFi)
- Valid Llama API key in `config.yaml`
- `luma.oled`, `openai`, `pyyaml`

**Setup**:
1. Configure WiFi on Rubik Pi
2. Ensure `config.yaml` contains valid Llama API key:
   ```yaml
   LLAMA_API_KEY: "your-api-key-here"
   ```

**Usage**:
```bash
# With OLED display (default)
python oled_chatbot.py

# Terminal-only mode
python oled_chatbot.py --no-display
```

**Features**:
- Streaming text animation with reading pace
- Star Wars-style scrolling for long conversations
- Markdown text cleaning and formatting
- Auto-scrolling display buffer
- Chat history management (20 messages)
- Terminal and OLED output

**Controls**:
- Type messages in terminal
- `exit` - Quit the chatbot
- `clear` - Clear display and conversation
- `Ctrl+C` - Emergency stop

---

### oled_dashboard.py

**Description**: Real-time system monitoring dashboard displaying CPU temperature, load, RAM usage, and network ping on OLED or terminal.

**Purpose**: Live IoT device monitoring with visual metrics.

**Requirements**:
- SSD1306 OLED display on I2C1 (OLED mode)
- Network connection for ping tests
- `luma.oled`, `psutil`, `ping3`, `rich`
- Optional: `gpiozero` for LED alerts

**Usage**:
```bash
# OLED display mode (default)
python oled_dashboard.py

# To use terminal mode, edit USE_OLED_DISPLAY = False in script
```

**Features**:
- Real-time metrics: CPU temp, CPU load, RAM usage, ping latency
- Temperature trend sparkline visualization
- High temperature alerts (>65°C)
- LED indicator support (if available)
- 2-second update interval for OLED, 1-second for terminal
- Graceful error handling for missing hardware

**Metrics Displayed**:
- **CPU Temperature**: System thermal reading
- **CPU Load**: Current processor utilization
- **RAM Usage**: Memory consumption percentage
- **Ping**: Network latency to 8.8.8.8
- **Temperature Trend**: Visual history sparkline

**Controls**:
- Press `Ctrl+C` to stop monitoring

---

### sensors.py

**Description**: Advanced sensor monitoring dashboard displaying MPU-6050 accelerometer and BMP180 pressure readings with trend visualization.

**Purpose**: Real-time sensor data monitoring for motion detection and environmental sensing.

**Requirements**:
- SSD1306 OLED display on I2C1 (0x3C)
- MPU-6050 accelerometer/gyroscope (0x68)
- BMP180 barometric pressure sensor (0x77)
- All sensors on same I2C bus
- `luma.oled`, `smbus2`, `mpu6050-raspberrypi`, `Adafruit-BMP`

**Hardware Setup**:
```
All devices on I2C Bus 1:
├── SSD1306 OLED (0x3C)
├── MPU-6050 (0x68) 
└── BMP180 (0x77)

Connections:
- SDA → GPIO 2 (Pin 3)
- SCL → GPIO 3 (Pin 5)  
- VCC → 3.3V (Pin 1)
- GND → Ground (Pin 6)
```

**Usage**:
```bash
python sensors.py
```

**Features**:
- Real-time accelerometer readings (X, Y, Z axes in g-force)
- Barometric pressure monitoring (hPa)
- Pressure trend sparkline (32-point history)
- 1-second update rate
- Clean display shutdown

**Sensor Data**:
- **Ax, Ay, Az**: 3-axis acceleration in g-force units
- **Pressure**: Atmospheric pressure in hectopascals (hPa)
- **Pressure Trend**: Visual sparkline showing pressure changes

**Controls**:
- Press `Ctrl+C` to stop monitoring

---

## Troubleshooting

### I2C Issues
```bash
# Check I2C devices
i2cdetect -y -r 1

# Expected addresses:
# 0x3C - SSD1306 OLED
# 0x68 - MPU-6050  
# 0x77 - BMP180
```

### Display Problems
- Verify wiring: SDA→Pin3, SCL→Pin5, VCC→Pin1, GND→Pin6
- Check I2C address (usually 0x3C for SSD1306)
- Ensure adequate power supply (3.3V)

### Sensor Issues (sensors.py)
- Install sensor libraries: `pip install smbus2 mpu6050-raspberrypi Adafruit-BMP`
- Verify I2C addresses: MPU-6050 (0x68), BMP180 (0x77)
- Check sensor wiring and power connections

### Chatbot Issues (oled_chatbot.py)
- Verify WiFi connection: `ping google.com`
- Check API key in `config.yaml`
- Ensure internet access for Llama API

### Permission Issues
```bash
# Add user to i2c group (if needed)
sudo usermod -a -G i2c $USER
# Logout and login again
```