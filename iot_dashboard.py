#!/usr/bin/env python3
"""
Terminal-only IoT dashboard – “slightly fancy, never boring”.

  • Live CPU temperature, CPU load, RAM, ping latency
  • Unicode spark-line of the last 30 temperature samples
  • Optional LED alert on GPIO17 (or the Pi’s ACT LED) if CPU ≥ 65 °C

Dependencies: rich, psutil, ping3, gpiozero   (≈150 KiB total)
"""

import time
import statistics
import warnings
from collections import deque

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich import box

import psutil
from ping3 import ping

# ───────────────────────── GPIO / LED Support ────────────────────────────────
# Many boards (or containers) don’t have native GPIO.  We detect that situation
# and fall back to a “mock” pin factory – no scary warnings, no crash.
try:
    # Suppress gpiozero’s pin-factory warnings **before** importing it
    warnings.filterwarnings("ignore", category=UserWarning, module="gpiozero")
    from gpiozero import Device, LED, CPUTemperature
    from gpiozero.pins.mock import MockFactory

    try:                       # real hardware?
        cpu_sensor = CPUTemperature()
        led = LED("LED")       # Pi’s on-board ACT LED
    except Exception:          # not a Pi – swap to mock pins
        Device.pin_factory = MockFactory()
        cpu_sensor = None      # psutil fallback handles temp
        led = LED(17)          # mock LED (does nothing)
    led_available = True
except ImportError:            # gpiozero not installed
    cpu_sensor = None
    led_available = False

# ────────────────────────── Helpers ──────────────────────────────────────────
HOST = "8.8.8.8"
HISTORY = 30
ALERT_TEMP = 65.0           # °C

console = Console()
history = deque(maxlen=HISTORY)


def read_cpu_temp() -> float | None:
    """Return CPU temperature in °C, or None if unavailable."""
    if cpu_sensor:
        return cpu_sensor.temperature
    # psutil fallback (works on most Linux systems with /sys/class/thermal)
    for temps in psutil.sensors_temperatures().values():
        for entry in temps:
            if "cpu" in (entry.label or "").lower() or entry.label == "":
                return entry.current
    return None


def sparkline(series):
    """Very small unicode temperature trend."""
    blocks = []
    for t in series:
        if t is None:
            blocks.append(" ")
        elif t >= ALERT_TEMP:
            blocks.append("⣿")
        else:
            blocks.append("⡆")
    return "".join(blocks)


def build_table(temp, cpu, mem, rtt):
    tbl = Table(title="🛰️  IoT Board Live Metrics", box=box.SIMPLE_HEAVY)
    add = tbl.add_row
    add("CPU Temp (°C)", f"{temp:.1f}" if temp else "N/A")
    add("CPU Load (%)", f"{cpu:.1f}")
    add("RAM Used (%)", f"{mem:.1f}")
    add(f"Ping {HOST} (ms)", f"{rtt:.1f}" if rtt else "N/A")
    add("Temp Trend", sparkline(history))
    return tbl


def safe_ping(host: str, **kwargs):
    """
    Call ping3.ping() in a way that works across versions:
      • v4.x accepts 'privileged'
      • v3.x and earlier do not
    """
    try:             # Try the modern signature first …
        return ping(host, privileged=False, unit="ms", **kwargs)
    except TypeError:
        return ping(host, unit="ms", **kwargs)


# ──────────────────────────── Main loop ──────────────────────────────────────
try:
    with Live(console=console, auto_refresh=False) as live:
        while True:
            temp = read_cpu_temp()
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            rtt = safe_ping(HOST, timeout=1)

            history.append(temp)
            live.update(Panel(build_table(temp, cpu, mem, rtt), border_style="cyan"),
                        refresh=True)

            if led_available:
                (led.on() if temp and temp >= ALERT_TEMP else led.off())

            time.sleep(1)

except KeyboardInterrupt:
    if led_available:
        led.off()
    console.print("\n[bold green]Bye![/bold green]")