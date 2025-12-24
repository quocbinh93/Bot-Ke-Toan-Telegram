#!/bin/bash

echo "========================================"
echo "  Telegram Accounting Bot Launcher"
echo "========================================"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[*] Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "[+] Virtual environment created"
fi

# Activate virtual environment
echo "[*] Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
echo "[*] Checking dependencies..."
if ! pip show aiogram > /dev/null 2>&1; then
    echo "[*] Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo
    echo "[!] WARNING: .env file not found!"
    echo "[!] Please copy .env.example to .env and fill in your API keys"
    echo
    exit 1
fi

# Run the bot
echo
echo "[+] Starting bot..."
echo
python main.py
