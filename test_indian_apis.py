"""
Test Indian APIs - Financial and Geographical Data
"""

import asyncio
from core.jarvis_brain import JarvisBrain


async def test_indian_apis():
    """Test Indian financial and geographical APIs"""
    print("\n" + "="*80)
    print("TESTING INDIAN APIs - Financial & Geographical Data")
    print("="*80 + "\n")
    
    # Initialize Jarvis
    brain = JarvisBrain()
    
    # Test queries for Indian data
    test_queries = [
        "what is the bitcoin price in INR",
        "show me currency exchange rates for INR",
        "what is the pincode information for Muzaffarnagar",
        "show me my current location",
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
    
    print("\n✅ Test complete! Check if Indian data is displayed above.\n")


if __name__ == "__main__":
    print("\nStarting Indian APIs test...")
    print("This will test financial data in INR and geographical data for Muzaffarnagar, UP.\n")
    
    asyncio.run(test_indian_apis())
