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
import re
from collections import deque
from openai import OpenAI

# Import OLED display functionality
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

class OLEDChatbot:
    def __init__(self, use_display=True):
        # Load configuration
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=config.get("LLAMA_API_KEY"),
            base_url="https://api.llama.com/compat/v1/",
        )
        self.chat_history = []
        
        # Display settings
        self.use_display = use_display
        
        if self.use_display:
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
            
    def clean_markdown_text(self, text):
        """Remove markdown formatting and preserve paragraph spacing."""
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Code
        text = re.sub(r'#{1,6}\s*(.*)', r'\1', text)  # Headers
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Links
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)  # Bullet points
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)  # Numbered lists
        
        # Convert double newlines to paragraph breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
        
    def clear_display(self):
        """Clear the OLED display."""
        if not self.use_display:
            return
        with canvas(self.display) as draw:
            pass
    
    def wrap_text(self, text, prefix=""):
        """Wrap text to fit OLED display width."""
        # Clean markdown first
        text = self.clean_markdown_text(text)
        
        # Add prefix to first line
        prefixed_text = prefix + text
        
        # Split into paragraphs and process
        paragraphs = prefixed_text.split('\n\n')
        all_lines = []
        
        for i, paragraph in enumerate(paragraphs):
            if i > 0:  # Add empty line between paragraphs
                all_lines.append("")
            
            # Wrap paragraph text to fit display
            words = paragraph.split()
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if len(test_line) <= self.max_chars_per_line:
                    current_line = test_line
                else:
                    if current_line:
                        all_lines.append(current_line)
                        current_line = word
                    else:
                        # Word is too long, break it
                        all_lines.append(word[:self.max_chars_per_line])
                        current_line = word[self.max_chars_per_line:]
            
            if current_line:
                all_lines.append(current_line)
                
        return all_lines
    
    def add_message(self, message, is_user=True):
        """Add a message to the text buffer with proper formatting."""
        if not self.use_display:
            return
        prefix = "You: " if is_user else "Bot: "
        wrapped_lines = self.wrap_text(message, prefix)
        
        # Add wrapped lines to buffer
        for line in wrapped_lines:
            self.text_buffer.append(line)
        
        # Add empty line for separation
        self.text_buffer.append("")
        
        # Auto-scroll to bottom
        self.scroll_to_bottom()
    
    def add_message_streaming(self, message, is_user=True, word_delay=0.4):
        """Add a message to the display with reading-pace streaming effect and Star Wars scrolling."""
        if not self.use_display:
            return
        prefix = "You: " if is_user else "Bot: "
        wrapped_lines = self.wrap_text(message, prefix)
        
        # If this is the start of a new conversation, clear the display
        if len(self.text_buffer) == 0:
            self.display_offset = 0
        
        # Add lines progressively with Star Wars-style scrolling
        for i, line in enumerate(wrapped_lines):
            self.text_buffer.append(line)
            
            # If we've exceeded the screen height, scroll up
            if len(self.text_buffer) > self.max_lines:
                self.display_offset = len(self.text_buffer) - self.max_lines
            
            self.update_display()
            time.sleep(word_delay)  # Pause between lines for reading
        
        # Add empty line for separation
        self.text_buffer.append("")
        
        # Adjust scrolling for the empty line
        if len(self.text_buffer) > self.max_lines:
            self.display_offset = len(self.text_buffer) - self.max_lines
            
        self.update_display()
    
    def scroll_to_bottom(self):
        """Scroll to show the most recent messages."""
        if not self.use_display:
            return
        if len(self.text_buffer) > self.max_lines:
            self.display_offset = len(self.text_buffer) - self.max_lines
        else:
            self.display_offset = 0
    
    def update_display(self):
        """Update the OLED display with current text buffer."""
        if not self.use_display:
            return
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
        if not self.use_display:
            return
        with canvas(self.display) as draw:
            lines = self.wrap_text(message)
            for i, line in enumerate(lines[:self.max_lines]):
                y_pos = i * self.line_height
                draw.text((0, y_pos), line, fill=1)
        time.sleep(duration)
    
    def get_user_input(self):
        """Get user input from console."""
        if self.use_display:
            # Show input prompt on display
            self.show_message("Waiting for input...\nCheck console", 1)
        
        # Get input from console
        user_input = input("\nYou: ")
        return user_input
    
    def run(self):
        """Main chatbot loop."""
        if self.use_display:
            print("OLED Chatbot started!")
            print("Output will be shown on OLED display.")
        else:
            print("Welcome to the Rubik Pi Chatbot!")
        print("Type 'exit' to quit, 'clear' to clear display.\n")
        
        if self.use_display:
            # Show welcome message on OLED
            self.show_message("Rubik Pi Chatbot\nReady!\n\nType in console...", 3)
            self.clear_display()
            
            # Add initial message to buffer with streaming
            self.add_message_streaming("Welcome! Type 'exit' to quit.", False, 0.27)
        
        while True:
            try:
                # Get user input
                user_input = self.get_user_input()
                print("")  # Console spacing
                
                if user_input.lower() == "exit":
                    if self.use_display:
                        self.show_message("Goodbye!\nThanks for chatting!", 2)
                        self.clear_display()
                    print("Goodbye!")
                    break
                
                if user_input.lower() == "clear":
                    if self.use_display:
                        self.text_buffer.clear()
                        self.display_offset = 0
                        self.update_display()  # Clear the display immediately
                        self.add_message_streaming("Display cleared.", False, 0.27)
                    continue
                
                # Add user message to display with streaming
                if self.use_display:
                    self.add_message_streaming(user_input, True, 0.27)  # Slower: 75% of 0.2 = ~0.27
                
                # Add user message to chat history
                self.chat_history.append({"role": "user", "content": user_input})
                
                # Keep only the most recent 20 messages
                if len(self.chat_history) > 20:
                    self.chat_history = self.chat_history[-20:]
                
                # Show "thinking" message
                if self.use_display:
                    self.show_message("Bot is thinking...", 1)
                
                # Get response from API
                response = self.client.chat.completions.create(
                    model="Llama-4-Maverick-17B-128E-Instruct-FP8",
                    messages=self.chat_history,
                    max_completion_tokens=1024
                )
                
                # Get the response content
                assistant_response = response.choices[0].message.content
                
                # Print full response to console first
                print(f"Llama: {assistant_response}\n")
                
                # Then add bot response to display with reading-pace streaming
                if self.use_display:
                    self.add_message_streaming(assistant_response, False, 0.53)  # Slower: 75% of 0.4 = ~0.53
                
                # Add assistant response to chat history
                self.chat_history.append({"role": "assistant", "content": assistant_response})
                
                # Keep only the most recent 20 messages after adding assistant response
                if len(self.chat_history) > 20:
                    self.chat_history = self.chat_history[-20:]
                    
            except KeyboardInterrupt:
                if self.use_display:
                    self.show_message("Interrupted!\nGoodbye!", 2)
                    self.clear_display()
                print("\nChatbot interrupted. Goodbye!")
                break
            except Exception as e:
                error_msg = f"Error: {str(e)[:50]}..."
                if self.use_display:
                    self.add_message(error_msg, False)
                    self.update_display()
                print(f"Error: {e}")
                time.sleep(2)

if __name__ == "__main__":
    import sys
    
    # Check for command line argument to disable display
    use_display = True
    if len(sys.argv) > 1 and sys.argv[1] == "--no-display":
        use_display = False
    
    chatbot = OLEDChatbot(use_display=use_display)
    chatbot.run()
