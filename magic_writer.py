#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import signal
import threading
import pyperclip
import google.generativeai as genai
from pynput import keyboard
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in environment variables")
    print("Please create a .env file with your API key or set it manually")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Global variables
SHORTCUT_KEY = keyboard.Key.f8  # Default shortcut key (can be changed)
processing_text = False
indicator_thread = None

def get_selected_text():
    """Get the currently selected text using xclip"""
    try:
        # Save current clipboard content
        old_clipboard = pyperclip.paste()

        # Copy selected text to clipboard
        subprocess.run(["xclip", "-selection", "primary", "-o"],
                      stdout=subprocess.PIPE,
                      text=True)

        # Get text from clipboard
        selected_text = pyperclip.paste()

        # Restore original clipboard content
        pyperclip.copy(old_clipboard)

        return selected_text
    except Exception as e:
        print(f"Error getting selected text: {e}")
        return None

def improve_text(text):
    """Send text to Gemini AI for improvement"""
    global processing_text

    if not text or len(text.strip()) == 0:
        print("No text selected")
        processing_text = False
        return None

    try:
        # Create prompt for Gemini
        prompt = f"""
        Please improve the following English text to make it more professional,
        clear, and grammatically correct. Maintain the original meaning and tone:

        "{text}"

        Respond ONLY with the improved text, no explanations.
        """

        # Get response from Gemini
        response = model.generate_content(prompt)
        improved_text = response.text.strip()

        # Sometimes Gemini might add quotes, let's remove them
        if improved_text.startswith('"') and improved_text.endswith('"'):
            improved_text = improved_text[1:-1]
        pyperclip.copy(improved_text)
        print("Just after copy")
        return improved_text
    except Exception as e:
        print(f"Error improving text with Gemini: {e}")
        return None
    finally:
        processing_text = False

def process_selected_text():
    """Process the selected text and replace it with improved version"""
    global processing_text

    if processing_text:
        return

    processing_text = True

    # Indicate processing is happening
    start_processing_indicator()

    # Get selected text
    original_text = get_selected_text()
    if not original_text:
        processing_text = False
        stop_processing_indicator()
        return

    # Improve text using Gemini
    improved_text = improve_text(original_text)
    if not improved_text:
        processing_text = False
        stop_processing_indicator()
        return

    # Copy improved text to clipboard
    pyperclip.copy(improved_text)

    # Notify user
    subprocess.run(["notify-send", "Magic Writer", "Text improved and copied to clipboard!"])
    print(f"Original: {original_text}")
    print(f"Improved: {improved_text}")

    stop_processing_indicator()

def start_processing_indicator():
    """Show a processing indicator in the terminal"""
    global indicator_thread

    def animate():
        chars = "/—\\|"
        i = 0
        while processing_text:
            sys.stdout.write(f'\rProcessing text with Gemini AI {chars[i % len(chars)]}')
            sys.stdout.flush()
            i += 1
            time.sleep(0.1)
        sys.stdout.write('\rProcessing complete!           \n')

    indicator_thread = threading.Thread(target=animate)
    indicator_thread.daemon = True
    indicator_thread.start()

def stop_processing_indicator():
    """Stop the processing indicator"""
    global indicator_thread
    if indicator_thread:
        indicator_thread.join(0.5)

def on_key_press(key):
    """Handle key press events"""
    if key == SHORTCUT_KEY and not processing_text:
        threading.Thread(target=process_selected_text).start()

def setup_listener():
    """Set up keyboard listener"""
    listener = keyboard.Listener(on_press=on_key_press)
    listener.start()
    return listener

def signal_handler(sig, frame):
    """Handle exit signals"""
    print("\nExiting Magic Writer...")
    sys.exit(0)

if __name__ == "__main__":
    print("Starting Magic Writer...")
    print(f"Press {SHORTCUT_KEY} to improve selected text")
    print("Ctrl+C to exit")

    # Set up signal handling for clean exit
    signal.signal(signal.SIGINT, signal_handler)

    # Start keyboard listener
    listener = setup_listener()

    try:
        # Keep the program running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting Magic Writer...")
        sys.exit(0)