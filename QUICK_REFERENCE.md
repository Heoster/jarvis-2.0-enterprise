# 🚀 Quick Reference - JARVIS Assistant

## ⚡ Quick Commands

### Test News (Working Now!)
```bash
python simple_news_test.py
```

### Start Assistant
```bash
python -m core.main start
```

### Single Query
```bash
python -m core.main query --query "What's the latest news?"
```

### Generate Training Data
```bash
python scripts/generate_training_data.py
```

---

## 🔑 API Keys

### News API ✅
```
Key: 751c492c240d46c2bb46c631ddd59626
File: .env
Status: Active
```

### Weather API ⚠️
```
Get key: https://openweathermap.org/api
Add to: .env file
Status: Needs setup (5 min)
```

---

## 💬 Example Queries

### News (Working!)
- "What's the latest news?"
- "Show me cricket news"
- "Get technology news"
- "What's happening in India?"

### Weather (Needs API key)
- "What's the weather?"
- "How's the weather in Delhi?"
- "Temperature in Muzaffarnagar"

### Math
- "What is 5 times 7?"
- "Calculate 2 + 2"
- "Derivative of x squared"

### General
- "What is AI?"
- "Explain Python"
- "How does this work?"

---

## 📁 Key Files

```
.env                          # API keys
simple_news_test.py          # Test news
SETUP_COMPLETE.md            # Full guide
INDIA_API_SETUP.md           # India setup
core/action_planner.py       # Action planning
execution/news_api.py        # News API
execution/weather_api.py     # Weather API
```

---

## 🎯 Default Settings

**Location**: Muzaffarnagar, UP, India
**Country**: India (IN)
**Language**: English
**Units**: Metric (Celsius)

---

## 📊 Status

✅ Core System: Complete
✅ News API: Active
✅ Action Planning: Complete
✅ Data Generation: Working
⚠️ Weather API: Needs key
⚠️ Voice: Future

---

## 🆘 Quick Fixes

**News not working?**
→ Check `.env` has `NEWS_API_KEY=751c492c...`

**Weather shows demo data?**
→ Add `OPENWEATHER_API_KEY` to `.env`

**Import errors?**
→ Run `pip install -r requirements.txt`

---

**Ready to start?** → `python -m core.main start`
