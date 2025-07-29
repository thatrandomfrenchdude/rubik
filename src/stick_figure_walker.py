#!/usr/bin/env python3
"""
Stick Figure Walking Animation for OLED Display

Creates an animated stick figure that walks around the perimeter of the SSD        try:
            # Clear display and draw stick figure
            with canvas(display) as draw:
                # Draw the stick figure
                figure.draw(draw)splay.
The stick figure will walk clockwise around the edges of the 128x64 pixel display with
walking animation including leg movement.

Hardware requirements:
  • Rubik Pi with SSD1306 OLED display on I2C1 (pins 3 & 5)
  • Power: pin 1 (3V3), Ground: pin 9

Dependencies: luma.oled
"""

import time
import math
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

# Display dimensions
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64

# Stick figure dimensions
FIGURE_HEIGHT = 12
FIGURE_WIDTH = 8

# Animation settings
ANIMATION_SPEED = 0.1  # seconds between frames
WALK_SPEED = 2  # pixels per frame

class StickFigure:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.direction = 0  # 0=right, 1=down, 2=left, 3=up
        self.step_phase = 0  # for walking animation (0-7)
        self.perimeter_position = 0  # position along the perimeter
        
    def update_position(self):
        """Update the stick figure's position along the perimeter."""
        # Calculate total perimeter - keeping figure fully on screen
        top_edge = DISPLAY_WIDTH - FIGURE_WIDTH
        right_edge = DISPLAY_HEIGHT - FIGURE_HEIGHT  
        bottom_edge = DISPLAY_WIDTH - FIGURE_WIDTH
        left_edge = DISPLAY_HEIGHT - FIGURE_HEIGHT
        perimeter = top_edge + right_edge + bottom_edge + left_edge
        
        # Move along perimeter
        self.perimeter_position = (self.perimeter_position + WALK_SPEED) % perimeter
        
        # Convert perimeter position to x,y coordinates and direction
        if self.perimeter_position < top_edge:
            # Top edge - walking right
            self.x = self.perimeter_position
            self.y = 0
            self.direction = 0
        elif self.perimeter_position < top_edge + right_edge:
            # Right edge - walking down
            self.x = DISPLAY_WIDTH - FIGURE_WIDTH
            self.y = self.perimeter_position - top_edge
            self.direction = 1
        elif self.perimeter_position < top_edge + right_edge + bottom_edge:
            # Bottom edge - walking left
            self.x = DISPLAY_WIDTH - FIGURE_WIDTH - (self.perimeter_position - top_edge - right_edge)
            self.y = DISPLAY_HEIGHT - FIGURE_HEIGHT
            self.direction = 2
        else:
            # Left edge - walking up
            self.x = 0
            self.y = DISPLAY_HEIGHT - FIGURE_HEIGHT - (self.perimeter_position - top_edge - right_edge - bottom_edge)
            self.direction = 3
        
        # Update walking animation phase
        self.step_phase = (self.step_phase + 1) % 8
    
    def draw(self, draw):
        """Draw the stick figure with walking animation."""
        # Base position
        x, y = int(self.x), int(self.y)
        
        # Head (circle represented as a small square)
        head_x = x + FIGURE_WIDTH // 2 - 1
        head_y = y
        draw.rectangle([head_x, head_y, head_x + 2, head_y + 2], fill=1)
        
        # Body (vertical line)
        body_top = y + 3
        body_bottom = y + 8
        body_x = x + FIGURE_WIDTH // 2
        draw.line([body_x, body_top, body_x, body_bottom], fill=1)
        
        # Arms (horizontal line from body)
        arm_y = y + 5
        arm_left = x + 1
        arm_right = x + FIGURE_WIDTH - 2
        draw.line([arm_left, arm_y, arm_right, arm_y], fill=1)
        
        # Legs with walking animation
        leg_start_x = body_x
        leg_start_y = body_bottom
        
        # Calculate leg positions based on walking phase and direction
        leg_offset = 2 if self.step_phase < 4 else -2
        
        if self.direction == 0:  # Walking right
            # Right leg
            draw.line([leg_start_x, leg_start_y, leg_start_x + leg_offset, leg_start_y + 4], fill=1)
            # Left leg  
            draw.line([leg_start_x, leg_start_y, leg_start_x - leg_offset, leg_start_y + 4], fill=1)
        elif self.direction == 1:  # Walking down
            # Right leg
            draw.line([leg_start_x, leg_start_y, leg_start_x + 2, leg_start_y + 2 + leg_offset], fill=1)
            # Left leg
            draw.line([leg_start_x, leg_start_y, leg_start_x - 2, leg_start_y + 2 - leg_offset], fill=1)
        elif self.direction == 2:  # Walking left
            # Right leg
            draw.line([leg_start_x, leg_start_y, leg_start_x - leg_offset, leg_start_y + 4], fill=1)
            # Left leg
            draw.line([leg_start_x, leg_start_y, leg_start_x + leg_offset, leg_start_y + 4], fill=1)
        else:  # Walking up (direction == 3)
            # Right leg
            draw.line([leg_start_x, leg_start_y, leg_start_x + 2, leg_start_y + 2 - leg_offset], fill=1)
            # Left leg
            draw.line([leg_start_x, leg_start_y, leg_start_x - 2, leg_start_y + 2 + leg_offset], fill=1)

def clear_display(display):
    """Clear the OLED display."""
    with canvas(display) as draw:
        pass  # Drawing nothing clears the display

def draw_scenery(draw):
    """Draw trees, lake, and flowers in the center area."""
    # Lake (oval in center)
    lake_x, lake_y = 50, 25
    lake_w, lake_h = 28, 14
    draw.ellipse([lake_x, lake_y, lake_x + lake_w, lake_y + lake_h], outline=1, fill=0)
    
    # Trees (simple triangles with trunks)
    # Tree 1 (left side)
    tree1_x, tree1_y = 25, 20
    draw.polygon([(tree1_x, tree1_y + 8), (tree1_x + 4, tree1_y), (tree1_x + 8, tree1_y + 8)], outline=1, fill=1)
    draw.rectangle([tree1_x + 3, tree1_y + 8, tree1_x + 5, tree1_y + 12], fill=1)
    
    # Tree 2 (right side)
    tree2_x, tree2_y = 85, 15
    draw.polygon([(tree2_x, tree2_y + 10), (tree2_x + 5, tree2_y), (tree2_x + 10, tree2_y + 10)], outline=1, fill=1)
    draw.rectangle([tree2_x + 4, tree2_y + 10, tree2_x + 6, tree2_y + 15], fill=1)
    
    # Flowers (small dots with stems)
    # Flower 1
    draw.point((35, 45), fill=1)
    draw.line([(35, 45), (35, 48)], fill=1)
    
    # Flower 2
    draw.point((90, 45), fill=1)
    draw.line([(90, 45), (90, 48)], fill=1)
    
    # Flower 3
    draw.point((45, 15), fill=1)
    draw.line([(45, 15), (45, 18)], fill=1)

def init_display():
    """Initialize the OLED display."""
    serial = i2c(port=1, address=0x3C)  # I2C port 1, typical SSD1306 address
    return ssd1306(serial)

def run_walking_animation():
    """Main animation loop."""
    print("Starting stick figure walking animation...")
    print("The stick figure will walk clockwise around the display perimeter")
    print("Press Ctrl+C to stop")
    
    # Initialize display
    display = init_display()
    
    # Create stick figure
    figure = StickFigure()
    
    try:
        while True:
            # Clear display and draw stick figure
            with canvas(display) as draw:
                # Draw scenery first (background)
                draw_scenery(draw)
                
                # Draw the stick figure (foreground)
                figure.draw(draw)
            
            # Update position for next frame
            figure.update_position()
            
            # Control animation speed
            time.sleep(ANIMATION_SPEED)
            
    except KeyboardInterrupt:
        print("\nStopping animation...")
        clear_display(display)
        print("Animation stopped")
    except Exception as e:
        print(f"\nError: {e}")
        clear_display(display)
    finally:
        print("Display cleanup complete")

if __name__ == "__main__":
    run_walking_animation()
