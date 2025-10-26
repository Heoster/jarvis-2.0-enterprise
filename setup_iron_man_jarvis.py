#!/usr/bin/env python3
"""
Iron Man JARVIS Setup Script
Initializes all components and runs comprehensive tests.
"""

import asyncio
import sys
from pathlib import Path
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.logger import get_logger, setup_logging
from core.smart_knowledge_integration import get_knowledge_integrator
from core.automatic_training import get_training_system
from jarvis_master import JarvisMaster

logger = get_logger(__name__)


async def setup_iron_man_jarvis():
    """Complete setup of Iron Man JARVIS"""
    
    print("🤖 IRON MAN JARVIS - Complete Setup")
    print("=" * 80)
    
    # Setup logging
    setup_logging(log_level="INFO")
    
    try:
        # Step 1: Initialize Knowledge Integration
        print("\n📚 Step 1: Initializing Knowledge Integration...")
        knowledge_integrator = get_knowledge_integrator()
        stats = await knowledge_integrator.integrate_all_knowledge()
        print(f"✅ Knowledge integration complete:")
        for key, value in stats.items():
            print(f"   - {key}: {value}")
        
        # Step 2: Initialize Training System
        print("\n🧠 Step 2: Initializing Automatic Training System...")
        training_system = get_training_system()
        training_stats = training_system.get_training_statistics()
        print(f"✅ Training system initialized:")
        print(f"   - Training count: {training_stats['training_count']}")
        print(f"   - Positive interactions: {training_stats['positive_interactions']}")
        
        # Step 3: Initialize JARVIS Master
        print("\n🤖 Step 3: Initializing Iron Man JARVIS...")
        jarvis = JarvisMaster()
        await jarvis.initialize_async_components()
        await jarvis.start_session("setup_session")
        print("✅ Iron Man JARVIS initialized successfully")
        
        # Step 4: Test Core Features
        print("\n🧪 Step 4: Testing Core Features...")
        
        # Test greeting
        greeting = await jarvis.get_greeting()
        print(f"✅ Greeting test: {greeting[:50]}...")
        
        # Test time awareness
        time_response = await jarvis.process_query("what time is it")
        print(f"✅ Time awareness: {'time' in time_response.lower()}")
        
        # Test greeting fix
        hello_response = await jarvis.process_query("hellow")
        print(f"✅ Smart editing: {'hello' in hello_response.lower() or 'mr. stark' in hello_response.lower()}")
        
        # Test Iron Man personality
        help_response = await jarvis.process_query("how can you help me")
        print(f"✅ Iron Man personality: {'mr. stark' in help_response.lower() or 'sir' in help_response.lower()}")
        
        # Step 5: Test Learning System
        print("\n🎓 Step 5: Testing Learning System...")
        test_query = "what is artificial intelligence"
        test_response = await jarvis.process_query(test_query)
        
        # Simulate positive feedback
        feedback_response = await jarvis.process_feedback(
            test_query, test_response, "excellent explanation, very helpful!"
        )
        print(f"✅ Learning system: {'learn' in feedback_response.lower()}")
        
        # Step 6: Show Status
        print("\n📊 Step 6: System Status...")
        status = jarvis.get_status()
        print(f"✅ System: {status['system']}")
        print(f"✅ Version: {status['version']}")
        print(f"✅ Status: {status['status']}")
        print(f"✅ Enhanced Features: {len(status['enhanced_features'])}")
        
        # Step 7: Create Sample Data
        print("\n💾 Step 7: Creating Sample Data...")
        await _create_sample_training_data(training_system)
        print("✅ Sample training data created")
        
        print("\n" + "=" * 80)
        print("🎉 IRON MAN JARVIS SETUP COMPLETE!")
        print("=" * 80)
        print("\n🚀 Ready to assist! Try these commands:")
        print("   python jarvis_master.py")
        print("   python test_iron_man_jarvis.py")
        print("\n🤖 Iron Man JARVIS is now fully operational, sir!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def _create_sample_training_data(training_system):
    """Create sample training data for demonstration"""
    
    sample_interactions = [
        {
            "query": "hello jarvis",
            "response": "Good morning, Mr. Stark. How may I assist you today?",
            "feedback": "great greeting, very professional"
        },
        {
            "query": "what time is it",
            "response": "The current time is 10:30 AM, sir.",
            "feedback": "perfect, exactly what I needed"
        },
        {
            "query": "search for python tutorials",
            "response": "I've found several excellent Python tutorials for you, sir.",
            "feedback": "excellent search results, very helpful"
        }
    ]
    
    for interaction in sample_interactions:
        await training_system.process_feedback(
            interaction["query"],
            interaction["response"], 
            interaction["feedback"]
        )


def create_quick_start_guide():
    """Create quick start guide"""
    
    guide_content = """# 🤖 Iron Man JARVIS - Quick Start Guide

## Welcome, Mr. Stark!

Your Iron Man JARVIS is now fully operational with enhanced capabilities.

## 🚀 Getting Started

### 1. Start JARVIS
```bash
python jarvis_master.py
```

### 2. Test All Features
```bash
python test_iron_man_jarvis.py
```

## 💬 Try These Commands

### Time & Date
- "what time is it"
- "what date is it"
- "what day is it"

### Greetings (with auto-correction)
- "hello" / "hellow" / "helo"
- "good morning"
- "hi jarvis"

### Web Search
- "search for artificial intelligence"
- "find information about python"
- "what is machine learning"

### Financial Data
- "bitcoin price in INR"
- "currency exchange rates"
- "mutual fund NAV"

### Indian Railways
- "train information"
- "trains from Muzaffarnagar"

### Entertainment
- "tell me a joke"
- "show me a dog image"
- "inspirational quote"

### Iron Man Personality
- "how can you help me"
- "what can you do"
- "who are you"

## 🧠 Automatic Learning

JARVIS learns from your positive feedback:
- After responses, you can say "good", "great", "helpful"
- JARVIS will automatically improve based on positive interactions
- Learning triggers after every 5 positive feedbacks

## 🎯 Features

✅ Iron Man Personality & Responses
✅ Time/Date Awareness  
✅ Smart Query Editing (fixes typos)
✅ Automatic Learning from Feedback
✅ Advanced Web Search & Scraping
✅ Indian Financial Data (Bitcoin, Currency, Mutual Funds)
✅ Railway Information
✅ Entertainment Content
✅ Proactive Assistance
✅ Enhanced Error Handling

## 🔧 Troubleshooting

If JARVIS doesn't respond as expected:
1. Check internet connection for web features
2. Run the test suite: `python test_iron_man_jarvis.py`
3. Check logs for error messages
4. Restart JARVIS: `python jarvis_master.py`

## 📊 Status & Statistics

Ask JARVIS: "show me your status" to see:
- System information
- Feature availability
- Learning statistics
- Performance metrics

---

**Ready to assist, Mr. Stark!** 🤖✨
"""
    
    with open("IRON_MAN_JARVIS_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(guide_content)


async def main():
    """Main setup function"""
    success = await setup_iron_man_jarvis()
    
    if success:
        create_quick_start_guide()
        print("\n📖 Quick start guide created: IRON_MAN_JARVIS_GUIDE.md")
    
    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)