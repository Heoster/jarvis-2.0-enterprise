# Quick Start Guide - On-Device Assistant

Get up and running with the On-Device Assistant in minutes.

## Prerequisites

- Python 3.9+ installed
- 8GB RAM minimum
- Internet connection (for initial setup)

## 5-Minute Setup

### 1. Install

```bash
# Clone and enter directory
git clone <repository-url>
cd on-device-assistant

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Download Models

```bash
# Download NLP models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 3. Initialize

```bash
# Initialize databases
python scripts/init_db.py
```

### 4. Run

```bash
# Start interactive mode
python -m core.main start
```

## First Queries

Try these examples:

### Basic Conversation
```
You: Hello!
Assistant: Hello! How can I help you today?

You: What can you do?
Assistant: I can help with calculations, answer questions, search the web, 
get weather and news, analyze images, and much more!
```

### Math Calculations
```
You: What is 15 * 27 + 42?
Assistant: The answer is 447.

You: Calculate the square root of 144
Assistant: The answer is 12.0.
```

### Information Queries
```
You: Tell me about Python programming
Assistant: Python is a high-level, interpreted programming language...
[Information from Wikipedia]

You: What is machine learning?
Assistant: Machine learning is a subset of artificial intelligence...
```

### Real-Time Data (with API keys)
```
You: What's the weather in London?
Assistant: The current temperature in London is 15°C with cloudy skies.

You: Show me the latest tech news
Assistant: Here are today's top technology headlines:
1. [News headline 1]
2. [News headline 2]
...

You: Search for best Python tutorials
Assistant: I found these resources:
1. [Search result 1]
2. [Search result 2]
...
```

## Configuration

### Basic Configuration

Edit `config/default.yaml`:

```yaml
assistant:
  name: "MyAssistant"
  personality: "friendly"  # or "formal", "concise"
  language: "en"
```

### Enable API Features

Create `.env` file:

```bash
# Weather
OPENWEATHER_API_KEY=your-key-here
ASSISTANT_APIS__WEATHER__ENABLED=true

# News
NEWS_API_KEY=your-key-here
ASSISTANT_APIS__NEWS__ENABLED=true

# Search (free, no key needed)
ASSISTANT_APIS__SEARCH__ENABLED=true
```

### Enable Google Cloud Features

```bash
# Set credentials
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
DIALOGFLOW_PROJECT_ID=your-project-id

# Enable Dialogflow
ASSISTANT_MODELS__AI__USE_DIALOGFLOW=true
```

## Usage Modes

### Interactive CLI

```bash
python -m core.main start
```

Best for: Testing, development, casual use

### Single Query

```bash
python -m core.main query --query "What is 2+2?"
```

Best for: Scripting, automation

### API Server

```bash
python -m core.main server --port 8000
```

Best for: Integration with other apps

Access at: http://localhost:8000/docs

### Python API

```python
from core.assistant import Assistant

# Create assistant
assistant = Assistant()

# Process query
response = await assistant.process_query("Hello!")
print(response.text)
```

## API Examples

### REST API

```python
import requests

# Query endpoint
response = requests.post('http://localhost:8000/api/v1/query', json={
    'text': 'What is the capital of France?'
})

result = response.json()
print(result['text'])
```

### WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/assistant');

ws.onopen = () => {
    ws.send(JSON.stringify({
        type: 'query',
        text: 'Hello, assistant!'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Response:', data.text);
};
```

## Computer Vision

### Analyze Images

```python
from core.vision import VisionEngine

vision = VisionEngine()

# Detect faces
faces = await vision.detect_faces('photo.jpg')
print(f"Found {len(faces)} faces")

# Analyze image
analysis = await vision.analyze_image('image.jpg')
print(f"Size: {analysis['width']}x{analysis['height']}")
print(f"Brightness: {analysis['brightness']}")

# Extract text (OCR)
text_data = await vision.extract_text('document.jpg')
print(f"Extracted text: {text_data['text']}")
```

## Real-Time Data

### Weather

```python
from core.realtime_data import RealTimeDataManager

data_manager = RealTimeDataManager(
    weather_api_key='your-key'
)

# Get current weather
weather = await data_manager.get_weather('New York')
print(f"Temperature: {weather['temperature']}°C")
print(f"Conditions: {weather['description']}")
```

### News

```python
# Get top headlines
news = await data_manager.get_news(category='technology', limit=5)

for article in news:
    print(f"- {article['title']}")
    print(f"  Source: {article['source']}")
```

### Web Search

```python
# Search the web
results = await data_manager.search_web('Python tutorials', limit=10)

for result in results:
    print(f"- {result['title']}")
    print(f"  {result['url']}")
```

### Knowledge

```python
# Get Wikipedia summary
info = await data_manager.get_knowledge('Artificial Intelligence')
print(f"Title: {info['title']}")
print(f"Summary: {info['summary']}")
print(f"URL: {info['url']}")
```

## Common Commands

### Check Status

```bash
python -m core.main status
```

Shows:
- System status
- Available components
- Configuration
- Uptime

### View Logs

```bash
# View recent logs
tail -f data/logs/assistant.log

# Windows
type data\logs\assistant.log
```

### Clear Data

```bash
# Clear conversation history
rm data/memory.db

# Clear cache
rm data/cache.db

# Reinitialize
python scripts/init_db.py
```

## Tips & Tricks

### Personality Modes

Change personality in `config/default.yaml`:

```yaml
assistant:
  personality: "friendly"  # Warm and conversational
  # personality: "formal"   # Professional and precise
  # personality: "concise"  # Brief and to the point
```

### Performance Tuning

```yaml
performance:
  max_concurrent_actions: 5      # Parallel action limit
  model_cache_size: 3            # Number of models in memory
  lazy_load_models: true         # Load models on demand
```

### Privacy Settings

```yaml
privacy:
  local_only: true               # No external calls
  encrypt_memory: true           # Encrypt stored data
  data_retention_days: 30        # Auto-delete old data
```

## Troubleshooting

### "Module not found" errors

```bash
pip install -r requirements.txt --upgrade
```

### Slow responses

- Reduce `model_cache_size` if low on RAM
- Enable `lazy_load_models`
- Use faster models in config

### API errors

- Check API keys in `.env`
- Verify internet connection
- Check API rate limits

### Database errors

```bash
# Reinitialize databases
python scripts/init_db.py
```

## Next Steps

1. **Configure API Keys**: Get weather and news data
   - OpenWeatherMap: https://openweathermap.org/api
   - NewsAPI: https://newsapi.org/

2. **Enable Google Cloud**: Use Dialogflow and Speech APIs
   - Follow [INSTALL.md](INSTALL.md) Google Cloud section

3. **Customize**: Edit `config/default.yaml` for your needs

4. **Integrate**: Use the API server for your applications

5. **Explore**: Check [README.md](README.md) for all features

## Getting Help

- **Documentation**: See [README.md](README.md) and [INSTALL.md](INSTALL.md)
- **Logs**: Check `data/logs/assistant.log`
- **Issues**: Open a GitHub issue
- **Examples**: See `examples/` directory

## Example Session

```
$ python -m core.main start

🤖 On-Device Assistant v0.1.0
Type 'help' for commands, 'exit' to quit

You: What is 25 * 4?
Assistant: The answer is 100.

You: Tell me about quantum computing
Assistant: Quantum computing is a type of computation that harnesses 
quantum mechanical phenomena like superposition and entanglement...

You: What's the weather in Tokyo?
Assistant: The current temperature in Tokyo is 22°C with clear skies.
Humidity is at 65% with light winds from the east.

You: Show me tech news
Assistant: Here are today's top technology headlines:
1. New AI breakthrough in natural language processing
2. Tech giant announces quantum computer milestone
3. Cybersecurity threats on the rise

You: exit
Goodbye! 👋
```

---

**Ready to go!** Start exploring with:
```bash
python -m core.main start
```
