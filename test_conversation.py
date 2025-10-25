"""
Test Jarvis's Natural Language Understanding and Conversational Abilities
"""

import asyncio
from core.jarvis_brain import JarvisBrain


async def test_conversation():
    """Test natural language conversation"""
    print("\n" + "="*80)
    print("TESTING NATURAL LANGUAGE CONVERSATION")
    print("="*80 + "\n")
    
    # Initialize Jarvis
    brain = JarvisBrain()
    
    # Test various conversational queries
    test_queries = [
        # Greetings
        "Hello!",
        "Hi there",
        "Good morning",
        "Hey Jarvis",
        
        # Questions about Jarvis
        "Who are you?",
        "What can you do?",
        "What are your capabilities?",
        "How are you?",
        
        # Thanks and farewell
        "Thank you",
        "Thanks for your help",
        "Goodbye",
        "See you later",
        
        # Natural questions
        "Can you help me?",
        "I need some information",
        "Tell me something interesting",
        
        # Mixed queries
        "What's the weather like?",
        "How do I search for something?",
        "Can you tell me a joke?",
    ]
    
    for query in test_queries:
        print(f"\n{'─'*80}")
        print(f"YOU: {query}")
        print(f"{'─'*80}")
        
        # Generate response
        response = await brain.generate_response(query)
        
        # Display response
        print(f"JARVIS: {response}\n")
        
        # Small delay
        await asyncio.sleep(0.5)
    
    print("\n" + "="*80)
    print("✅ Conversation test complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    print("\nTesting Jarvis's conversational abilities...")
    print("This will test natural language understanding and responses.\n")
    
    asyncio.run(test_conversation())
