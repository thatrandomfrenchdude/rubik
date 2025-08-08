# Camera Stats Module

This module provides camera capture functionality with real-time CPU temperature monitoring displayed on an OLED screen.

## Features

- **Camera Capture**: OpenCV-based video capture from configurable camera index
- **CPU Temperature Monitoring**: Reads CPU temperature from system thermal zones
- **OLED Display**: Shows real-time stats on SSD1306 OLED display
- **Temperature History**: Maintains temperature history with sparkline visualization
- **Modular Design**: Easy to integrate into other projects

## Files

- `camera_stats_module.py` - Main module with CameraStatsMonitor class
- `camera.py` - Simple application using the module
- `camera_examples.py` - Usage examples and demonstrations

## Usage

### Basic Usage

```python
from camera_stats_module import create_camera_monitor

# Create and run camera monitor with default settings
monitor = create_camera_monitor()
monitor.run()
```

### Custom Configuration

```python
from camera_stats_module import CameraStatsMonitor

# Create monitor with custom settings
monitor = CameraStatsMonitor(
    camera_index=1,      # Camera device index
    oled_addr=0x3C,      # OLED I2C address
    history_length=64    # Temperature history length
)

monitor.run(update_interval=0.5)  # Update every 0.5 seconds
```

### Programmatic Control

```python
monitor = CameraStatsMonitor()

# Start the monitor
if monitor.start():
    # Get current statistics
    stats = monitor.get_stats()
    print(f"Current temperature: {stats['current_temperature']:.1f}°C")
    
    # Update stats manually
    temp = monitor.update_stats()
    
    # Stop when done
    monitor.stop()
```

## Configuration

### Camera Settings
- `camera_index`: Camera device index (default: 2)
  - Try 0, 1, or 2 depending on your camera setup
  - Arducam modules often use index 2

### OLED Settings
- `oled_addr`: I2C address of OLED display (default: 0x3C)
- Connected to I2C port 1 (typical for Raspberry Pi)

### Temperature Monitoring
- Reads from `/sys/class/thermal/thermal_zone0/temp` (Linux thermal zone)
- Fallback to `vcgencmd measure_temp` (Raspberry Pi specific)
- Updates at configurable intervals (default: 1 second)

## OLED Display Layout

```
Camera + CPU Stats
CPU: 45.2°C
Frames: 1234
Temp Trend:
*#*..*#*..*.#*..
```

- Line 1: Title
- Line 2: Current CPU temperature
- Line 3: Frame count
- Line 4: Temperature trend label
- Line 5: Sparkline showing temperature history

## Dependencies

Required packages (from requirements.txt):
- `opencv-python` - Camera capture
- `luma.oled` - OLED display control
- Standard library modules: `time`, `os`, `collections`

## Hardware Requirements

- Camera compatible with OpenCV (USB webcam, Arducam, etc.)
- SSD1306 OLED display connected via I2C
- System with thermal zone support (Linux/Raspberry Pi)

## Error Handling

- Graceful fallback if OLED display cannot be initialized
- Simulated temperature data if thermal sensors unavailable
- Proper cleanup of camera and display resources
- Keyboard interrupt handling (Ctrl+C)

## Examples

Run the examples to test different usage patterns:

```bash
python camera_examples.py
```

Choose from:
1. Basic usage with default settings
2. Custom configuration example
3. Programmatic stats monitoring

## Integration

The module can be easily integrated into larger projects:

```python
# In your main application
from camera_stats_module import CameraStatsMonitor

class MyApp:
    def __init__(self):
        self.camera_monitor = CameraStatsMonitor()
    
    def start_monitoring(self):
        if self.camera_monitor.start():
            # Camera and OLED initialized successfully
            return True
        return False
    
    def get_current_temp(self):
        stats = self.camera_monitor.get_stats()
        return stats['current_temperature']
```

## Troubleshooting

### Camera Issues
- Check camera index (try 0, 1, or 2)
- Verify camera permissions
- Ensure camera isn't used by another application

### OLED Issues
- Check I2C connection and address
- Verify OLED power supply
- Enable I2C interface (Raspberry Pi: `sudo raspi-config`)

### Temperature Reading Issues
- Module falls back to simulated data
- Check thermal zone files exist: `/sys/class/thermal/thermal_zone0/temp`
- For Raspberry Pi: ensure `vcgencmd` is available
