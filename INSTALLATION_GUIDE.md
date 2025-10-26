# 🛠️ Jarvis AI - Complete Installation Guide

**Step-by-step guide to install and configure your personal AI assistant**

---

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 11+
- **Python**: 3.9 or higher
- **RAM**: 8GB minimum
- **Storage**: 5GB free space
- **Internet**: Required for real-time features

### Recommended Requirements
- **RAM**: 16GB or more
- **CPU**: Multi-core processor (Intel i5/AMD Ryzen 5 or better)
- **Storage**: 10GB+ free space
- **GPU**: Optional, for faster AI processing

---

## ⚡ Quick Installation (5 Minutes)

### Step 1: Install Python
Make sure you have Python 3.9 or higher:

```bash
# Check Python version
python --version

# Should show Python 3.9.x or higher
```

**If you need to install Python:**
- **Windows**: Download from https://python.org/downloads/
- **Linux**: `sudo apt install python3.9 python3.9-venv python3-pip`
- **macOS**: `brew install python@3.9`

### Step 2: Clone Repository
```bash
git clone <repository-url>
cd on-device-assistant
```

### Step 3: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Step 5: Initialize System
```bash
# Initialize databases and create directories
python scripts/init_db.py
```

### Step 6: Test Installation
```bash
# Quick test
python -m core.main status

# Should show: "System Status: Operational"
```

### Step 7: Start Jarvis
```bash
python -m core.main start
```

**Congratulations! Jarvis is now running!** 🎉

---

## 🔧 Detailed Installation

### Platform-Specific Setup

#### Windows Installation
```bash
# Install Visual C++ Build Tools (if needed)
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Install Python packages
pip install -r requirements.txt

# Install PyAudio (if needed for voice features)
pip install pipwin
pipwin install pyaudio
```

#### Linux Installation (Ubuntu/Debian)
```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3-dev build-essential portaudio19-dev libsndfile1 ffmpeg

# Install Python packages
pip install -r requirements.txt
```

#### macOS Installation
```bash
# Install Homebrew dependencies
brew install portaudio ffmpeg

# Install Python packages
pip install -r requirements.txt
```

---

## 🔑 API Keys Configuration (Optional)

Most features work without API keys, but you can enhance functionality:

### Step 1: Create .env File
```bash
# Copy example file
cp .env.example .env

# Edit with your preferred editor
nano .env  # Linux/Mac
notepad .env  # Windows
```

### Step 2: Add API Keys

#### Weather Data (Free)
1. Visit: https://openweathermap.org/api
2. Sign up for free account
3. Get your API key
4. Add to `.env`:
```bash
OPENWEATHER_API_KEY=your_api_key_here
```

#### News Headlines (Free)
1. Visit: https://newsapi.org/
2. Sign up for free account (100 requests/day)
3. Get your API key
4. Add to `.env`:
```bash
NEWS_API_KEY=your_api_key_here
```

#### Google Cloud (Optional)
For advanced AI features:
1. Create Google Cloud project
2. Enable Dialogflow API
3. Create service account
4. Download credentials JSON
5. Add to `.env`:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
DIALOGFLOW_PROJECT_ID=your_project_id
```

### Step 3: Test API Configuration
```bash
# Test weather API
python -c "from core.realtime_data import RealTimeDataManager; import asyncio; print(asyncio.run(RealTimeDataManager().get_weather('London')))"

# Test news API
python -c "from core.realtime_data import RealTimeDataManager; import asyncio; print(asyncio.run(RealTimeDataManager().get_news()))"
```

---

## 📁 Directory Structure

After installation, your directory should look like:

```
on-device-assistant/
├── core/                     # Core AI modules
├── storage/                  # Database and memory
├── execution/                # Action executors
├── server/                   # API server
├── monitoring/               # Security and logging
├── voice/                    # Voice I/O (placeholder)
├── examples/                 # Demo applications
├── tests/                    # Test suite
├── scripts/                  # Utility scripts
├── docs/                     # Documentation
├── data/                     # Generated databases
├── models/                   # Downloaded AI models
├── config/                   # Configuration files
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
└── README.md                 # Main documentation
```

---

## 🧪 Verification & Testing

### Basic Functionality Test
```bash
# Test system status
python -m core.main status

# Test single query
python -m core.main query --query "Hello Jarvis"

# Test interactive mode (Ctrl+C to exit)
python -m core.main start
```

### Comprehensive Test Suite
```bash
# Run all tests
python test_jarvis_complete.py

# Run specific test categories
python -m pytest tests/test_jarvis_enhanced.py -v
python -m pytest tests/test_api_routing.py -v

# Run demo applications
python examples/jarvis_enhanced_demo.py
python examples/codeex_demo.py
```

### Feature-Specific Tests
```bash
# Test web scraping
python test_web_search.py

# Test student features
python examples/codeex_demo.py

# Test API server
python -m core.main server
# Visit http://localhost:8000/docs
```

---

## 🎛️ Configuration Options

### Basic Configuration (config/default.yaml)
```yaml
assistant:
  name: "Jarvis"
  owner: "Heoster"
  personality: "professional"  # or "magical"
  language: "en"

models:
  ai:
    use_dialogflow: false
    use_local: true
    model_name: "blenderbot"

apis:
  weather:
    enabled: true
    default_location: "Muzaffarnagar"
  news:
    enabled: true
    country: "in"
  search:
    enabled: true
    cache_duration: 3600

features:
  web_scraping: true
  student_features: true
  indian_apis: true
  voice_io: false
```

### Environment Variables (.env)
```bash
# Personal Identity
JARVIS_OWNER=Heoster
JARVIS_COMPANY="Codeex AI"
JARVIS_VERSION=1.0.0

# API Keys (optional)
OPENWEATHER_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
RAILWAY_API_KEY=your_key_here

# Google Cloud (optional)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
DIALOGFLOW_PROJECT_ID=your_project_id

# Feature Toggles
ENABLE_WEB_SCRAPING=true
ENABLE_STUDENT_FEATURES=true
PERSONALITY_STYLE=professional

# Performance
WEB_SCRAPER_CACHE_DURATION=3600
MAX_CONCURRENT_REQUESTS=5
```

---

## 🚀 Startup Options

### Interactive CLI Mode (Default)
```bash
python -m core.main start
```
- Natural conversation interface
- All features available
- Real-time interaction

### API Server Mode
```bash
python -m core.main server --port 8000
```
- REST API at http://localhost:8000
- WebSocket support
- API documentation at /docs

### Single Query Mode
```bash
python -m core.main query --query "What is machine learning?"
```
- One-off queries
- Scriptable interface
- Automation friendly

### Status Check
```bash
python -m core.main status
```
- System health check
- Feature availability
- Configuration summary

---

## 🐛 Troubleshooting

### Common Installation Issues

#### "spaCy model not found"
```bash
python -m spacy download en_core_web_sm
```

#### "Microsoft Visual C++ 14.0 is required" (Windows)
1. Download Visual Studio Build Tools
2. Install "Desktop development with C++"
3. Restart and try again

#### "No module named 'core'"
```bash
# Make sure you're in the right directory
cd on-device-assistant

# Reinstall dependencies
pip install -r requirements.txt
```

#### "Permission denied" (Linux/Mac)
```bash
# Fix permissions
chmod +x scripts/*.py
sudo chown -R $USER:$USER data/
```

#### "Port already in use"
```bash
# Use different port
python -m core.main server --port 8001

# Or kill existing process
lsof -ti:8000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :8000   # Windows
```

### Performance Issues

#### Slow startup
- **Normal**: First run loads models (10-15 seconds)
- **Solution**: Subsequent runs are faster
- **Alternative**: Use `python jarvis.py --simple` for instant startup

#### High memory usage
- **Expected**: 1-2GB with all models loaded
- **Solution**: Reduce model cache size in config
- **Alternative**: Enable lazy loading

#### Slow responses
- **Check**: Internet connection for web features
- **Solution**: Disable real-time features if offline
- **Optimize**: Increase cache duration

---

## 🔄 Updates & Maintenance

### Updating Dependencies
```bash
# Update all packages
pip install -r requirements.txt --upgrade

# Update specific package
pip install transformers --upgrade
```

### Updating Models
```bash
# Update spaCy model
python -m spacy download en_core_web_sm --upgrade

# Clear model cache
rm -rf models/cache/
```

### Database Maintenance
```bash
# Reinitialize databases
python scripts/init_db.py

# Clear conversation history
rm data/memory.db

# Clear cache
rm data/cache.db
```

---

## 🔒 Security Considerations

### Data Privacy
- All processing happens locally by default
- Conversation history stored locally
- API keys stored in .env file (keep secure)
- No telemetry sent without consent

### Network Security
- API server binds to localhost by default
- Use HTTPS in production
- Configure firewall rules appropriately
- Monitor access logs

### File Permissions
```bash
# Secure configuration files
chmod 600 .env
chmod 600 config/default.yaml

# Secure data directory
chmod 700 data/
```

---

## 📊 Performance Optimization

### Memory Optimization
```yaml
# In config/default.yaml
performance:
  model_cache_size: 3        # Reduce if low on RAM
  lazy_load_models: true     # Load models on demand
  max_conversation_history: 100
```

### Speed Optimization
```yaml
performance:
  enable_caching: true
  cache_duration: 3600       # 1 hour
  max_concurrent_actions: 5
  response_timeout: 30
```

### Storage Optimization
```bash
# Clean up old logs
find data/logs/ -name "*.log" -mtime +30 -delete

# Compress old data
gzip data/logs/*.log.old
```

---

## ✅ Installation Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] spaCy model downloaded (`python -m spacy download en_core_web_sm`)
- [ ] NLTK data downloaded
- [ ] Databases initialized (`python scripts/init_db.py`)
- [ ] System status check passes (`python -m core.main status`)
- [ ] Basic test works (`python -m core.main query --query "Hello"`)
- [ ] Interactive mode starts (`python -m core.main start`)
- [ ] API keys configured (optional)
- [ ] Tests pass (`python test_jarvis_complete.py`)

---

## 🎉 Success!

If you see this message, installation is complete:

```
✅ System Status: Operational
🤖 Jarvis AI Assistant Ready
👤 Owner: Heoster
🏢 Developer: Codeex AI
📊 All systems nominal
```

**You're ready to use Jarvis!**

```bash
python -m core.main start
```

**"Good day, Heoster. Jarvis at your service. How may I assist you today?"** ✨

---

## 📞 Getting Help

- **Documentation**: Check other .md files in the repository
- **Logs**: Look at `data/logs/assistant.log` for errors
- **Tests**: Run `python test_jarvis_complete.py` to diagnose issues
- **Status**: Use `python -m core.main status` to check system health
- **Community**: Check GitHub issues for common problems

---

*Installation complete! Welcome to the future of AI assistance!* 🚀