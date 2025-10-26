#!/usr/bin/env python3
"""
Comprehensive test for Iron Man JARVIS features
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_iron_man_jarvis():
    """Test all Iron Man JARVIS features"""
    try:
        from core.jarvis_brain import JarvisBrain
        
        print("🤖 Initializing Iron Man JARVIS...")
        jarvis = JarvisBrain()
        
        print("✅ JARVIS initialized successfully!")
        
        # Test Iron Man personality responses
        print("\n🎭 Testing Iron Man Personality...")
        
        test_queries = [
            "hello",
            "good morning", 
            "what time is it",
            "what can you do",
            "who are you",
            "how are you",
            "thank you",
            "calculate 25 + 17",
            "search for artificial intelligence",
            "tell me a joke"
        ]
        
        for query in test_queries:
            print(f"\n👤 User: {query}")
            response = await jarvis.generate_response(query)
            print(f"🤖 JARVIS: {response}")
        
        # Test enhanced status
        print("\n📊 Enhanced Status Report:")
        status = jarvis.get_enhanced_status()
        
        print(f"Status: {status['status']}")
        print(f"Iron Man Mode: {status['iron_man_mode']}")
        print(f"Enhanced Features: {len(status['enhanced_features'])}")
        
        for feature in status['enhanced_features']:
            print(f"  ✅ {feature}")
        
        # Test memory and learning
        print(f"\nMemory: {len(jarvis.get_memory())} conversations stored")
        
        # Test feedback processing
        print("\n🎓 Testing Learning System...")
        learning_triggered = await jarvis.process_feedback(
            "hello", 
            "Good evening, Mr. Stark", 
            "excellent response"
        )
        print(f"Learning triggered: {learning_triggered}")
        
        print("\n✅ All Iron Man JARVIS features tested successfully!")
        print("🚀 JARVIS is ready to assist Mr. Stark!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_iron_man_jarvis())