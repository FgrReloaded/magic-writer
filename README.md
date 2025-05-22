# Magic Writer

An AI-powered text enhancement tool for Linux that helps improve your English writing by leveraging Google's Gemini AI.

## Features

- Runs in the background
- Activates via keyboard shortcut (F8 by default)
- Improves selected text and copies it to clipboard
- Shows desktop notifications when processing is complete

## Requirements

- Linux with X11 (Wayland support may vary)
- Python 3.6+
- xclip utility
- Google Gemini API key (free)

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/magic-writer.git
cd magic-writer
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. Install xclip if not already installed:

```bash
sudo apt install xclip    # Debian/Ubuntu
# or
sudo pacman -S xclip     # Arch Linux
# or
sudo dnf install xclip   # Fedora
```

4. Get your Gemini API key:

   - Go to https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy the API key

5. Create a `.env` file with your API key:

```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

6. Make the script executable:

```bash
chmod +x magic_writer.py
```

## Usage

1. Start the application:

```bash
python3 magic_writer.py
```

2. Use the tool:

   - Select text in any application
   - Press F8
   - Wait for processing (you'll see a notification)
   - The improved text is now in your clipboard - paste it wherever you need

3. To change the shortcut key, edit the `SHORTCUT_KEY` variable in `magic_writer.py`

## Autostart

To make Magic Writer start automatically with your system:

1. Copy the desktop file to your applications directory:

```bash
cp magic-writer.desktop ~/.local/share/applications/
```

2. Add to startup applications in your desktop environment settings

## Troubleshooting

- If you get permission errors when accessing the keyboard, you may need to run the script with sudo or adjust permissions.
- If xclip fails to get selected text, try using a different clipboard tool or check if xclip is installed correctly.

### Clipboard Issues

If you're experiencing issues with text not being copied to clipboard:

1. Make sure both xclip and xsel are installed:

```bash
sudo apt install xclip xsel  # for Debian/Ubuntu
```

2. Try running the script in a terminal to see any error messages.

3. If issues persist, you can manually modify the script to use a different clipboard method by editing the `process_selected_text` function in `magic_writer.py`.

4. For Wayland users: The clipboard functionality may be limited. Consider using X11 or searching for Wayland-specific clipboard utilities.

## License

MIT
