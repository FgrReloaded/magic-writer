import os
import sys
import time
import subprocess
import signal
import threading
import google.generativeai as genai
from pynput import keyboard
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in environment variables")
    print("Please create a .env file with your API key or set it manually")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

SHORTCUT_KEY = keyboard.Key.f8
processing_text = False
indicator_thread = None

def get_selected_text():
    """Get the currently selected text using xclip"""
    try:
        result = subprocess.run(['xclip', '-selection', 'primary', '-o'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         text=True)

        if result.returncode != 0:
            print(f"Error getting selected text: {result.stderr}")
            return None

        return result.stdout
    except Exception as e:
        print(f"Error getting selected text: {e}")
        return None

def copy_text_to_clipboard(text):
    """
    Attempt to copy text to clipboard using multiple methods
    Returns True if at least one method succeeds
    """
    if not text:
        return False

    success = False

    try:
        process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
        process.communicate(input=text.encode('utf-8'))
        print("Method 1: Text copied to clipboard selection")
        success = True
    except Exception as e:
        print(f"Method 1 failed: {e}")

    try:
        process = subprocess.Popen(['xclip', '-selection', 'primary'], stdin=subprocess.PIPE)
        process.communicate(input=text.encode('utf-8'))
        print("Method 2: Text copied to primary selection")
        success = True
    except Exception as e:
        print(f"Method 2 failed: {e}")

    try:
        process = subprocess.Popen(['xsel', '--input', '--clipboard'], stdin=subprocess.PIPE)
        process.communicate(input=text.encode('utf-8'))
        print("Method 3: Text copied using xsel")
        success = True
    except Exception as e:
        print(f"Method 3 failed: {e}")

    try:
        process = subprocess.Popen(['wl-copy'], stdin=subprocess.PIPE)
        process.communicate(input=text.encode('utf-8'))
        print("Method 4: Text copied using wl-copy")
        success = True
    except Exception as e:
        print(f"Method 4 failed: {e}")

    if not success:
        try:
            temp_file = '/tmp/magic_writer_clipboard.txt'
            with open(temp_file, 'w') as f:
                f.write(text)

            subprocess.run(f"cat {temp_file} | xclip -selection clipboard", shell=True)
            subprocess.run(f"cat {temp_file} | xsel --input --clipboard", shell=True, stderr=subprocess.DEVNULL)

            print("Method 5: Text copied using file-based method")
            success = True
        except Exception as e:
            print(f"Method 5 failed: {e}")

    return success

def improve_text(text):
    """Send text to Gemini AI for improvement"""
    global processing_text

    if not text or len(text.strip()) == 0:
        print("No text selected")
        processing_text = False
        return None

    try:
        prompt = f"""
        Please improve the following English text to make it more professional,
        clear, and grammatically correct. Maintain the original meaning and tone:

        "{text}"

        Respond ONLY with the improved text, no explanations.
        """

        response = model.generate_content(prompt)
        improved_text = response.text.strip()

        if improved_text.startswith('"') and improved_text.endswith('"'):
            improved_text = improved_text[1:-1]

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

    start_processing_indicator()

    original_text = get_selected_text()
    if not original_text or len(original_text.strip()) == 0:
        print("No text selected")
        processing_text = False
        stop_processing_indicator()
        subprocess.run(["notify-send", "Magic Writer", "No text selected!"])
        return

    print(f"Selected text: {original_text}")

    improved_text = improve_text(original_text)
    if not improved_text:
        processing_text = False
        stop_processing_indicator()
        return

    clipboard_success = copy_text_to_clipboard(improved_text)

    try:
        with open('/tmp/last_improved_text.txt', 'w') as f:
            f.write(improved_text)
        print("Text saved to /tmp/last_improved_text.txt as backup")
    except Exception as e:
        print(f"Failed to save backup file: {e}")

    print(f"Clipboard operation success: {clipboard_success}")
    print(f"Original: {original_text}")
    print(f"Improved: {improved_text}")

    if clipboard_success:
        subprocess.run(["notify-send", "Magic Writer", "Text improved and copied to clipboard!"])
    else:
        subprocess.run(["notify-send", "Magic Writer",
                      "Text improved but clipboard failed. Saved to /tmp/last_improved_text.txt"])

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

    signal.signal(signal.SIGINT, signal_handler)

    listener = setup_listener()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting Magic Writer...")
        sys.exit(0)