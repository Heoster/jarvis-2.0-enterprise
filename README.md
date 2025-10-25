# Codeex AI - Magical Learning Assistant

Meet **Jarvis** - Heoster's personal AI assistant, developed by **Codeex AI Company**! A sophisticated, intelligent companion powered by advanced AI with Transformers, LangChain, real-time web scraping, and a professional personality.

> *"Good morning, Heoster. Jarvis at your service. Systems are online and ready."*

**Identity:**
- **Name**: Jarvis
- **Owner**: Heoster (your personal AI)
- **Developer**: Codeex AI Company
- **Purpose**: Your intelligent, loyal, and capable AI companion

## 🎯 What's New in Codeex

- **🌐 Advanced Web Scraping** - Real-time data gathering from DuckDuckGo and web pages
- **🎭 Personal AI for Heoster** - Jarvis is now your personal AI, developed by Codeex AI
- **🧠 Intelligent API Routing** - Automatically detects intent and routes to appropriate endpoints
- **🔍 Smart Search** - Automatically searches and scrapes web for current information
- **🪄 Magical Personality** - Warm, encouraging responses with emojis and sparkles
- **📝 Grammar Correction** - Professional grammar checking with magical feedback
- **🎯 Interactive Quizzes** - Test your knowledge with instant feedback
- **📚 Expanded Knowledge** - Minecraft modding, coding, homework help, and more
- **⭐ Feedback System** - Help Codeex improve through your feedback
- **🎓 Student-Focused** - Designed specifically for learners of all levels
- **💬 Natural Language** - Just ask naturally - no commands needed!

## Features

- **Jarvis AI Brain**: Sophisticated AI powered by Transformers + LangChain
- **Advanced NLP**: Deep text understanding using spaCy, NLTK, and transformers
- **Conversational Intelligence**: Context-aware, multi-turn conversations with memory
- **Computer Vision**: OpenCV integration for image analysis and face detection
- **Real-Time Data**: Live weather, news, web search, and knowledge graph access
- **Multi-Source Intelligence**: Retrieves from memory, training data, web, and APIs
- **Two-Stage Retrieval**: BM25 sparse + dense semantic search
- **Sophisticated Personality**: Professional yet personable, like Tony Stark's AI
- **Voice Control**: Google Cloud Speech-to-Text and Text-to-Speech (coming soon)
- **Device & Browser Control**: Complete hands-free operation (coming soon)
- **Privacy-First**: All data stays local by default
- **Fast**: <800ms response time for simple queries

## Architecture

```
User Input → NLP Analysis → Intent Classification → Action Planning
    ↓
Retrieval (Memory + Knowledge + Real-time Data) → AI Generation → Response
    ↓
Action Execution → Memory Storage → User Output
```

## Key Technologies

### AI Frameworks
- **Google Dialogflow**: Advanced conversational AI and intent detection
- **Transformers**: Local NLU with Hugging Face models (BlenderBot, etc.)
- **OpenCV**: Computer vision for image analysis and object detection

### Real-Time Capabilities
- **Weather**: OpenWeatherMap integration
- **News**: NewsAPI for latest headlines and articles
- **Search**: DuckDuckGo web search
- **Knowledge**: Wikipedia and knowledge graph integration

### Machine Learning
- **TensorFlow & PyTorch**: Deep learning frameworks
- **spaCy & NLTK**: Natural language processing
- **Sentence Transformers**: Semantic embeddings

### Speech
- **Google Cloud Speech-to-Text**: High-quality voice recognition
- **Google Cloud Text-to-Speech**: Natural voice synthesis
- **Local alternatives**: SpeechRecognition, pyttsx3

## Installation

### Prerequisites

- Python 3.9 or higher
- 8GB RAM minimum (16GB recommended)
- Optional: Google Cloud account for Dialogflow and Speech APIs

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd on-device-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Download NLP Models

```bash
# Download spaCy models
python -m spacy download en_core_web_sm

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### Step 3: Configure APIs (Optional)

Create a `.env` file:

```bash
# Google Cloud (optional)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
DIALOGFLOW_PROJECT_ID=your-project-id

# Weather API (optional)
OPENWEATHER_API_KEY=your-api-key

# News API (optional)
NEWS_API_KEY=your-api-key
```

### Step 4: Initialize Databases

```bash
# Initialize databases
python scripts/init_db.py
```

## Quick Start

### Interactive Mode

```bash
# Start interactive CLI
python -m core.main start

# Or use the assistant command (after installation)
assistant start
```

### Single Query Mode

```bash
python -m core.main query --query "What is the weather today?"
```

### Server Mode

```bash
# Start API server
python -m core.main server --host 127.0.0.1 --port 8000

# Access API at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Check Status

```bash
python -m core.main status
```

## Configuration

Configuration is managed through `config/default.yaml`. You can also use environment variables:

```bash
# Set custom config path
export ASSISTANT_CONFIG_PATH=/path/to/config.yaml

# Override specific settings
export ASSISTANT_SERVER__PORT=9000
export ASSISTANT_MODELS__AI__USE_DIALOGFLOW=true
```

See `.env.example` for all available environment variables.

## Usage Examples

### Interactive CLI

```
You: What is 15 + 27?
Assistant: The answer is 42.

You: What's the weather in New York?
Assistant: The current temperature in New York is 72°F with partly cloudy skies.

You: Tell me the latest news
Assistant: Here are today's top headlines: [news articles]

You: Search for Python tutorials
Assistant: I found several resources: [search results]

You: Open Chrome
Assistant: Opening Chrome now.
```

### API Usage

```python
import requests

# Query endpoint
response = requests.post('http://localhost:8000/api/v1/query', json={
    'text': 'What is the capital of France?',
    'stream': False
})

print(response.json())
```

### Computer Vision

```python
from core.vision import VisionEngine

vision = VisionEngine()

# Detect faces
faces = await vision.detect_faces('image.jpg')

# Analyze image
analysis = await vision.analyze_image('photo.jpg')

# Extract text (OCR)
text = await vision.extract_text('document.jpg')
```

### Real-Time Data

```python
from core.realtime_data import RealTimeDataManager

data_manager = RealTimeDataManager(
    weather_api_key='your-key',
    news_api_key='your-key'
)

# Get weather
weather = await data_manager.get_weather('London')

# Get news
news = await data_manager.get_news(category='technology')

# Search web
results = await data_manager.search_web('AI trends 2024')

# Get knowledge
info = await data_manager.get_knowledge('Quantum Computing')
```

## Project Structure

```
on-device-assistant/
├── core/                   # Core intelligence components
│   ├── nlp.py             # NLP engine
│   ├── decision_engine.py # Intent classification
│   ├── action_planner.py  # Action planning
│   ├── retrieval.py       # Information retrieval
│   ├── ai_client.py       # AI backends (Dialogflow, local)
│   ├── realtime_data.py   # Real-time data services
│   ├── vision.py          # Computer vision
│   ├── assistant.py       # Main orchestrator
│   └── main.py            # Entry point
├── storage/               # Data persistence
│   ├── memory_store.py    # User memory
│   ├── vector_db.py       # Vector database
│   └── knowledge_cache.py # Document cache
├── execution/             # Action executors
│   ├── math_engine.py     # Math operations
│   └── code_engine.py     # Code execution
├── server/                # API server
│   └── api.py             # FastAPI endpoints
├── monitoring/            # Security & monitoring
│   └── consent_manager.py # Permission management
├── voice/                 # Voice I/O (coming soon)
├── config/                # Configuration files
├── data/                  # Databases and cache
├── models/                # Downloaded models
└── scripts/               # Utility scripts
```

## Capabilities

### Natural Language Processing
- Intent classification
- Entity extraction
- Sentiment analysis
- Language detection
- Date/time parsing

### Real-Time Information
- Current weather and forecasts
- Latest news headlines
- Web search results
- Wikipedia knowledge
- Real-time data aggregation

### Computer Vision
- Face detection
- Object detection
- Image analysis
- OCR (text extraction)
- Image comparison

### Conversational AI
- Context-aware responses
- Multi-turn conversations
- Personality customization
- Multiple AI backends

### Action Execution
- Mathematical calculations
- Code execution (sandboxed)
- System commands
- Device control (coming soon)

## Performance

- **Simple queries**: <800ms (target)
- **Complex queries**: <2000ms (target)
- **Memory usage**: ~500MB base + models
- **CPU**: Optimized for multi-core processors

## Privacy & Security

- **Local-first**: All processing happens on your device
- **No telemetry**: No data sent to external servers by default
- **Encrypted storage**: Sensitive data encrypted at rest
- **Permission system**: Granular control over assistant capabilities
- **Audit logs**: Complete transparency of actions
- **Optional cloud**: Use Dialogflow/Google Cloud only if configured

## Roadmap

- [x] Core NLP and intent classification
- [x] AI integration with Dialogflow and local models
- [x] Two-stage retrieval system
- [x] Math and code execution
- [x] REST API and WebSocket support
- [x] Real-time data integration (weather, news, search)
- [x] Computer vision with OpenCV
- [x] Knowledge graph integration
- [ ] Voice input/output (STT/TTS)
- [ ] Device control (Windows/Linux/macOS)
- [ ] Browser control via extension
- [ ] Activity monitoring
- [ ] Mobile app integration

## Troubleshooting

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Google Cloud Setup

```bash
# Install Google Cloud SDK
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Test Dialogflow
python -c "from google.cloud import dialogflow; print('OK')"
```

### OpenCV Issues

```bash
# Reinstall OpenCV
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python opencv-contrib-python
```

### Database Errors

```bash
# Reinitialize databases
python scripts/init_db.py
```

## API Keys

To enable all features, obtain API keys from:

- **OpenWeatherMap**: https://openweathermap.org/api
- **NewsAPI**: https://newsapi.org/
- **Google Cloud**: https://console.cloud.google.com/
  - Enable Dialogflow API
  - Enable Speech-to-Text API
  - Enable Text-to-Speech API

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with Google Dialogflow, OpenCV, spaCy, FastAPI, and many other open-source libraries
- Inspired by the need for privacy-respecting AI assistants with real-time capabilities

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [repository-url]/docs

---

**Note**: This is an alpha release. Some features are still in development.
