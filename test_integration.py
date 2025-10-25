"""
Integration Test Suite for JARVIS Complete
Tests the unified system with all components
"""

import asyncio
import sys

print("🧪 JARVIS Complete - Integration Test Suite")
print("="*80)
print()

async def test_imports():
    """Test 1: Verify all imports work"""
    print("Test 1: Checking imports...")
    try:
        from core.jarvis_unified import get_jarvis_unified
        from core.jarvis_brain import JarvisBrain
        from core.intent_classifier_enhanced import EnhancedIntentClassifier
        from core.prompt_engine_enhanced import EnhancedPromptEngine
        from storage.contextual_memory_enhanced import EnhancedContextualMemory
        from core.sentiment_analyzer import SentimentAnalyzer
        from core.query_decomposer import QueryDecomposer
        from core.semantic_matcher import SemanticMatcher
        print("  ✅ All imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

async def test_enhanced_components():
    """Test 2: Verify enhanced components initialize"""
    print("\nTest 2: Initializing enhanced components...")
    try:
        from core.intent_classifier_enhanced import EnhancedIntentClassifier
        from core.sentiment_analyzer import SentimentAnalyzer
        from storage.contextual_memory_enhanced import EnhancedContextualMemory
        
        classifier = EnhancedIntentClassifier()
        sentiment = SentimentAnalyzer()
        memory = EnhancedContextualMemory()
        
        print("  ✅ Enhanced components initialized")
        return True
    except Exception as e:
        print(f"  ❌ Initialization failed: {e}")
        return False

async def test_intent_classification():
    """Test 3: Test intent classification"""
    print("\nTest 3: Testing intent classification...")
    try:
        from core.intent_classifier_enhanced import EnhancedIntentClassifier
        
        classifier = EnhancedIntentClassifier()
        
        test_queries = [
            ("hello", "conversational"),
            ("what is python", "question"),
            ("search for AI", "fetch"),
        ]
        
        passed = 0
        for query, expected in test_queries:
            intent = await classifier.classify(query)
            if intent.category.value == expected:
                print(f"  ✅ '{query}' → {intent.category.value}")
                passed += 1
            else:
                print(f"  ⚠️  '{query}' → {intent.category.value} (expected {expected})")
        
        print(f"  Result: {passed}/{len(test_queries)} passed")
        return passed == len(test_queries)
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

async def test_sentiment_analysis():
    """Test 4: Test sentiment analysis"""
    print("\nTest 4: Testing sentiment analysis...")
    try:
        from core.sentiment_analyzer import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer()
        
        test_cases = [
            ("I'm confused and frustrated", "frustrated"),
            ("This is awesome!", "excited"),
            ("Got it, thanks", "confident"),
        ]
        
        passed = 0
        for text, expected_mood in test_cases:
            sentiment = analyzer.analyze(text)
            if sentiment['mood'] == expected_mood:
                print(f"  ✅ '{text}' → {sentiment['mood']}")
                passed += 1
            else:
                print(f"  ⚠️  '{text}' → {sentiment['mood']} (expected {expected_mood})")
        
        print(f"  Result: {passed}/{len(test_cases)} passed")
        return passed >= len(test_cases) - 1  # Allow 1 failure
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

async def test_contextual_memory():
    """Test 5: Test contextual memory"""
    print("\nTest 5: Testing contextual memory...")
    try:
        from storage.contextual_memory_enhanced import EnhancedContextualMemory
        
        memory = EnhancedContextualMemory()
        memory.start_session("test_session")
        
        # Add interactions
        await memory.add_interaction("Hello", "Hi there!", {})
        await memory.add_interaction("How are you?", "I'm great!", {})
        
        # Get context
        context = await memory.get_context_for_query("test")
        
        if len(context['short_term_history']) == 2:
            print("  ✅ Memory storing interactions correctly")
            return True
        else:
            print(f"  ⚠️  Expected 2 interactions, got {len(context['short_term_history'])}")
            return False
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

async def test_unified_jarvis():
    """Test 6: Test unified JARVIS"""
    print("\nTest 6: Testing unified JARVIS...")
    try:
        from core.jarvis_unified import get_jarvis_unified
        
        jarvis = await get_jarvis_unified()
        await jarvis.start_session("test_unified")
        
        # Test query processing
        response = await jarvis.process_query("hello")
        
        if response and len(response) > 0:
            print(f"  ✅ Unified JARVIS responding")
            print(f"     Response: {response[:100]}...")
            return True
        else:
            print("  ⚠️  Empty response")
            return False
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_original_brain():
    """Test 7: Test original JARVIS brain"""
    print("\nTest 7: Testing original JARVIS brain...")
    try:
        from core.jarvis_brain import JarvisBrain
        
        brain = JarvisBrain()
        response = await brain.generate_response("hello")
        
        if response and len(response) > 0:
            print(f"  ✅ Original brain responding")
            print(f"     Response: {response[:100]}...")
            return True
        else:
            print("  ⚠️  Empty response")
            return False
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

async def test_query_decomposition():
    """Test 8: Test query decomposition"""
    print("\nTest 8: Testing query decomposition...")
    try:
        from core.query_decomposer import QueryDecomposer
        
        decomposer = QueryDecomposer()
        
        complex_query = "First search for Python, then summarize it, and create a quiz"
        tasks = await decomposer.decompose(complex_query)
        
        if len(tasks) >= 3:
            print(f"  ✅ Decomposed into {len(tasks)} tasks")
            for i, task in enumerate(tasks, 1):
                print(f"     {i}. {task['task'][:50]}")
            return True
        else:
            print(f"  ⚠️  Expected 3+ tasks, got {len(tasks)}")
            return False
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

async def run_all_tests():
    """Run all integration tests"""
    tests = [
        test_imports,
        test_enhanced_components,
        test_intent_classification,
        test_sentiment_analysis,
        test_contextual_memory,
        test_unified_jarvis,
        test_original_brain,
        test_query_decomposition,
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*80)
    print("📊 Test Summary")
    print("="*80)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Passed: {passed}/{total} ({percentage:.1f}%)")
    print()
    
    if passed == total:
        print("✅ All tests passed! JARVIS Complete is fully operational!")
    elif passed >= total * 0.75:
        print("⚠️  Most tests passed. System is operational with minor issues.")
    else:
        print("❌ Multiple tests failed. System needs attention.")
    
    print()
    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
