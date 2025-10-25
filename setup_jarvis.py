#!/usr/bin/env python3
"""
JARVIS MASTER Setup Script
Checks dependencies and prepares the system
"""

import sys
import subprocess
import os

print("="*80)
print("🔧 JARVIS MASTER - Setup & Dependency Check")
print("="*80)
print()

def check_python_version():
    """Check Python version"""
    print("1. Checking Python version...")
    version = sys.version_info
    
    if version >= (3, 8):
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro}")
        print("   Error: Python 3.8 or higher required")
        return False


def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def check_dependencies():
    """Check critical dependencies"""
    print("\n2. Checking critical dependencies...")
    
    critical_packages = {
        'aiohttp': 'aiohttp',
        'beautifulsoup4': 'bs4',
        'transformers': 'transformers',
        'langchain': 'langchain',
        'spacy': 'spacy',
    }
    
    missing = []
    
    for package, import_name in critical_packages.items():
        if check_package(package, import_name):
            print(f"   ✅ {package}")
        else:
            print(f"   ❌ {package} (missing)")
            missing.append(package)
    
    return missing


def check_optional_dependencies():
    """Check optional dependencies"""
    print("\n3. Checking optional dependencies...")
    
    optional_packages = {
        'wikipedia': 'wikipedia',
        'duckduckgo-search': 'duckduckgo_search',
        'torch': 'torch',
    }
    
    for package, import_name in optional_packages.items():
        if check_package(package, import_name):
            print(f"   ✅ {package}")
        else:
            print(f"   ⚠️  {package} (optional, but recommended)")


def check_spacy_model():
    """Check if spaCy model is downloaded"""
    print("\n4. Checking spaCy language model...")
    
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            print("   ✅ en_core_web_sm model installed")
            return True
        except OSError:
            print("   ❌ en_core_web_sm model not found")
            return False
    except ImportError:
        print("   ⚠️  spaCy not installed")
        return False


def install_dependencies():
    """Install missing dependencies"""
    print("\n5. Installing dependencies...")
    
    try:
        print("   Running: pip install -r requirements.txt")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("   ✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Installation failed: {e}")
        return False


def install_spacy_model():
    """Install spaCy language model"""
    print("\n6. Installing spaCy language model...")
    
    try:
        print("   Running: python -m spacy download en_core_web_sm")
        subprocess.check_call([
            sys.executable, "-m", "spacy", "download", "en_core_web_sm"
        ])
        print("   ✅ spaCy model installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Installation failed: {e}")
        return False


def check_config():
    """Check configuration files"""
    print("\n7. Checking configuration...")
    
    config_files = [
        'config/config.yaml',
        '.env.example'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"   ✅ {config_file}")
        else:
            print(f"   ⚠️  {config_file} (not found, using defaults)")
    
    # Check if .env exists
    if os.path.exists('.env'):
        print("   ✅ .env file found")
    else:
        print("   ℹ️  .env file not found (optional)")
        print("      Most features work without API keys!")


def create_directories():
    """Create necessary directories"""
    print("\n8. Creating directories...")
    
    directories = [
        'logs',
        'data',
        'storage',
        'cache'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"   ✅ Created {directory}/")
        else:
            print(f"   ✅ {directory}/ exists")


def main():
    """Main setup function"""
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python version too old")
        return False
    
    # Check dependencies
    missing = check_dependencies()
    
    # Check optional dependencies
    check_optional_dependencies()
    
    # Check spaCy model
    spacy_model_missing = not check_spacy_model()
    
    # Check config
    check_config()
    
    # Create directories
    create_directories()
    
    # Offer to install missing packages
    if missing or spacy_model_missing:
        print("\n" + "="*80)
        print("⚠️  Some dependencies are missing")
        print("="*80)
        
        if missing:
            print(f"\nMissing packages: {', '.join(missing)}")
        
        if spacy_model_missing:
            print("\nMissing spaCy model: en_core_web_sm")
        
        response = input("\nWould you like to install them now? (y/n): ").strip().lower()
        
        if response == 'y':
            if missing:
                if not install_dependencies():
                    print("\n❌ Setup incomplete")
                    return False
            
            if spacy_model_missing:
                if not install_spacy_model():
                    print("\n⚠️  spaCy model installation failed")
                    print("   You can install it manually: python -m spacy download en_core_web_sm")
        else:
            print("\n⚠️  Setup incomplete. Install dependencies manually:")
            print("   pip install -r requirements.txt")
            if spacy_model_missing:
                print("   python -m spacy download en_core_web_sm")
            return False
    
    # Final check
    print("\n" + "="*80)
    print("✅ SETUP COMPLETE!")
    print("="*80)
    print()
    print("🚀 You can now start JARVIS MASTER:")
    print()
    print("   python start_jarvis.py")
    print()
    print("   or")
    print()
    print("   python jarvis_master.py")
    print()
    print("📚 For more information, see JARVIS_COMPLETE_GUIDE.md")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
