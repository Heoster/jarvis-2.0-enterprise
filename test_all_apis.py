"""
Test All APIs - Financial, Railway, Mutual Funds, and Entertainment
"""

import asyncio
from core.jarvis_brain import JarvisBrain


async def test_all_apis():
    """Test all integrated APIs"""
    print("\n" + "="*80)
    print("TESTING ALL INTEGRATED APIs")
    print("="*80 + "\n")
    
    # Initialize Jarvis
    brain = JarvisBrain()
    
    # Test queries for all APIs
    test_queries = [
        # Financial
        "what is the bitcoin price in INR",
        "show me currency exchange rates",
        
        # Railway
        "show me train information",
        "what is train schedule for 14511",
        
        # Mutual Funds
        "show me mutual fund NAV",
        "search for SBI bluechip fund",
        
        # Entertainment - Jokes
        "tell me a joke",
        "tell me a programming joke",
        
        # Entertainment - Images & Facts
        "show me a dog image",
        "tell me a cat fact",
        
        # Entertainment - Quotes
        "give me an inspirational quote",
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
        await asyncio.sleep(1)
    
    print("\n✅ All API tests complete!\n")


if __name__ == "__main__":
    print("\nStarting comprehensive API test...")
    print("Testing: Finance, Railway, Mutual Funds, Jokes, Images, Quotes\n")
    
    asyncio.run(test_all_apis())
