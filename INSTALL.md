# Installation Guide - On-Device Assistant

Complete installation guide for the On-Device Assistant with all features.

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 11+
- **Python**: 3.9 or higher
- **RAM**: 8GB minimum
- **Storage**: 5GB free space
- **CPU**: Multi-core processor recommended

### Recommended Requirements
- **RAM**: 16GB or more
- **GPU**: NVIDIA GPU with CUDA support (optional, for faster processing)
- **Storage**: 10GB+ free space

## Installation Steps

### 1. Install Python

#### Windows
Download from https://www.python.org/downloads/
- Check "Add Python to PATH" during installation

#### Linux
```bash
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip
```

#### macOS
```bash
brew install python@3.9
```

### 2. Clone Repository

```bash
git clone <repository-url>
cd on-device-assistant
```

### 3. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### 4. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Optional: Install development dependencies
pip install -r requirements-optional.txt
```

### 5. Download NLP Models

```bash
# Download spaCy model
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"
```

### 6. Initialize Databases

```bash
# Create data directories and initialize databases
python scripts/init_db.py
```

### 7. Configure Environment (Optional)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys and preferences
# nano .env  # Linux/Mac
# notepad .env  # Windows
```

## Optional: Google Cloud Setup

For Dialogflow and Google Speech services:

### 1. Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable the following APIs:
   - Dialogflow API
   - Cloud Speech-to-Text API
   - Cloud Text-to-Speech API

### 2. Create Service Account

1. Go to IAM & Admin > Service Accounts
2. Create a new service account
3. Grant roles:
   - Dialogflow API Client
   - Cloud Speech Client
   - Cloud Text-to-Speech Client
4. Create and download JSON key

### 3. Configure Credentials

```bash
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Or add to .env file
echo "GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json" >> .env
echo "DIALOGFLOW_PROJECT_ID=your-project-id" >> .env
```

### 4. Enable Dialogflow

In `.env`:
```bash
ASSISTANT_MODELS__AI__USE_DIALOGFLOW=true
ASSISTANT_MODELS__AI__DIALOGFLOW_PROJECT_ID=your-project-id
```

## Optional: API Keys

### OpenWeatherMap (Weather Data)

1. Sign up at https://openweathermap.org/api
2. Get your API key
3. Add to `.env`:
```bash
OPENWEATHER_API_KEY=your-api-key
ASSISTANT_APIS__WEATHER__ENABLED=true
```

### NewsAPI (News Headlines)

1. Sign up at https://newsapi.org/
2. Get your API key
3. Add to `.env`:
```bash
NEWS_API_KEY=your-api-key
ASSISTANT_APIS__NEWS__ENABLED=true
```

## Verification

### Test Installation

```bash
# Run validation script
python validate_setup.py

# Check system status
python -m core.main status
```

### Test Components

```bash
# Test NLP
python -c "from core.nlp import NLPEngine; print('NLP OK')"

# Test AI client
python -c "from core.ai_client import AIClient; print('AI OK')"

# Test vision
python -c "from core.vision import VisionEngine; print('Vision OK')"

# Test real-time data
python -c "from core.realtime_data import RealTimeDataManager; print('Data OK')"
```

### Run Interactive Mode

```bash
python -m core.main start
```

Try these test queries:
- "What is 2 + 2?"
- "Tell me about Python"
- "What's the weather?" (if API key configured)
- "Latest news" (if API key configured)

## Platform-Specific Notes

### Windows

#### Install Visual C++ Build Tools
Some packages require compilation:
1. Download from https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install "Desktop development with C++"

#### PyAudio Installation
```bash
pip install pipwin
pipwin install pyaudio
```

### Linux

#### Install System Dependencies
```bash
# Ubuntu/Debian
sudo apt install -y \
    python3-dev \
    build-essential \
    portaudio19-dev \
    libsndfile1 \
    ffmpeg

# Fedora/RHEL
sudo dnf install -y \
    python3-devel \
    gcc \
    portaudio-devel \
    libsndfile \
    ffmpeg
```

### macOS

#### Install Homebrew Dependencies
```bash
brew install portaudio ffmpeg
```

## Troubleshooting

### Import Errors

```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### OpenCV Issues

```bash
# Reinstall OpenCV
pip uninstall opencv-python opencv-contrib-python -y
pip install opencv-python opencv-contrib-python
```

### Google Cloud Authentication

```bash
# Test authentication
gcloud auth application-default login

# Verify credentials
python -c "from google.cloud import dialogflow; print('Auth OK')"
```

### Database Errors

```bash
# Remove old databases
rm -rf data/*.db data/*.index

# Reinitialize
python scripts/init_db.py
```

### Permission Errors (Linux/Mac)

```bash
# Make scripts executable
chmod +x scripts/*.py

# Fix data directory permissions
chmod -R 755 data/
```

## Uninstallation

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv/

# Remove data (optional)
rm -rf data/

# Remove downloaded models (optional)
rm -rf models/
```

## Next Steps

After installation:

1. Read [QUICKSTART.md](QUICKSTART.md) for usage examples
2. Read [README.md](README.md) for feature overview
3. Configure API keys for full functionality
4. Customize `config/default.yaml` for your needs

## Getting Help

- Check [README.md](README.md) for common issues
- Review logs in `data/logs/assistant.log`
- Open an issue on GitHub
- Check documentation at [repository-url]/docs

---

**Installation complete!** Start using the assistant with:
```bash
python -m core.main start
```
