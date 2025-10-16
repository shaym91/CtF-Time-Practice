#!/bin/bash

echo "============================================================"
echo "🎯 CTF COMPETITION 2024 - LINUX/WSL STARTUP"
echo "============================================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python 3.7+"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

echo "✅ Python3 found!"
echo

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install flask pytz
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies!"
    echo "Try: pip3 install -r requirements.txt"
    exit 1
fi

echo "✅ Dependencies installed!"
echo

# Start the server
echo "🚀 Starting CTF Platform..."
echo "🌐 Server will be available at: http://localhost:5000"
echo "⏰ Competition Time: 5 PM - 5 AM (Bangladesh Time)"
echo "🎯 18 INSANE Challenges Ready!"
echo
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo

python3 run.py
