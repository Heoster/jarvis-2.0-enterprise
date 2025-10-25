# 🚀 Codeex AI - Quick Start Guide

Get up and running with Codeex AI in 5 minutes!

---

## 📋 Prerequisites

- Python 3.9 or higher
- 8GB RAM minimum
- Internet connection (for API features)

---

## ⚡ Quick Install

### 1. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 2. Initialize Databases

```bash
python scripts/init_db.py
```

### 3. Configure (Optional)

Create `.env` file for API keys:

```bash
# Optional: For weather and news features
OPENWEATHER_API_KEY=your_key_here
NEWS_API_KEY=your_key_here

# Optional: For Google Cloud features
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

---

## 🎮 Usage

### Option 1: Interactive CLI (Recommended for First Time)

```bash
python -m core.main start
```

**Try these commands:**
```
> Hello!
> /correct hlo how r u
> /quiz python 5
> /help minecraft forge setup
> What is 15 + 27?
> /stats
```

### Option 2: API Server

```bash
# Start server
python -m core.main server

# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Option 3: Python Code

```python
from core.codeex_assistant import create_codeex_assistant
import asyncio

async def main():
    assistant = create_codeex_assistant()
    
    # Get greeting
    greeting = await assistant.get_greeting()
    print(greeting)
    
    # Correct grammar
    response = await assistant.process_query("/correct hlo how r u")
    print(response.text)
    
    # Start quiz
    response = await assistant.process_query("/quiz python 5")
    print(response.text)

asyncio.run(main())
```

---

## 🎯 Key Features & Commands

### Grammar Correction

```bash
# CLI
> /correct hlo how r u

# API
curl -X POST http://localhost:8000/api/v1/correct \
  -H "Content-Type: application/json" \
  -d '{"text": "hlo how r u"}'
```

### Interactive Quizzes

```bash
# CLI
> /quiz python 5          # Start 5-question Python quiz
> /quiz topics            # List available topics
> /quiz stats             # View your quiz statistics

# API
curl -X POST http://localhost:8000/api/v1/quiz/create \
  -H "Content-Type: application/json" \
  -d '{"topic": "python", "num_questions": 5}'
```

### Knowledge Base Help

```bash
# CLI
> /help minecraft forge setup
> /help python basics
> /help debugging tips

# API
curl "http://localhost:8000/api/v1/knowledge/search?q=minecraft+forge"
```

### Feedback

```bash
# CLI
> /feedback positive Great explanation!
> /feedback negative Too complicated

# API
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is 2+2?",
    "response": "The answer is 4",
    "feedback_type": "positive",
    "comment": "Clear and helpful!"
  }'
```

---

## 🎨 Available Quiz Topics

- **python** - Python programming
- **math** - Mathematics
- **minecraft** - Minecraft modding
- More topics can be added!

---

## 📚 Knowledge Base Categories

- **Minecraft Modding** - Forge setup, common errors, advanced topics
- **Programming** - Python, Java, coding best practices
- **Study Tips** - Learning strategies, debugging mindset
- **Homework Help** - Math, science, writing

---

## 🧪 Run Demo

```bash
python examples/codeex_demo.py
```

This demonstrates all features:
- Personalized greetings
- Grammar correction
- Quiz system
- Knowledge base
- Feedback system
- Regular queries

---

## 🔧 Troubleshooting

### Import Errors

```bash
pip install -r requirements.txt --upgrade
```

### Grammar Tool Not Working

```bash
# Install language tool
pip install language-tool-python

# If still issues, basic corrections will be used automatically
```

### Database Errors

```bash
# Reinitialize databases
python scripts/init_db.py
```

### Port Already in Use

```bash
# Use different port
python -m core.main server --port 8001
```

---

## 📊 Check Status

```bash
# CLI
> /stats

# API
curl http://localhost:8000/api/v1/status
curl http://localhost:8000/api/v1/quiz/stats
curl http://localhost:8000/api/v1/feedback/stats
```

---

## 🎓 Learning Path

### Day 1: Get Started
1. Install and run interactive CLI
2. Try grammar correction
3. Take your first quiz

### Day 2: Explore Features
1. Search knowledge base
2. Provide feedback
3. Check your statistics

### Day 3: Advanced Usage
1. Use API endpoints
2. Integrate into your projects
3. Add custom quiz questions

---

## 💡 Tips

1. **Use /correct** before submitting homework
2. **Take quizzes** to test your knowledge
3. **Provide feedback** to help Codeex improve
4. **Search knowledge base** when stuck
5. **Check stats** to track your progress

---

## 🌟 Example Session

```
You: Hello!
Codeex: 🌅 Good morning, brilliant student! Ready to learn some magic today?

You: /correct hlo how r u
Codeex: 🪄 Codeex's Grammar Magic ✨
        📝 You said: hlo how r u
        ✅ Codeex suggests: Hello, how are you?
        💡 What changed:
           1. Expanded 'hlo' to 'hello'
           2. Expanded 'r' to 'are'
           3. Expanded 'u' to 'you'
        You're doing great! 🌟

You: /quiz python 3
Codeex: 🌟 Codeex Quiz Time! 🌟
        ❓ What is the correct way to create a list in Python?
           1. list = []
           2. list = ()
           3. list = {}
           4. list = <>
        💭 Take your time and think it through!

You: 1
Codeex: ✨ Correct! Square brackets [] are used to create lists in Python.
        Score: 1/3
        [Next question appears...]
```

---

## 📖 Documentation

- **Full Features**: `CODEEX_FEATURES.md`
- **Implementation**: `IMPLEMENTATION_COMPLETE.md`
- **Statistics**: `JARVIS_STATS.md`
- **API Docs**: `http://localhost:8000/docs` (when server running)

---

## 🎉 You're Ready!

Start with:
```bash
python -m core.main start
```

Then type:
```
> Hello!
```

**Happy learning with Codeex! ✨🌟**

---

**Need help?** Check the documentation or ask Codeex directly!
