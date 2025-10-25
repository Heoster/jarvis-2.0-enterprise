#!/usr/bin/env python3
"""
Simple launcher for JARVIS MASTER
Quick and easy way to start your AI assistant
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗    ███╗   ███╗ █████╗ ███████╗  ║
║     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝    ████╗ ████║██╔══██╗██╔════╝  ║
║     ██║███████║██████╔╝██║   ██║██║███████╗    ██╔████╔██║███████║███████╗  ║
║██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║    ██║╚██╔╝██║██╔══██║╚════██║  ║
║╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║    ██║ ╚═╝ ██║██║  ██║███████║  ║
║ ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝  ║
║                                                                               ║
║                    Complete AI Assistant - Fully Operational                 ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝

🤖 JARVIS MASTER - Your Personal AI Assistant
   Developed by Codeex AI Company for Heoster

📦 Features:
   ✅ Advanced Web Search & Scraping (DuckDuckGo)
   ✅ Real-time Data (Weather, News, Wikipedia)
   ✅ Indian APIs (Finance INR, Railway, Mutual Funds)
   ✅ Entertainment (Jokes, Quotes, Images)
   ✅ Transformers + LangChain AI
   ✅ Natural Language Understanding
   ✅ Contextual Memory & Learning

🚀 Starting JARVIS MASTER...
""")

# Check Python version
if sys.version_info < (3, 8):
    print("❌ Error: Python 3.8 or higher is required")
    print(f"   Current version: {sys.version}")
    sys.exit(1)

# Check for required packages
try:
    import aiohttp
    import beautifulsoup4
except ImportError as e:
    print(f"⚠️  Warning: Some packages may be missing: {e}")
    print("   Run: pip install -r requirements.txt")
    print()

# Import and run
try:
    from jarvis_master import main
    main()
except ImportError as e:
    print(f"❌ Error importing JARVIS MASTER: {e}")
    print()
    print("Make sure you're in the correct directory and all files are present.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting JARVIS MASTER: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
