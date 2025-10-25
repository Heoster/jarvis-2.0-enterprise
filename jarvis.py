#!/usr/bin/env python
"""
JARVIS Complete - Main Entry Point
Unified system combining Original JARVIS + JARVIS 2.0 Enhancements

Usage:
    python jarvis.py              # Run interactive mode with all features
    python jarvis.py --simple     # Run simple demo mode
    python jarvis.py --original   # Run original JARVIS only
    python jarvis.py --test       # Run integration tests
"""

import sys
import asyncio
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="JARVIS Complete - Unified AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python jarvis.py                 # Full system with all features
  python jarvis.py --simple        # Simple demo (no heavy models)
  python jarvis.py --original      # Original JARVIS only
  python jarvis.py --test          # Run integration tests
  python jarvis.py --help          # Show this help
        """
    )
    
    parser.add_argument(
        '--simple',
        action='store_true',
        help='Run simple demo mode (lightweight, no heavy models)'
    )
    
    parser.add_argument(
        '--original',
        action='store_true',
        help='Run original JARVIS only (disable enhancements)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run integration tests'
    )
    
    parser.add_argument(
        '--enhanced-only',
        action='store_true',
        help='Run JARVIS 2.0 enhancements only (demo mode)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.test:
            # Run integration tests
            print("🧪 Running integration tests...")
            import subprocess
            result = subprocess.run([sys.executable, "test_integration.py"])
            sys.exit(result.returncode)
        
        elif args.simple:
            # Run simple demo
            print("🤖 Starting JARVIS Simple Demo...")
            import subprocess
            result = subprocess.run([sys.executable, "run_jarvis_simple.py"])
            sys.exit(result.returncode)
        
        elif args.enhanced_only:
            # Run enhanced features only
            print("✨ Starting JARVIS 2.0 Enhanced Demo...")
            import subprocess
            result = subprocess.run([sys.executable, "run_jarvis_enhanced.py"])
            sys.exit(result.returncode)
        
        elif args.original:
            # Run original JARVIS
            print("🤖 Starting Original JARVIS...")
            import subprocess
            result = subprocess.run([sys.executable, "-m", "core.main", "start", "--no-unified"])
            sys.exit(result.returncode)
        
        else:
            # Run complete unified system
            print("🚀 Starting JARVIS Complete - Unified System...")
            import subprocess
            result = subprocess.run([sys.executable, "run_jarvis_complete.py"])
            sys.exit(result.returncode)
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
