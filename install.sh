#!/bin/bash

echo "Installing Magic Writer..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip is not installed. Please install pip and try again."
    exit 1
fi

# Install xclip and xsel if not already installed
if ! command -v xclip &> /dev/null || ! command -v xsel &> /dev/null; then
    echo "xclip or xsel not found. Attempting to install..."

    # Try to detect package manager
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y xclip xsel
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm xclip xsel
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y xclip xsel
    elif command -v yum &> /dev/null; then
        sudo yum install -y xclip xsel
    else
        echo "Warning: Could not automatically install clipboard utilities. Please install xclip and xsel manually."
    fi
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Make script executable
chmod +x magic_writer.py

# Set up desktop entry
echo "Setting up desktop entry..."
mkdir -p ~/.local/share/applications
cp magic-writer.desktop ~/.local/share/applications/

# Prompt for API key if not set
if [ ! -f .env ]; then
    echo "Please enter your Gemini API key (get one from https://makersuite.google.com/app/apikey):"
    read api_key
    echo "GEMINI_API_KEY=$api_key" > .env
    echo "API key saved to .env file"
fi

echo "Installation complete!"
echo "To start Magic Writer, run: python3 magic_writer.py"
echo "Or search for 'Magic Writer' in your applications menu."
echo ""
echo "Would you like to start Magic Writer now? (y/n)"
read start_now

if [[ $start_now == "y" || $start_now == "Y" ]]; then
    python3 magic_writer.py
fi