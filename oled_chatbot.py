#!/usr/bin/env python3
"""
OLED Chatbot - Modified version of cl_chatbot.py that displays on OLED screen.

Displays chatbot conversation on SSD1306 OLED display with auto-scrolling.
Based on cl_chatbot.py but outputs to OLED instead of console.

Hardware requirements:
  • Rubik Pi with SSD1306 OLED display on I2C1 (pins 3 & 5)
  • Power: pin 1 (3V3), Ground: pin 9

Dependencies: luma.oled, openai, pyyaml
"""

import yaml
import time
import textwrap
from collections import deque
from openai import OpenAI

# Import OLED display functionality
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

class OLEDChatbot:
    def __init__(self):
        # Load configuration
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=config.get("LLAMA_API_KEY"),
            base_url="https://api.llama.com/compat/v1/",
        )
        self.chat_history = []
        
        # Initialize OLED display
        serial = i2c(port=1, address=0x3C)  # I2C port 1, typical SSD1306 address
        self.display = ssd1306(serial)
        
        # Display settings
        self.line_height = 8  # pixels per line
        self.char_width = 6   # approximate pixels per character
        self.max_chars_per_line = 128 // self.char_width  # ~21 chars per line
        self.max_lines = 64 // self.line_height  # 8 lines total
        
        # Scrolling text buffer - stores lines to display
        self.text_buffer = deque(maxlen=100)  # Keep last 100 lines
        self.display_offset = 0  # For scrolling
        
    def clear_display(self):
        """Clear the OLED display."""
        with canvas(self.display) as draw:
            pass
    
    def wrap_text(self, text, prefix=""):
        """Wrap text to fit OLED display width."""
        # Add prefix to first line
        prefixed_text = prefix + text
        
        # Wrap text to fit display
        lines = []
        words = prefixed_text.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) <= self.max_chars_per_line:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    # Word is too long, break it
                    lines.append(word[:self.max_chars_per_line])
                    current_line = word[self.max_chars_per_line:]
        
        if current_line:
            lines.append(current_line)
            
        return lines
    
    def add_message(self, message, is_user=True):
        """Add a message to the text buffer with proper formatting."""
        prefix = "You: " if is_user else "Bot: "
        wrapped_lines = self.wrap_text(message, prefix)
        
        # Add wrapped lines to buffer
        for line in wrapped_lines:
            self.text_buffer.append(line)
        
        # Add empty line for separation
        self.text_buffer.append("")
        
        # Auto-scroll to bottom
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """Scroll to show the most recent messages."""
        if len(self.text_buffer) > self.max_lines:
            self.display_offset = len(self.text_buffer) - self.max_lines
        else:
            self.display_offset = 0
    
    def update_display(self):
        """Update the OLED display with current text buffer."""
        with canvas(self.display) as draw:
            # Get lines to display
            start_idx = self.display_offset
            end_idx = min(start_idx + self.max_lines, len(self.text_buffer))
            
            # Draw each line
            for i, line_idx in enumerate(range(start_idx, end_idx)):
                if line_idx < len(self.text_buffer):
                    y_pos = i * self.line_height
                    draw.text((0, y_pos), self.text_buffer[line_idx], fill=1)
    
    def show_message(self, message, duration=2):
        """Show a temporary message on the display."""
        with canvas(self.display) as draw:
            lines = self.wrap_text(message)
            for i, line in enumerate(lines[:self.max_lines]):
                y_pos = i * self.line_height
                draw.text((0, y_pos), line, fill=1)
        time.sleep(duration)
    
    def get_user_input(self):
        """Get user input from console (since OLED can't handle input)."""
        # Show input prompt on display
        self.show_message("Waiting for input...\nCheck console", 1)
        
        # Get input from console
        user_input = input("\nYou: ")
        return user_input
    
    def run(self):
        """Main chatbot loop."""
        print("OLED Chatbot started!")
        print("Output will be shown on OLED display.")
        print("Type 'exit' to quit, 'clear' to clear display.\n")
        
        # Show welcome message on OLED
        self.show_message("Rubik Pi Chatbot\nReady!\n\nType in console...", 3)
        self.clear_display()
        
        # Add initial message to buffer
        self.add_message("Welcome! Type 'exit' to quit.", False)
        self.update_display()
        
        while True:
            try:
                # Get user input
                user_input = self.get_user_input()
                print("")  # Console spacing
                
                if user_input.lower() == "exit":
                    self.show_message("Goodbye!\nThanks for chatting!", 2)
                    self.clear_display()
                    print("Goodbye!")
                    break
                
                if user_input.lower() == "clear":
                    self.text_buffer.clear()
                    self.display_offset = 0
                    self.add_message("Display cleared.", False)
                    self.update_display()
                    continue
                
                # Add user message to display
                self.add_message(user_input, True)
                self.update_display()
                
                # Add user message to chat history
                self.chat_history.append({"role": "user", "content": user_input})
                
                # Keep only the most recent 20 messages
                if len(self.chat_history) > 20:
                    self.chat_history = self.chat_history[-20:]
                
                # Show "thinking" message
                self.show_message("Bot is thinking...", 1)
                
                # Get response from API
                response = self.client.chat.completions.create(
                    model="Llama-4-Maverick-17B-128E-Instruct-FP8",
                    messages=self.chat_history,
                    max_completion_tokens=1024
                )
                
                # Get the response content
                assistant_response = response.choices[0].message.content
                
                # Add bot response to display
                self.add_message(assistant_response, False)
                self.update_display()
                
                # Also print to console for reference
                print(f"Bot: {assistant_response}\n")
                
                # Add assistant response to chat history
                self.chat_history.append({"role": "assistant", "content": assistant_response})
                
                # Keep only the most recent 20 messages after adding assistant response
                if len(self.chat_history) > 20:
                    self.chat_history = self.chat_history[-20:]
                    
            except KeyboardInterrupt:
                self.show_message("Interrupted!\nGoodbye!", 2)
                self.clear_display()
                print("\nChatbot interrupted. Goodbye!")
                break
            except Exception as e:
                error_msg = f"Error: {str(e)[:50]}..."
                self.add_message(error_msg, False)
                self.update_display()
                print(f"Error: {e}")
                time.sleep(2)

if __name__ == "__main__":
    chatbot = OLEDChatbot()
    chatbot.run()
