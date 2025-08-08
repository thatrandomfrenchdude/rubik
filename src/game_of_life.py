#!/usr/bin/env python3
"""
Conway's Game of Life displayed on the SSD1306 OLED used in camera.py.

Features:
- 128x64 OLED with bottom 8px reserved for stats text (grid: 128x56)
- 1px per cell life grid
- Random initial seeding (configurable density + RNG seed)
- Generation stepping with Conway rules (finite grid, edges have fewer neighbors)
- Stats tracking: generations, current population, initial, peak, average, runtime
- Extinction detection: when population hits 0, print stats & exit
"""

import time
import random
import argparse
import statistics
from dataclasses import dataclass, field

# OLED / Luma imports
try:
    from luma.core.interface.serial import i2c
    from luma.core.render import canvas
    from luma.oled.device import ssd1306
except ImportError:  # Allow graceful failure if libraries not present
    i2c = canvas = ssd1306 = None


OLED_WIDTH = 128
OLED_HEIGHT = 64
STATS_BAR_HEIGHT = 8  # Reserve bottom row (8px) for a single text line
GRID_HEIGHT = OLED_HEIGHT - STATS_BAR_HEIGHT  # 56
GRID_WIDTH = OLED_WIDTH  # 128


@dataclass
class LifeStats:
    generation: int = 0
    initial_population: int = 0
    population: int = 0
    peak_population: int = 0
    cumulative_population: int = 0
    start_time: float = field(default_factory=time.time)
    pop_history: list = field(default_factory=list)

    def update(self, population: int):
        self.generation += 1
        self.population = population
        if self.generation == 1:
            self.initial_population = population
        if population > self.peak_population:
            self.peak_population = population
        self.cumulative_population += population
        self.pop_history.append(population)

    @property
    def average_population(self) -> float:
        if self.generation == 0:
            return 0.0
        return self.cumulative_population / self.generation

    @property
    def runtime(self) -> float:
        return time.time() - self.start_time


class GameOfLifeOLED:
    def __init__(self, density: float = 0.25, seed: int | None = None, fps: float = 12.0, oled_addr: int = 0x3C):
        """
        Args:
            density: Probability a cell starts alive (0..1)
            seed: RNG seed (optional)
            fps: target frames (generations) per second
            oled_addr: I2C address of the SSD1306
        """
        if seed is None:
            seed = int(time.time())
        self.seed = seed
        random.seed(seed)
        self.density = max(0.0, min(1.0, density))
        self.fps = fps
        self.frame_delay = 1.0 / fps if fps > 0 else 0.0
        self.oled_addr = oled_addr
        self.serial = None
        self.device = None
        self.stats = LifeStats()

        # Board representation: 2D list of 0/1 ints
        self.board = self._random_board()

    # --- Initialization helpers ---
    def init_oled(self) -> bool:
        if i2c is None:
            print("luma.oled not installed; running headless (no display)")
            return False
        try:
            self.serial = i2c(port=1, address=self.oled_addr)
            self.device = ssd1306(self.serial)
            return True
        except Exception as e:
            print(f"Failed to init OLED: {e}")
            return False

    def _random_board(self):
        return [ [1 if random.random() < self.density else 0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT) ]

    # --- Game logic ---
    def step(self):
        new_board = [ [0]*GRID_WIDTH for _ in range(GRID_HEIGHT) ]
        population = 0
        # Pre-calc neighbor offsets
        offsets = (-1, 0, 1)
        for y in range(GRID_HEIGHT):
            row = self.board[y]
            for x in range(GRID_WIDTH):
                alive = row[x]
                neighbors = 0
                # Count neighbors (bounded grid)
                for dy in offsets:
                    ny = y + dy
                    if ny < 0 or ny >= GRID_HEIGHT:
                        continue
                    nrow = self.board[ny]
                    for dx in offsets:
                        if dx == 0 and dy == 0:
                            continue
                        nx = x + dx
                        if nx < 0 or nx >= GRID_WIDTH:
                            continue
                        neighbors += nrow[nx]
                # Apply Conway's rules
                if alive:
                    new_alive = 1 if neighbors in (2, 3) else 0
                else:
                    new_alive = 1 if neighbors == 3 else 0
                new_board[y][x] = new_alive
                population += new_alive
        self.board = new_board
        self.stats.update(population)
        return population

    # --- Rendering ---
    def render(self):
        if not self.device:
            return  # Headless mode
        with canvas(self.device) as draw:
            # Draw live cells
            for y, row in enumerate(self.board):
                for x, cell in enumerate(row):
                    if cell:
                        draw.point((x, y), fill=1)
            # Stats line at bottom
            draw.text((0, GRID_HEIGHT), f"G:{self.stats.generation} P:{self.stats.population}", fill=1)

    # --- Main loop ---
    def run(self):
        display_ok = self.init_oled()
        # Count initial population as generation 0 baseline (we treat first step as generation 1)
        initial_pop = sum(sum(row) for row in self.board)
        # Record as generation 1 stats (so generation numbers represent displayed generations)
        self.stats.update(initial_pop)
        if display_ok:
            self.render()
        if initial_pop == 0:
            print("Initial board extinct; regenerating...")
            self.board = self._random_board()
            initial_pop = sum(sum(r) for r in self.board)
            self.stats = LifeStats()  # reset stats
            self.stats.update(initial_pop)
            if display_ok:
                self.render()
        last_time = time.time()
        try:
            while True:
                if self.stats.population == 0:
                    break  # extinction reached
                start = time.time()
                self.step()
                if display_ok:
                    self.render()
                # Frame pacing
                elapsed = time.time() - start
                sleep_for = self.frame_delay - elapsed
                if sleep_for > 0:
                    time.sleep(sleep_for)
                last_time = start
        except KeyboardInterrupt:
            print("Interrupted by user.")
        finally:
            self._finalize(display_ok)

    # --- Finalization ---
    def _finalize(self, display_ok: bool):
        if display_ok and self.device:
            # Clear display
            with canvas(self.device):
                pass
        self.print_stats()

    def print_stats(self):
        if not self.stats.pop_history:
            print("No statistics gathered.")
            return
        print("\nGame of Life Extinction Stats")
        print("Seed:              ", self.seed)
        print("Grid:              ", f"{GRID_WIDTH} x {GRID_HEIGHT}")
        print("Initial population:", self.stats.initial_population)
        print("Generations:       ", self.stats.generation)
        print("Peak population:   ", self.stats.peak_population)
        print("Average population:", f"{self.stats.average_population:.2f}")
        print("Runtime (s):       ", f"{self.stats.runtime:.2f}")
        if len(self.stats.pop_history) > 1:
            try:
                print("Population stdev:  ", f"{statistics.pstdev(self.stats.pop_history):.2f}")
            except statistics.StatisticsError:
                pass
        # Simple sparkline (optional)
        history = self.stats.pop_history
        if len(history) > 0:
            spark = self._sparkline(history[-min(64, len(history)):])
            print("Recent pop trend:  ", spark)

    @staticmethod
    def _sparkline(series):
        # Basic ascii sparkline (▁▂▃▄▅▆▇█)
        if not series:
            return ""
        blocks = "▁▂▃▄▅▆▇█"
        lo, hi = min(series), max(series)
        rng = hi - lo or 1
        return ''.join(blocks[int((v - lo) / rng * (len(blocks)-1))] for v in series)


def parse_args():
    p = argparse.ArgumentParser(description="Conway's Game of Life on SSD1306 OLED")
    p.add_argument('--density', type=float, default=0.25, help='Initial live cell probability (0-1)')
    p.add_argument('--seed', type=int, default=None, help='RNG seed (default: time-based)')
    p.add_argument('--fps', type=float, default=12.0, help='Generations per second')
    return p.parse_args()


def main():
    args = parse_args()
    game = GameOfLifeOLED(density=args.density, seed=args.seed, fps=args.fps)
    print(f"Starting Game of Life (seed={game.seed}, density={game.density}, fps={game.fps})")
    game.run()


if __name__ == '__main__':
    main()
