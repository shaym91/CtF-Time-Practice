#!/usr/bin/env python3
"""
CTF Platform Runner - Handles errors and starts the server
"""

import sys
import traceback
import os
from datetime import datetime

def main():
    """Main runner function with error handling"""
    print("=" * 60)
    print("🎯 CTF COMPETITION 2024 - PLATFORM STARTUP")
    print("=" * 60)
    print(f"⏰ Current Time: {datetime.now()}")
    print(f"📍 Working Directory: {os.getcwd()}")
    print("=" * 60)
    
    try:
        # Import and start the Flask app
        from app import app
        
        print("✅ Flask app imported successfully!")
        print("🚀 Starting CTF Platform Server...")
        print("🌐 Server URL: http://localhost:5000")
        print("⏰ Competition: 5 PM - 5 AM (Bangladesh Time)")
        print("🎯 Challenges: 18 INSANE Level")
        print("=" * 60)
        
        # Get port from environment or use default
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        # Start the server
        app.run(host=host, port=port, debug=True, use_reloader=False)
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Solution: Install dependencies with:")
        print("   pip install flask pytz")
        print("   or")
        print("   pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Server Error: {e}")
        print("🔍 Full Error Details:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Server failed to start!")
        sys.exit(1)
    else:
        print("\n✅ Server started successfully!")
