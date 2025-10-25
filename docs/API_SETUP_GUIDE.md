# API Setup Guide - Weather & News for India

## Overview

This guide shows you how to set up free Weather and News APIs with default location set to **Muzaffarnagar, Uttar Pradesh, India**.

---

## ✅ News API - CONFIGURED

Your News API is already set up and working!

**API Key**: `751c492c240d46c2bb46c631ddd59626`
**Status**: ✓ Active
**Default Country**: India (IN)
**Free Tier**: 100 requests/day

### Test Your News API

```bash
# Quick test
python test_news_api.py

# Or use in assistant
python -m core.main query --query "What's the latest news from India?"
python -m core.main query --query "Show me technology news"
python -m core.main query --query "Get sports news"
```

### Available News Categories

- `general` - General news (default)
- `business` - Business news
- `technology` - Tech news
- `sports` - Sports news
- `entertainment` - Entertainment news
- `health` - Health news
- `science` - Science news

---

## ⚠️ Weather API - NOT YET CONFIGURED

To get weather data for Muzaffarnagar and other Indian cities, you need a free OpenWeatherMap API key.

### Step 1: Get Free API Key

1. Visit: https://openweathermap.org/api
2. Click "Get API Key" or "Sign Up"
3. Fill in the form:
   - Email address
   - Username
   - Password
4. Verify your email
5. Copy your API key

### Step 2: Add to .env File

Open the `.env` file and add your key:

```bash
# Replace this line:
OPENWEATHER_API_KEY=

# With your actual key:
OPENWEATHER_API_KEY=your_actual_key_here
```

### Step 3: Test Weather API

```bash
# Quick test
python -c "import asyncio; from execution.weather_api import get_weather; print(asyncio.run(get_weather()))"

# Or use in assistant
python -m core.main query --query "What's the weather in Muzaffarnagar?"
python -m core.main query --query "How's the weather?"
python -m core.main query --query "Weather in Delhi"
```

---

## Usage Examples

### In Python Code

```python
import asyncio
from execution.weather_api import WeatherAPI
from execution.news_api import NewsAPI

async def main():
    # Weather for Muzaffarnagar (default)
    weather_api = WeatherAPI()
    weather = await weather_api.get_current_weather()
    print(weather_api.format_weather_text(weather))
    
    # Weather for specific city
    weather = await weather_api.get_current_weather(city='Delhi')
    print(weather_api.format_weather_text(weather))
    
    # News from India
    news_api = NewsAPI()
    news = await news_api.get_top_headlines(page_size=5)
    print(news_api.format_news_text(news))
    
    # Technology news
    news = await news_api.get_news_by_category('technology', page_size=3)
    print(news_api.format_news_text(news))
    
    # Search news
    news = await news_api.search_news('cricket', page_size=5)
    print(news_api.format_news_text(news))

asyncio.run(main())
```

### In Assistant (Voice/Text)

```
You: "What's the weather in Muzaffarnagar?"
Assistant: "Weather in Muzaffarnagar: 28.5°C, partly cloudy. Feels like 30.2°C. Humidity: 65%. Wind: 3.5 m/s."

You: "Show me the latest news from India"
Assistant: "Here are the top 5 news headlines from India:
1. Sale of air purifiers, masks rise in Delhi...
2. Orkla India to 'go deep, not wide' in India play...
..."

You: "Get me technology news"
Assistant: "Here are the top technology news headlines from India:
1. [Latest tech news]
..."

You: "What's the weather?"
Assistant: "Weather in Muzaffarnagar: [current weather]"
```

---

## Default Settings

### Weather API
- **Default Location**: Muzaffarnagar, Uttar Pradesh, India
- **Coordinates**: 29.4727°N, 77.7085°E
- **Units**: Metric (Celsius)
- **Free Tier**: 1,000 calls/day, 60 calls/minute

### News API
- **Default Country**: India (IN)
- **Default Language**: English (en)
- **Free Tier**: 100 requests/day
- **Coverage**: Last 30 days of articles

---

## API Limits & Best Practices

### News API (100 requests/day)

**Smart Usage**:
- Cache results for 1 hour
- Limit to 5-10 articles per request
- Use categories to narrow results
- Search only when needed

**Example Caching**:
```python
# Cache news for 1 hour
last_fetch = None
cached_news = None

async def get_cached_news():
    global last_fetch, cached_news
    now = datetime.now()
    
    if last_fetch is None or (now - last_fetch).seconds > 3600:
        news_api = NewsAPI()
        cached_news = await news_api.get_top_headlines()
        last_fetch = now
    
    return cached_news
```

### Weather API (1,000 requests/day)

**Smart Usage**:
- Cache results for 10-15 minutes
- Weather doesn't change that fast
- Use forecast for future predictions

---

## Troubleshooting

### News API Issues

**Problem**: "API error: 401"
- **Solution**: Check your API key in `.env` file
- **Verify**: Key should be 32 characters

**Problem**: "API error: 429"
- **Solution**: You've hit the daily limit (100 requests)
- **Wait**: Limit resets at midnight UTC
- **Tip**: Implement caching

**Problem**: No articles returned
- **Solution**: Try different search terms or categories
- **Note**: Some categories may have fewer articles

### Weather API Issues

**Problem**: "Demo data" message
- **Solution**: Add your OpenWeatherMap API key to `.env`

**Problem**: "API error: 401"
- **Solution**: Check your API key
- **Verify**: Key is activated (can take 10 minutes after signup)

**Problem**: Wrong location
- **Solution**: Specify city name: `get_current_weather(city='YourCity')`

---

## Testing Commands

### Test News API
```bash
# Test 1: Top headlines
python -c "import asyncio; from execution.news_api import get_india_news; print(asyncio.run(get_india_news()))"

# Test 2: Technology news
python -c "import asyncio; from execution.news_api import get_india_news; print(asyncio.run(get_india_news('technology')))"

# Test 3: Search
python -c "import asyncio; from execution.news_api import search_india_news; print(asyncio.run(search_india_news('cricket')))"
```

### Test Weather API
```bash
# Test 1: Default location (Muzaffarnagar)
python -c "import asyncio; from execution.weather_api import get_weather; print(asyncio.run(get_weather()))"

# Test 2: Specific city
python -c "import asyncio; from execution.weather_api import get_weather; print(asyncio.run(get_weather('Delhi')))"
```

### Test in Assistant
```bash
# Start interactive mode
python -m core.main start

# Then type:
# "What's the weather?"
# "Show me the news"
# "Get technology news"
```

---

## API Documentation Links

- **NewsAPI**: https://newsapi.org/docs
- **OpenWeatherMap**: https://openweathermap.org/api

---

## Summary

✅ **News API**: Configured and working with your key
⚠️ **Weather API**: Needs free API key from OpenWeatherMap

**Next Steps**:
1. Get free OpenWeatherMap API key (5 minutes)
2. Add it to `.env` file
3. Test with: `python test_news_api.py`
4. Start using: `python -m core.main start`

**Your assistant is now India-focused with:**
- Default location: Muzaffarnagar, UP
- Default country: India
- English language
- Free APIs (no payment needed)

---

**Last Updated**: 2024-10-25
**Status**: News API ✓ Active | Weather API ⚠️ Pending Setup
