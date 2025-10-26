#!/usr/bin/env python3
"""
Quick test for the enhanced Jarvis Brain
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_jarvis_brain():
    """Test the enhanced Jarvis Brain"""
    try:
        from core.jarvis_brain import JarvisBrain
        
        print("🧠 Initializing Enhanced Jarvis Brain...")
        jarvis = JarvisBrain()
        
        print("✅ Jarvis Brain initialized successfully!")
        
        # Test basic functionality
        print("\n🔍 Testing basic responses...")
        
        # Test greeting
        response = await jarvis.generate_response("hello")
        print(f"Greeting: {response}")
        
        # Test time query
        response = await jarvis.generate_response("what time is it")
        print(f"Time: {response}")
        
        # Test capabilities
        response = await jarvis.generate_response("what can you do")
        print(f"Capabilities: {response[:100]}...")
        
        # Test status
        status = jarvis.get_enhanced_status()
        print(f"\n📊 Status: {status['status']}")
        print(f"Features: {len(status['enhanced_features'])} enhanced features")
        
        print("\n✅ All tests passed! Enhanced Jarvis Brain is operational.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_jarvis_brain())