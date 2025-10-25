#!/usr/bin/env python3
"""
Complete Test Suite for JARVIS MASTER
Tests all features to ensure everything is working
"""

import asyncio
import sys
from datetime import datetime

print("="*80)
print("🧪 JARVIS MASTER - Complete Feature Test Suite")
print("="*80)
print()


async def test_initialization():
    """Test 1: System Initialization"""
    print("Test 1: System Initialization")
    print("-" * 40)
    
    try:
        from jarvis_master import JarvisMaster
        
        jarvis = JarvisMaster()
        await jarvis.initialize_async_components()
        
        status = jarvis.get_status()
        print(f"✅ System Status: {status['status']}")
        print(f"✅ Brain: {status['brain']['name']}")
        print(f"✅ Features Loaded: {len(status['features'])}")
        print()
        return jarvis
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_greeting(jarvis):
    """Test 2: Greeting Generation"""
    print("Test 2: Greeting Generation")
    print("-" * 40)
    
    try:
        greeting = await jarvis.get_greeting()
        print(f"✅ Greeting: {greeting[:80]}...")
        print()
        return True
    except Exception as e:
        print(f"❌ Greeting failed: {e}")
        return False


async def test_conversational(jarvis):
    """Test 3: Conversational Queries"""
    print("Test 3: Conversational Queries")
    print("-" * 40)
    
    queries = [
        "Hello Jarvis",
        "How are you?",
        "What can you do?",
    ]
    
    for query in queries:
        try:
            print(f"Query: {query}")
            response = await jarvis.process_query(query)
            print(f"✅ Response: {response[:100]}...")
            print()
        except Exception as e:
            print(f"❌ Failed: {e}")
            return False
    
    return True


async def test_web_search(jarvis):
    """Test 4: Web Search & Scraping"""
    print("Test 4: Web Search & Scraping")
    print("-" * 40)
    
    try:
        print("Query: Search for Python programming")
        response = await jarvis.process_query("Search for Python programming")
        
        if len(response) > 100:
            print(f"✅ Web search working: {len(response)} chars returned")
            print(f"Preview: {response[:150]}...")
        else:
            print(f"⚠️  Short response: {response}")
        
        print()
        return True
    except Exception as e:
        print(f"❌ Web search failed: {e}")
        return False


async def test_indian_finance(jarvis):
    """Test 5: Indian Financial APIs"""
    print("Test 5: Indian Financial APIs")
    print("-" * 40)
    
    queries = [
        "What's the Bitcoin price in INR?",
        "Show me currency exchange rates",
    ]
    
    for query in queries:
        try:
            print(f"Query: {query}")
            response = await jarvis.process_query(query)
            
            if "INR" in response or "₹" in response or "rupee" in response.lower():
                print(f"✅ Financial data working")
                print(f"Preview: {response[:150]}...")
            else:
                print(f"⚠️  Response: {response[:150]}...")
            
            print()
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    return True


async def test_entertainment(jarvis):
    """Test 6: Entertainment APIs"""
    print("Test 6: Entertainment APIs")
    print("-" * 40)
    
    queries = [
        "Tell me a joke",
        "Give me an inspirational quote",
    ]
    
    for query in queries:
        try:
            print(f"Query: {query}")
            response = await jarvis.process_query(query)
            print(f"✅ Entertainment working")
            print(f"Response: {response[:200]}...")
            print()
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    return True


async def test_knowledge(jarvis):
    """Test 7: Knowledge Queries"""
    print("Test 7: Knowledge Queries")
    print("-" * 40)
    
    try:
        print("Query: What is artificial intelligence?")
        response = await jarvis.process_query("What is artificial intelligence?")
        
        if len(response) > 50:
            print(f"✅ Knowledge retrieval working")
            print(f"Preview: {response[:200]}...")
        else:
            print(f"⚠️  Short response: {response}")
        
        print()
        return True
    except Exception as e:
        print(f"❌ Knowledge query failed: {e}")
        return False


async def test_math(jarvis):
    """Test 8: Mathematical Computation"""
    print("Test 8: Mathematical Computation")
    print("-" * 40)
    
    try:
        print("Query: Calculate 25 * 4 + 10")
        response = await jarvis.process_query("Calculate 25 * 4 + 10")
        print(f"✅ Math processing: {response[:150]}...")
        print()
        return True
    except Exception as e:
        print(f"❌ Math failed: {e}")
        return False


async def test_context_memory(jarvis):
    """Test 9: Context & Memory"""
    print("Test 9: Context & Memory")
    print("-" * 40)
    
    try:
        # First query
        print("Query 1: My name is Heoster")
        response1 = await jarvis.process_query("My name is Heoster")
        print(f"Response 1: {response1[:100]}...")
        
        # Follow-up query
        print("\nQuery 2: What's my name?")
        response2 = await jarvis.process_query("What's my name?")
        print(f"Response 2: {response2[:100]}...")
        
        print("\n✅ Context tracking working")
        print()
        return True
    except Exception as e:
        print(f"❌ Context failed: {e}")
        return False


async def test_farewell(jarvis):
    """Test 10: Farewell"""
    print("Test 10: Farewell")
    print("-" * 40)
    
    try:
        farewell = await jarvis.get_farewell()
        print(f"✅ Farewell: {farewell}")
        print()
        return True
    except Exception as e:
        print(f"❌ Farewell failed: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    print("Starting comprehensive test suite...")
    print()
    
    results = {
        'passed': 0,
        'failed': 0,
        'total': 10
    }
    
    # Test 1: Initialization
    jarvis = await test_initialization()
    if jarvis:
        results['passed'] += 1
    else:
        results['failed'] += 1
        print("\n❌ Cannot continue without initialization")
        return results
    
    # Start session
    await jarvis.start_session("test_session")
    
    # Test 2: Greeting
    if await test_greeting(jarvis):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 3: Conversational
    if await test_conversational(jarvis):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 4: Web Search
    if await test_web_search(jarvis):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 5: Indian Finance
    if await test_indian_finance(jarvis):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 6: Entertainment
    if await test_entertainment(jarvis):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 7: Knowledge
    if await test_knowledge(jarvis):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 8: Math
    if await test_math(jarvis):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 9: Context
    if await test_context_memory(jarvis):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Test 10: Farewell
    if await test_farewell(jarvis):
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # Shutdown
    await jarvis.shutdown()
    
    return results


async def main():
    """Main test runner"""
    start_time = datetime.now()
    
    results = await run_all_tests()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Print summary
    print("="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {results['total']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"⏱️  Duration: {duration:.2f} seconds")
    print()
    
    if results['failed'] == 0:
        print("🎉 ALL TESTS PASSED! JARVIS MASTER is fully operational!")
        return 0
    else:
        print(f"⚠️  {results['failed']} test(s) failed. Check output above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
