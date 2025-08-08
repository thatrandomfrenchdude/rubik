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
- Stability / oscillation detection: detect small-period oscillators & exit
"""

import time
import random
import argparse
import statistics
from dataclasses import dataclass, field
from typing import Dict, Tuple

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
    termination_reason: str | None = None

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


class StabilityDetector:
    """Detects small-period oscillations / stability by hashing board states.

    If the exact board state repeats with a period <= max_period a certain
    number of times (min_repeats confirmations), we declare stability.
    """
    def __init__(self, max_period: int = 10, min_repeats: int = 3):
        self.max_period = max_period
        self.min_repeats = min_repeats
        self.last_seen: Dict[int, int] = {}            # hash -> generation
        self.period_counts: Dict[Tuple[int, int], int] = {}  # (hash, period) -> count
        self.last_period: int | None = None
        self.trigger_hash: int | None = None

    def observe(self, h: int, generation: int) -> bool:
        if h in self.last_seen:
            period = generation - self.last_seen[h]
            if 0 < period <= self.max_period:
                key = (h, period)
                self.period_counts[key] = self.period_counts.get(key, 0) + 1
                if self.period_counts[key] >= self.min_repeats:
                    self.last_period = period
                    self.trigger_hash = h
                    return True
        self.last_seen[h] = generation
        return False


class GameOfLifeOLED:
    def __init__(self, density: float = 0.25, seed: int | None = None, fps: float = 12.0, oled_addr: int = 0x3C,
                 max_period: int = 10, min_repeats: int = 3):
        """
        Args:
            density: Probability a cell starts alive (0..1)
            seed: RNG seed (optional)
            fps: target frames (generations) per second
            oled_addr: I2C address of the SSD1306
            max_period: Maximum oscillator period considered "stable"
            min_repeats: Number of confirmations (state appearances) needed
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
        self.stability = StabilityDetector(max_period=max_period, min_repeats=min_repeats)

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
        return [[1 if random.random() < self.density else 0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def _board_hash(self) -> int:
        # Efficient stable hash (convert each row bits into bytes then hash)
        # Simpler: join string of 0/1; Python hash randomization ok across run
        return hash('\n'.join(''.join('1' if c else '0' for c in row) for row in self.board))

    # --- Game logic ---
    def step(self):
        new_board = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        population = 0
        offsets = (-1, 0, 1)
        for y in range(GRID_HEIGHT):
            row = self.board[y]
            for x in range(GRID_WIDTH):
                alive = row[x]
                neighbors = 0
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
            for y, row in enumerate(self.board):
                for x, cell in enumerate(row):
                    if cell:
                        draw.point((x, y), fill=1)
            draw.text((0, GRID_HEIGHT), f"G:{self.stats.generation} P:{self.stats.population}", fill=1)

    # --- Main loop ---
    def run(self):
        display_ok = self.init_oled()
        initial_pop = sum(sum(row) for row in self.board)
        self.stats.update(initial_pop)
        if display_ok:
            self.render()
        if initial_pop == 0:
            print("Initial board extinct; regenerating...")
            self.board = self._random_board()
            initial_pop = sum(sum(r) for r in self.board)
            self.stats = LifeStats()
            self.stats.update(initial_pop)
            if display_ok:
                self.render()
        # Register initial board hash AFTER stats gen=1
        self.stability.observe(self._board_hash(), self.stats.generation)
        try:
            while True:
                if self.stats.population == 0:
                    self.stats.termination_reason = "extinction"
                    break
                start = time.time()
                self.step()
                h = self._board_hash()
                if self.stability.observe(h, self.stats.generation):
                    self.stats.termination_reason = (
                        f"stability(period={self.stability.last_period}, repeats>={self.stability.period_counts[(self.stability.trigger_hash, self.stability.last_period)]})"
                    )
                    break
                if display_ok:
                    self.render()
                elapsed = time.time() - start
                sleep_for = self.frame_delay - elapsed
                if sleep_for > 0:
                    time.sleep(sleep_for)
        except KeyboardInterrupt:
            if not self.stats.termination_reason:
                self.stats.termination_reason = "user-interrupt"
            print("Interrupted by user.")
        finally:
            self._finalize(display_ok)

    # --- Finalization ---
    def _finalize(self, display_ok: bool):
        if display_ok and self.device:
            with canvas(self.device):
                pass
        self.print_stats()

    def print_stats(self):
        if not self.stats.pop_history:
            print("No statistics gathered.")
            return
        print("\nGame of Life Termination Stats")
        print("Reason:            ", self.stats.termination_reason)
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
        history = self.stats.pop_history
        if len(history) > 0:
            spark = self._sparkline(history[-min(64, len(history)):])
            print("Recent pop trend:  ", spark)

    @staticmethod
    def _sparkline(series):
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
    p.add_argument('--max-period', type=int, default=10, help='Max oscillator period to treat as stable')
    p.add_argument('--min-repeats', type=int, default=3, help='Times the same state must recur (with same period) before exiting')
    return p.parse_args()


def main():
    args = parse_args()
    game = GameOfLifeOLED(density=args.density, seed=args.seed, fps=args.fps,
                          max_period=args.max_period, min_repeats=args.min_repeats)
    print(f"Starting Game of Life (seed={game.seed}, density={game.density}, fps={game.fps}, max_period={game.stability.max_period})")
    game.run()


if __name__ == '__main__':
    main()
