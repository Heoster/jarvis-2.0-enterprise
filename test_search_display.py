"""
Quick test to verify web search results are displayed properly
"""

import asyncio
from core.jarvis_brain import JarvisBrain


async def test_search_display():
    """Test that search results show scraped content clearly"""
    print("\n" + "="*80)
    print("TESTING WEB SEARCH DISPLAY")
    print("="*80 + "\n")
    
    # Initialize Jarvis
    brain = JarvisBrain()
    
    # Test queries that should trigger web search
    test_queries = [
        "search for Python programming",
        "what is artificial intelligence",
        "find information about machine learning",
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"QUERY: {query}")
        print(f"{'='*80}\n")
        
        # Generate response
        response = await brain.generate_response(query)
        
        # Display response
        print(response)
        print("\n" + "="*80 + "\n")
        
        # Wait a bit between queries
        await asyncio.sleep(2)
    
    print("\n✅ Test complete! Check if scraped content is visible above.\n")


if __name__ == "__main__":
    print("\nStarting search display test...")
    print("This will test if web search results show scraped text and headings.\n")
    
    asyncio.run(test_search_display())
