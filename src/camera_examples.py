#!/usr/bin/env python3
"""
Example usage of the CameraStatsMonitor module
"""

from camera import CameraStatsMonitor, create_camera_monitor
import time


def example_basic_usage():
    """Basic usage example"""
    print("=== Basic Usage Example ===")
    
    # Create and run camera monitor with default settings
    monitor = create_camera_monitor()
    monitor.run()


def example_custom_configuration():
    """Example with custom configuration"""
    print("=== Custom Configuration Example ===")
    
    # Create monitor with custom settings
    monitor = CameraStatsMonitor(
        camera_index=1,      # Try camera index 1 instead of 2
        oled_addr=0x3C,      # OLED I2C address
        history_length=64    # Keep more temperature history
    )
    
    # Start the monitor
    if monitor.start():
        print("Monitor started successfully!")
        
        # Run for a specific duration
        try:
            start_time = time.time()
            while time.time() - start_time < 30:  # Run for 30 seconds
                monitor.run()
                break  # run() will handle the loop
        except KeyboardInterrupt:
            pass
        finally:
            monitor.stop()


def example_stats_monitoring():
    """Example showing how to monitor stats programmatically"""
    print("=== Stats Monitoring Example ===")
    
    monitor = CameraStatsMonitor()
    
    if not monitor.start():
        print("Failed to start monitor")
        return
    
    try:
        # Monitor stats for a short period
        for i in range(10):
            # Update stats
            temp = monitor.update_stats()
            stats = monitor.get_stats()
            
            print(f"Update {i+1}:")
            print(f"  Current temp: {temp:.1f}°C")
            print(f"  Frame count: {stats['frame_count']}")
            print(f"  History length: {len(stats['temperature_history'])}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        pass
    finally:
        monitor.stop()


if __name__ == "__main__":
    print("Camera Stats Module Examples")
    print("Choose an example to run:")
    print("1. Basic usage (default)")
    print("2. Custom configuration")
    print("3. Stats monitoring")
    
    choice = input("Enter choice (1-3, default=1): ").strip()
    
    if choice == "2":
        example_custom_configuration()
    elif choice == "3":
        example_stats_monitoring()
    else:
        example_basic_usage()
