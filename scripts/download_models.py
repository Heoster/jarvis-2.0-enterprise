"""Download required models for the assistant."""

import sys
import subprocess


def download_spacy_model():
    """Download spaCy model."""
    print("Downloading spaCy model...")
    try:
        subprocess.run([
            sys.executable, "-m", "spacy", "download", "en_core_web_sm"
        ], check=True)
        print("✓ spaCy model downloaded")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to download spaCy model: {e}")


def download_nltk_data():
    """Download NLTK data."""
    print("Downloading NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✓ NLTK data downloaded")
    except Exception as e:
        print(f"✗ Failed to download NLTK data: {e}")


def check_ollama():
    """Check if Ollama is installed."""
    print("Checking Ollama installation...")
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Ollama is installed")
            print("\nInstalled models:")
            print(result.stdout)
            
            print("\nTo download required models, run:")
            print("  ollama pull llama3.2:1b-instruct-q8_0")
            print("  ollama pull llama3.2:3b-instruct-q4_0")
            print("  ollama pull codellama:7b-instruct-q4_0")
        else:
            print("✗ Ollama not found")
            print("Install from: https://ollama.ai/")
    except FileNotFoundError:
        print("✗ Ollama not found")
        print("Install from: https://ollama.ai/")


def main():
    """Download all required models."""
    print("=" * 50)
    print("On-Device Assistant - Model Download")
    print("=" * 50)
    print()
    
    download_spacy_model()
    print()
    
    download_nltk_data()
    print()
    
    check_ollama()
    print()
    
    print("=" * 50)
    print("Setup complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
