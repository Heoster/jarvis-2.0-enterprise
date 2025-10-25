"""
Test Web Search and Scraping Functionality
Run this to verify web scraping is working correctly
"""

import asyncio
from core.web_scraper import get_web_scraper


async def test_search():
    """Test DuckDuckGo search"""
    print("=" * 70)
    print("Testing DuckDuckGo Search")
    print("=" * 70)
    
    scraper = await get_web_scraper()
    
    # Test search
    query = "Python programming tutorial"
    print(f"\nSearching for: {query}")
    
    results = await scraper.search_duckduckgo(query, max_results=5)
    
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Snippet: {result['snippet'][:100]}...")
    
    return results


async def test_scrape(url):
    """Test webpage scraping"""
    print("\n" + "=" * 70)
    print("Testing Webpage Scraping")
    print("=" * 70)
    
    scraper = await get_web_scraper()
    
    print(f"\nScraping: {url}")
    
    content = await scraper.scrape_webpage(url)
    
    if 'error' in content:
        print(f"Error: {content['error']}")
    else:
        print(f"\nTitle: {content.get('title', 'N/A')}")
        print(f"Description: {content.get('description', 'N/A')[:100]}...")
        print(f"Content length: {len(content.get('content', ''))} characters")
        print(f"\nFirst 500 characters of content:")
        print(content.get('content', '')[:500])
    
    return content


async def test_search_and_scrape():
    """Test combined search and scrape"""
    print("\n" + "=" * 70)
    print("Testing Search and Scrape Combined")
    print("=" * 70)
    
    scraper = await get_web_scraper()
    
    query = "artificial intelligence news"
    print(f"\nSearching and scraping for: {query}")
    
    results = await scraper.search_and_scrape(query, num_results=3)
    
    if 'error' in results:
        print(f"Error: {results['error']}")
    else:
        print(f"\nQuery: {results['query']}")
        print(f"Total search results: {results['total_results']}")
        print(f"Successfully scraped: {results['scraped_count']}")
        
        for i, item in enumerate(results.get('scraped_content', []), 1):
            print(f"\n--- Result {i} ---")
            print(f"Title: {item['title']}")
            print(f"URL: {item['url']}")
            print(f"Snippet: {item['snippet'][:100]}...")
            print(f"Content preview: {item['content'][:200]}...")
            print(f"Full content length: {len(item.get('full_content', ''))} chars")
    
    return results


async def test_jarvis_search():
    """Test Jarvis brain with web search"""
    print("\n" + "=" * 70)
    print("Testing Jarvis Brain with Web Search")
    print("=" * 70)
    
    from core.jarvis_brain import JarvisBrain
    
    brain = JarvisBrain()
    
    # Test queries that should trigger web search
    test_queries = [
        "search for Python tutorials",
        "what is machine learning",
        "find information about AI",
    ]
    
    for query in test_queries:
        print(f"\n\nQuery: {query}")
        print("-" * 70)
        
        response = await brain.generate_response(query)
        
        print(f"\nResponse:\n{response}")
        print("\n" + "=" * 70)


async def main():
    """Run all tests"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                                                                      ║")
    print("║              WEB SCRAPING FUNCTIONALITY TEST                         ║")
    print("║                                                                      ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print("\n")
    
    try:
        # Test 1: Search
        search_results = await test_search()
        
        # Test 2: Scrape first result
        if search_results:
            await test_scrape(search_results[0]['url'])
        
        # Test 3: Combined search and scrape
        await test_search_and_scrape()
        
        # Test 4: Jarvis brain integration
        await test_jarvis_search()
        
        print("\n")
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║                                                                      ║")
        print("║                    ALL TESTS COMPLETED! ✅                           ║")
        print("║                                                                      ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print("\n")
    
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\nStarting web scraping tests...")
    print("This will test DuckDuckGo search and webpage scraping.\n")
    
    asyncio.run(main())
