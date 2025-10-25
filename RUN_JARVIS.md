# 🚀 How to Run JARVIS Complete

**Quick Start Guide for JARVIS Complete Edition**

---

## 🎯 Quick Start (Recommended)

### Option 1: Full System (All Features)
```bash
python jarvis.py
```
This runs **JARVIS Complete** with:
- ✅ Original JARVIS (web search, APIs, real-time data)
- ✅ JARVIS 2.0 (enhanced intelligence, sentiment, memory)
- ✅ All 18 features integrated

### Option 2: Simple Demo (Lightweight)
```bash
python jarvis.py --simple
```
No heavy models, instant start, basic features

### Option 3: Enhanced Features Only
```bash
python jarvis.py --enhanced-only
```
JARVIS 2.0 enhancements demo

### Option 4: Original JARVIS Only
```bash
python jarvis.py --original
```
Original full-featured JARVIS without enhancements

---

## 📋 All Available Commands

### Main Entry Points

| Command | Description | Features |
|---------|-------------|----------|
| `python jarvis.py` | **Complete System** | All 18 features |
| `python jarvis.py --simple` | Simple Demo | Lightweight, instant |
| `python jarvis.py --enhanced-only` | JARVIS 2.0 Demo | Enhanced features only |
| `python jarvis.py --original` | Original JARVIS | Full original features |
| `python jarvis.py --test` | Run Tests | Integration tests |

### Alternative Entry Points

| Command | Description |
|---------|-------------|
| `python run_jarvis_complete.py` | Direct unified system |
| `python run_jarvis_enhanced.py` | Direct enhanced demo |
| `python run_jarvis_simple.py` | Direct simple demo |
| `python -m core.main start` | Original with unified |
| `python -m core.main start --no-unified` | Original only |

### Testing

| Command | Description |
|---------|-------------|
| `python test_integration.py` | Integration tests |
| `pytest tests/test_jarvis_enhanced.py -v` | Enhanced features tests |
| `python retrain_classifier.py` | Retrain intent classifier |

---

## 🎓 What Each Mode Does

### 1. Complete System (`python jarvis.py`)

**Best for**: Production use, full capabilities

**Includes**:
- Web search and scraping
- Real-time data (weather, news)
- Indian APIs (finance, railway, location)
- Enhanced intent classification (95%+)
- Sentiment analysis
- Contextual memory with learning
- Semantic matching
- Query decomposition
- All 18 features

**Startup time**: ~10-15 seconds (loading models)

### 2. Simple Demo (`python jarvis.py --simple`)

**Best for**: Quick testing, demonstrations

**Includes**:
- Basic conversational AI
- Intent detection
- Simple responses
- No heavy models

**Startup time**: Instant

### 3. Enhanced Only (`python jarvis.py --enhanced-only`)

**Best for**: Testing JARVIS 2.0 features

**Includes**:
- Enhanced intent classification
- Sentiment analysis
- Contextual memory
- Semantic matching
- Magical personality

**Startup time**: ~5-10 seconds

### 4. Original Only (`python jarvis.py --original`)

**Best for**: Using proven original features

**Includes**:
- Web search and scraping
- Real-time data
- API routing
- Indian APIs
- Transformers + LangChain

**Startup time**: ~5-10 seconds

---

## 💡 Example Sessions

### Complete System Example

```bash
$ python jarvis.py

🚀 Starting JARVIS Complete - Unified System...
🤖 JARVIS COMPLETE - Unified System
============================================================
⏳ Initializing complete system...

Good day, sir. Jarvis at your service. How may I assist you today?

✅ System Status: OPERATIONAL

📦 Original JARVIS Features:
  • Web Search & Scraping
  • Real-time Data (Weather, News, Knowledge)
  • API Routing (Grammar, Quiz, Feedback)
  • Transformers + LangChain
  • Indian APIs (Finance, Railway, Location)
  • Action Planning & Execution

✨ JARVIS 2.0 Enhancements:
  • Enhanced Intent Classification (95%+ accuracy)
  • Semantic Matching with Sentence Transformers
  • Magical Prompt Engineering
  • Contextual Memory with Learning
  • Sentiment Analysis & Tone Adjustment
  • Multi-Stage Query Decomposition
  • Knowledge Graph

Type 'exit' or 'quit' to stop
============================================================

You: hello
🔄 Processing with unified system...

Jarvis: Good day, sir! Jarvis 2.0 at your service. How may I assist you today? ✨

[Session: 1 interactions]

You: search for quantum computing
🔄 Processing with unified system...

Jarvis: [Performs web search, analyzes sentiment, provides comprehensive answer]

[Session: 2 interactions]
```

### Simple Demo Example

```bash
$ python jarvis.py --simple

🤖 JARVIS 2.0 Enterprise Edition - Quick Demo
============================================================

✅ Initializing JARVIS 2.0...

🎯 JARVIS 2.0 Features:
  • Enhanced Intent Classification
  • Contextual Memory
  • Sentiment Analysis
  • Magical Personality

Type your message (or 'exit' to quit)
============================================================

You: hello

Jarvis: Good day, sir! Jarvis 2.0 at your service. How may I assist you today? ✨

[Intent: greeting | Turn: 1]
```

---

## 🔧 Troubleshooting

### Issue: "spaCy model not found"

**Solution**:
```bash
python -m spacy download en_core_web_sm
```

### Issue: "LangChain not available"

**Solution**:
```bash
pip install langchain langchain-community
```

### Issue: Slow startup

**Solution**: Use simple mode
```bash
python jarvis.py --simple
```

### Issue: Import errors

**Solution**: Install all dependencies
```bash
pip install -r requirements.txt
```

### Issue: Models downloading slowly

**Solution**: Wait for first run, models are cached after that

---

## 📊 Performance Comparison

| Mode | Startup Time | Response Time | Memory Usage | Features |
|------|--------------|---------------|--------------|----------|
| Complete | 10-15s | 2-6s | ~1GB | All 18 |
| Enhanced Only | 5-10s | 1-3s | ~500MB | 8 enhanced |
| Original Only | 5-10s | 2-5s | ~500MB | 10 original |
| Simple | Instant | <1s | ~50MB | Basic |

---

## 🎯 Recommended Usage

### For Development
```bash
python jarvis.py --simple          # Quick testing
python jarvis.py --test            # Run tests
```

### For Demonstration
```bash
python jarvis.py --enhanced-only   # Show new features
python jarvis.py --simple          # Quick demo
```

### For Production
```bash
python jarvis.py                   # Full system
```

### For Debugging
```bash
python jarvis.py --original        # Test original features
python test_integration.py         # Run all tests
```

---

## 📚 Additional Resources

- **Full Documentation**: `JARVIS_COMPLETE_INTEGRATION.md`
- **Feature Guide**: `JARVIS_UPGRADES_COMPLETE.md`
- **Developer Guide**: `JARVIS_DEVELOPER_GUIDE.md`
- **Original Features**: `HEOSTER_JARVIS_COMPLETE.md`

---

## ✅ Quick Checklist

Before running JARVIS:

- [ ] Python 3.9+ installed
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] spaCy model downloaded: `python -m spacy download en_core_web_sm`
- [ ] At least 8GB RAM available
- [ ] Internet connection (for web search features)

---

## 🎉 Success!

If you see this, JARVIS is working:

```
✅ System Status: OPERATIONAL
```

**You're ready to use JARVIS Complete!** 🚀✨

---

**"Good day, sir. All systems are operational. How may I assist you?"** 🎩
