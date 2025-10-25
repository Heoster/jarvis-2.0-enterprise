"""
Demo script for Weather and News APIs.

Shows how to use the free APIs with default India settings.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execution.weather_api import WeatherAPI, get_weather
from execution.news_api import NewsAPI, get_india_news, search_india_news


async def demo_weather():
    """Demonstrate weather API."""
    print("=" * 60)
    print("Weather API Demo")
    print("=" * 60)
    print()
    
    api = WeatherAPI()
    
    # 1. Default location (Muzaffarnagar, UP, India)
    print("1. Weather in Muzaffarnagar (default):")
    print("-" * 60)
    weather = await api.get_current_weather()
    print(api.format_weather_text(weather))
    print()
    
    # 2. Specific city in India
    print("2. Weather in Delhi:")
    print("-" * 60)
    weather = await api.get_current_weather(city='Delhi')
    print(api.format_weather_text(weather))
    print()
    
    # 3. Another city
    print("3. Weather in Mumbai:")
    print("-" * 60)
    weather = await api.get_current_weather(city='Mumbai')
    print(api.format_weather_text(weather))
    print()
    
    # 4. Forecast
    print("4. 5-day forecast for Muzaffarnagar:")
    print("-" * 60)
    forecast = await api.get_forecast()
    if forecast.get('success'):
        print(f"Location: {forecast['location']['city']}")
        print(f"Total forecasts: {len(forecast['forecast'])}")
        print("\nNext 24 hours:")
        for item in forecast['forecast'][:8]:  # First 8 = 24 hours
            print(f"  {item['datetime']}: {item['temperature']:.1f}°C, {item['description']}")
    else:
        print(f"Error: {forecast.get('error')}")
    print()
    
    # 5. Quick function
    print("5. Using convenience function:")
    print("-" * 60)
    text = await get_weather('Bangalore')
    print(text)
    print()


async def demo_news():
    """Demonstrate news API."""
    print("=" * 60)
    print("News API Demo")
    print("=" * 60)
    print()
    
    api = NewsAPI()
    
    # 1. Top headlines from India
    print("1. Top headlines from India:")
    print("-" * 60)
    news = await api.get_top_headlines(page_size=5)
    print(api.format_news_text(news))
    print()
    
    # 2. Technology news
    print("2. Technology news from India:")
    print("-" * 60)
    news = await api.get_news_by_category('technology', page_size=3)
    print(api.format_news_text(news, max_articles=3))
    print()
    
    # 3. Sports news
    print("3. Sports news from India:")
    print("-" * 60)
    news = await api.get_news_by_category('sports', page_size=3)
    print(api.format_news_text(news, max_articles=3))
    print()
    
    # 4. Search for specific topic
    print("4. Search for 'cricket' news:")
    print("-" * 60)
    news = await api.search_news('cricket', page_size=3)
    print(api.format_news_text(news, max_articles=3))
    print()
    
    # 5. Quick functions
    print("5. Using convenience functions:")
    print("-" * 60)
    text = await get_india_news(category='business', count=3)
    print(text)
    print()


async def demo_integrated():
    """Demonstrate integrated usage (like in the assistant)."""
    print("=" * 60)
    print("Integrated Demo (Assistant-style)")
    print("=" * 60)
    print()
    
    # Simulate user queries
    queries = [
        "What's the weather in Muzaffarnagar?",
        "Show me the latest news from India",
        "What's the weather like?",
        "Get me technology news"
    ]
    
    for query in queries:
        print(f"User: {query}")
        print("-" * 60)
        
        # Simple query parsing
        query_lower = query.lower()
        
        if 'weather' in query_lower:
            # Extract city if mentioned
            city = None
            if 'in ' in query_lower:
                parts = query_lower.split('in ')
                if len(parts) > 1:
                    city = parts[1].strip().rstrip('?').title()
            
            weather_api = WeatherAPI()
            weather = await weather_api.get_current_weather(city=city)
            response = weather_api.format_weather_text(weather)
            print(f"Assistant: {response}")
        
        elif 'news' in query_lower:
            # Extract category if mentioned
            category = None
            for cat in ['business', 'technology', 'sports', 'entertainment', 'health']:
                if cat in query_lower:
                    category = cat
                    break
            
            news_api = NewsAPI()
            news = await news_api.get_top_headlines(category=category, page_size=3)
            response = news_api.format_news_text(news, max_articles=3)
            print(f"Assistant: {response}")
        
        print()


async def main():
    """Run all demos."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Weather & News API Demo" + " " * 25 + "║")
    print("║" + " " * 10 + "Default: India (Muzaffarnagar, UP)" + " " * 13 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # Check for API keys
    has_weather_key = bool(os.getenv('OPENWEATHER_API_KEY'))
    has_news_key = bool(os.getenv('NEWS_API_KEY'))
    
    if not has_weather_key or not has_news_key:
        print("⚠️  API Keys Not Found")
        print("-" * 60)
        if not has_weather_key:
            print("❌ OPENWEATHER_API_KEY not set")
            print("   Get free key: https://openweathermap.org/api")
        if not has_news_key:
            print("❌ NEWS_API_KEY not set")
            print("   Get free key: https://newsapi.org/register")
        print()
        print("📝 Using demo data for this demonstration.")
        print("   Set API keys in .env file for real data.")
        print()
    else:
        print("✅ API Keys Found")
        print("-" * 60)
        if has_weather_key:
            print("✓ OPENWEATHER_API_KEY is set")
        if has_news_key:
            print("✓ NEWS_API_KEY is set")
        print()
    
    input("Press Enter to continue...")
    print()
    
    try:
        # Run demos
        await demo_weather()
        input("Press Enter for news demo...")
        print()
        
        await demo_news()
        input("Press Enter for integrated demo...")
        print()
        
        await demo_integrated()
        
        print("=" * 60)
        print("✅ Demo Complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Get free API keys (see links above)")
        print("2. Add them to .env file")
        print("3. Try: python -m core.main query --query 'What's the weather?'")
        print()
    
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
