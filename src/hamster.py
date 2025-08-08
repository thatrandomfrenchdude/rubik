#!/usr/bin/env python3
"""Hamster-in-a-wheel OLED animation.

Displays an endlessly running hamster inside a rotating exercise wheel on the
128x64 SSD1306 OLED (same device as used in camera.py). Falls back to a simple
ASCII terminal animation if luma.oled is not installed or the display cannot
initialize.

Ctrl-C to exit.
"""
from __future__ import annotations

import math
import time
import argparse
from dataclasses import dataclass

# Luma OLED libs
try:
    from luma.core.interface.serial import i2c  # type: ignore
    from luma.core.render import canvas  # type: ignore
    from luma.oled.device import ssd1306  # type: ignore
except ImportError:  # Headless fallback
    i2c = canvas = ssd1306 = None  # type: ignore

OLED_W = 128
OLED_H = 64


@dataclass
class WheelConfig:
    cx: int = 64          # center x
    cy: int = 32          # center y (leave space bottom if wanted)
    radius: int = 26      # outer wheel radius
    track_thickness: int = 2
    hamster_radius: int = 4
    inner_margin: int = 4  # distance inside wheel rim for hamster center path
    spokes: int = 8


class HamsterWheel:
    def __init__(self, fps: float = 15.0, oled_addr: int = 0x3C, rev_time: float = 2.5, direction: int = 1):
        self.fps = fps
        self.frame_delay = 1.0 / fps if fps > 0 else 0.0
        self.oled_addr = oled_addr
        self.rev_time = max(0.2, rev_time)  # seconds per full revolution
        self.direction = 1 if direction >= 0 else -1
        self.serial = None
        self.device = None
        self.cfg = WheelConfig()
        self._start = time.time()
        self._frame = 0
        self._headless = False
        # Leg animation parameters
        self._leg_cycle_len = 4      # number of distinct poses
        self._leg_frames_per_pose = 2  # frames each pose persists

    # --- Initialization ---
    def init(self):
        if i2c is None:
            print("luma.oled not installed; running headless ASCII animation")
            self._headless = True
            return False
        try:
            self.serial = i2c(port=1, address=self.oled_addr)
            self.device = ssd1306(self.serial)
            return True
        except Exception as e:
            print(f"Could not init OLED ({e}); headless mode.")
            self._headless = True
            return False

    # --- Frame computation ---
    def _angles(self):
        # Current base angle based on time so speed independent of frame drops
        elapsed = time.time() - self._start
        turns = (elapsed / self.rev_time) * self.direction
        base_angle = (turns % 1.0) * 2 * math.pi
        return base_angle

    def _hamster_pos(self):
        """Fixed hamster position at bottom inside wheel to give running illusion."""
        x = self.cfg.cx
        y = self.cfg.cy + (self.cfg.radius - self.cfg.inner_margin)
        return x, y

    # --- Drawing helpers (OLED) ---
    def _draw_circle(self, draw, cx, cy, r):
        # Midpoint circle approx via parametric points for simplicity
        steps = max(32, int(2 * math.pi * r))
        for i in range(steps):
            ang = 2 * math.pi * i / steps
            x = cx + int(r * math.cos(ang))
            y = cy + int(r * math.sin(ang))
            draw.point((x, y), fill=1)

    def _draw_hamster(self, draw, x, y):
        hr = self.cfg.hamster_radius
        # Body (filled circle approximation)
        for yy in range(-hr, hr + 1):
            for xx in range(-hr, hr + 1):
                if xx*xx + yy*yy <= hr*hr:
                    draw.point((x + xx, y + yy), fill=1)
        # Ear
        draw.point((x + hr//2, y - hr), fill=1)
        # Tail
        draw.point((x - hr - 1, y), fill=1)
        # Animated legs
        pose = (self._frame // self._leg_frames_per_pose) % self._leg_cycle_len
        # Define leg endpoints relative to body center bottom
        # Two front legs (right side), two back legs (left side)
        # Poses cycle: extend / mid / opposite extend / mid
        leg_y_base = y + hr - 1
        # Small vertical bob to simulate stride
        bob = 0 if pose % 2 == 0 else 1
        # Front legs
        if pose == 0:        # front extended forward
            front_offsets = [(+2, 0), (+3, +1)]
            back_offsets = [(-2, +1), (-3, 0)]
        elif pose == 1:      # gather
            front_offsets = [(+1, +1), (+2, +1)]
            back_offsets = [(-1, +1), (-2, +1)]
        elif pose == 2:      # front back, rear forward (opposite)
            front_offsets = [(+1, +1), (+0, 0)]
            back_offsets = [(-2, 0), (-3, +1)]
        else:                 # gather
            front_offsets = [(+1, +1), (+2, +1)]
            back_offsets = [(-1, +1), (-2, +1)]
        # Draw legs as short 1px or 2px strokes
        for dx, dy in front_offsets:
            draw.point((x + dx, leg_y_base + dy - bob), fill=1)
        for dx, dy in back_offsets:
            draw.point((x + dx, leg_y_base + dy - bob), fill=1)

    def _draw_spokes(self, draw, base_angle):
        for i in range(self.cfg.spokes):
            ang = base_angle + (2 * math.pi / self.cfg.spokes) * i
            x1 = self.cfg.cx + int((self.cfg.radius - 1) * math.cos(ang))
            y1 = self.cfg.cy + int((self.cfg.radius - 1) * math.sin(ang))
            draw.line((self.cfg.cx, self.cfg.cy, x1, y1), fill=1)

    # --- Render a frame to OLED ---
    def render_oled(self):
        if not self.device:
            return
        ang = self._angles()
        with canvas(self.device) as draw:
            # Wheel rim (outer + inner thickness)
            for t in range(self.cfg.track_thickness):
                self._draw_circle(draw, self.cfg.cx, self.cfg.cy, self.cfg.radius - t)
            self._draw_spokes(draw, ang)
            # Hamster fixed (does not rotate with wheel)
            hx, hy = self._hamster_pos()
            self._draw_hamster(draw, hx, hy)

    # --- Headless ASCII fallback ---
    def render_ascii(self):
        # Simple coarse grid 40x20
        W, H = 40, 20
        grid = [[' ']*W for _ in range(H)]
        ang = self._angles()
        cx, cy = W//2, H//2
        r = min(cx, cy) - 2
        # Wheel perimeter
        steps = 120
        for i in range(steps):
            a = 2*math.pi*i/steps
            x = cx + int(r * math.cos(a))
            y = cy + int(r * math.sin(a))
            if 0 <= x < W and 0 <= y < H:
                grid[y][x] = '#'
        # Spokes
        for i in range(8):
            a = ang + (2*math.pi/8)*i
            x = cx + int(r * math.cos(a))
            y = cy + int(r * math.sin(a))
            if 0 <= x < W and 0 <= y < H:
                grid[y][x] = '*'
        # Hamster body (simple 'O')
        hx, hy = cx, cy + r - 1
        if hy >= H:
            hy = H - 2
        grid[hy][hx] = 'O'
        # Simple leg animation indicator underneath
        pose = (self._frame // self._leg_frames_per_pose) % self._leg_cycle_len
        leg_char = ['/', '|', '\\', '|'][pose]
        if hy+1 < H:
            grid[hy+1][hx] = leg_char
        print("\033[H\033[J", end='')
        print("Hamster Wheel (ASCII fallback)")
        for row in grid:
            print(''.join(row))
        print("Ctrl-C to exit. FPS=", self.fps)

    # --- Main loop ---
    def run(self):
        self.init()
        try:
            while True:
                start = time.time()
                if self._headless:
                    self.render_ascii()
                else:
                    self.render_oled()
                self._frame += 1
                elapsed = time.time() - start
                sleep_for = self.frame_delay - elapsed
                if sleep_for > 0:
                    time.sleep(sleep_for)
        except KeyboardInterrupt:
            pass
        finally:
            if self.device:
                # Clear display
                from contextlib import suppress
                with suppress(Exception):
                    with canvas(self.device):
                        pass


def parse_args():
    p = argparse.ArgumentParser(description="Hamster wheel OLED animation")
    p.add_argument('--fps', type=float, default=15.0, help='Frames per second')
    p.add_argument('--rev-time', type=float, default=2.5, help='Seconds per full wheel revolution')
    p.add_argument('--direction', type=int, default=1, help='Wheel direction (1 or -1)')
    p.add_argument('--addr', type=lambda x: int(x, 0), default=0x3C, help='I2C address (default 0x3C)')
    return p.parse_args()


def main():
    args = parse_args()
    wheel = HamsterWheel(fps=args.fps, oled_addr=args.addr, rev_time=args.rev_time, direction=args.direction)
    wheel.run()


if __name__ == '__main__':
    main()
