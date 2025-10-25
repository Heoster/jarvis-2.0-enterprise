"""
Comprehensive test suite for enhanced JARVIS features.
Tests casual queries, technical prompts, mixed-language inputs, and voice-to-text errors.
"""

import pytest
import asyncio
from core.intent_classifier_enhanced import EnhancedIntentClassifier
from core.prompt_engine_enhanced import EnhancedPromptEngine
from storage.contextual_memory_enhanced import EnhancedContextualMemory
from core.semantic_matcher import SemanticMatcher
from core.sentiment_analyzer import SentimentAnalyzer
from core.query_decomposer import QueryDecomposer
from core.models import IntentCategory


class TestEnhancedIntentClassifier:
    """Test enhanced intent classification."""
    
    @pytest.fixture
    def classifier(self):
        return EnhancedIntentClassifier()
    
    @pytest.mark.asyncio
    async def test_casual_query(self, classifier):
        """Test casual conversational query."""
        intent = await classifier.classify("hey jarvis how are you doing today")
        assert intent.category == IntentCategory.CONVERSATIONAL
        assert intent.confidence > 0.7
    
    @pytest.mark.asyncio
    async def test_technical_query(self, classifier):
        """Test technical programming query."""
        intent = await classifier.classify("write a python function to implement binary search algorithm")
        assert intent.category == IntentCategory.CODE
        assert 'entities' in intent.parameters
    
    @pytest.mark.asyncio
    async def test_minecraft_modding_query(self, classifier):
        """Test Minecraft modding specific query."""
        intent = await classifier.classify("how do I create a custom block in forge 1.19")
        assert intent.category in [IntentCategory.CODE, IntentCategory.QUESTION]
        assert 'slots' in intent.parameters
        # Check for Minecraft version slot
        if 'minecraft_mod' in intent.parameters['slots']:
            assert len(intent.parameters['slots']['minecraft_mod']) > 0
    
    @pytest.mark.asyncio
    async def test_cli_command_detection(self, classifier):
        """Test CLI command detection."""
        intent = await classifier.classify("git clone the repository and npm install dependencies")
        assert intent.category == IntentCategory.COMMAND
        assert intent.parameters.get('cli_match') is not None
    
    @pytest.mark.asyncio
    async def test_math_query(self, classifier):
        """Test mathematical query."""
        intent = await classifier.classify("calculate the derivative of x squared plus 3x")
        assert intent.category == IntentCategory.MATH
        assert intent.confidence > 0.6
    
    @pytest.mark.asyncio
    async def test_voice_to_text_errors(self, classifier):
        """Test handling of voice-to-text errors."""
        # Common voice recognition errors
        intent = await classifier.classify("hlo jarvis wat is the whether")
        assert intent.category == IntentCategory.QUESTION
        # Should still classify correctly despite typos
    
    @pytest.mark.asyncio
    async def test_mixed_language_input(self, classifier):
        """Test mixed language/code input."""
        intent = await classifier.classify("explain this code: def factorial(n): return 1 if n == 0 else n * factorial(n-1)")
        assert intent.category in [IntentCategory.CODE, IntentCategory.QUESTION]
    
    @pytest.mark.asyncio
    async def test_compound_query(self, classifier):
        """Test compound query with multiple intents."""
        intent = await classifier.classify("search for python tutorials and then open vscode")
        # Should detect primary intent
        assert intent.category in [IntentCategory.FETCH, IntentCategory.COMMAND]
    
    @pytest.mark.asyncio
    async def test_slot_filling(self, classifier):
        """Test slot filling functionality."""
        intent = await classifier.classify("remind me at 3:30 PM to check the weather in New York")
        slots = intent.parameters.get('slots', {})
        assert 'time' in slots or 'location' in slots


class TestEnhancedPromptEngine:
    """Test enhanced prompt engineering."""
    
    @pytest.fixture
    def prompt_engine(self):
        return EnhancedPromptEngine()
    
    def test_magical_personality_integration(self, prompt_engine):
        """Test magical personality in prompts."""
        from core.models import Intent, IntentCategory
        intent = Intent(category=IntentCategory.QUESTION, confidence=0.9, parameters={}, context={})
        
        prompt = prompt_engine.build_prompt(
            query="What is machine learning?",
            intent=intent
        )
        
        assert "magical" in prompt.lower() or "✨" in prompt or "🌟" in prompt
    
    def test_few_shot_examples(self, prompt_engine):
        """Test few-shot example inclusion."""
        from core.models import Intent, IntentCategory
        intent = Intent(category=IntentCategory.CODE, confidence=0.9, parameters={}, context={})
        
        prompt = prompt_engine.build_prompt(
            query="How do I create a list in Python?",
            intent=intent
        )
        
        # Should include examples
        assert "example" in prompt.lower() or "```python" in prompt
    
    def test_chain_of_thought_prompt(self, prompt_engine):
        """Test chain-of-thought reasoning prompt."""
        steps = [
            "Understand the problem",
            "Break it into smaller parts",
            "Solve each part",
            "Combine the solutions"
        ]
        
        prompt = prompt_engine.create_chain_of_thought_prompt(
            "How do I implement quicksort?",
            steps
        )
        
        assert "step-by-step" in prompt.lower()
        assert all(step in prompt for step in steps)
    
    def test_context_aware_prompting(self, prompt_engine):
        """Test context-aware prompt building."""
        from core.models import Intent, IntentCategory, Document
        intent = Intent(category=IntentCategory.QUESTION, confidence=0.9, parameters={}, context={})
        
        context = {
            'context_docs': [
                Document(id='1', text='Machine learning is...', source='wiki', metadata={})
            ],
            'web_results': [
                {'title': 'ML Tutorial', 'content': 'Learn ML basics...'}
            ]
        }
        
        prompt = prompt_engine.build_prompt(
            query="What is machine learning?",
            intent=intent,
            context=context
        )
        
        assert "Machine learning" in prompt or "ML" in prompt


class TestEnhancedContextualMemory:
    """Test enhanced contextual memory."""
    
    @pytest.fixture
    def memory(self):
        return EnhancedContextualMemory(max_short_term_turns=3)
    
    @pytest.mark.asyncio
    async def test_short_term_memory(self, memory):
        """Test short-term memory (last 3 turns)."""
        await memory.add_interaction("Hello", "Hi there!", {})
        await memory.add_interaction("How are you?", "I'm great!", {})
        await memory.add_interaction("What's 2+2?", "It's 4!", {})
        await memory.add_interaction("Thanks", "You're welcome!", {})
        
        recent = memory.short_term.get_recent_turns()
        assert len(recent) == 3  # Should keep only last 3
        assert recent[-1]['user'] == "Thanks"
    
    @pytest.mark.asyncio
    async def test_preference_learning(self, memory):
        """Test user preference learning."""
        await memory.user_preferences.learn_preference(
            'explanation_style', 'use_examples', True, confidence=0.9
        )
        
        pref = await memory.user_preferences.get_preference('explanation_style', 'use_examples')
        assert pref == True
    
    @pytest.mark.asyncio
    async def test_topic_continuity(self, memory):
        """Test topic continuity tracking."""
        await memory.add_interaction("Tell me about Python", "Python is...", {'intent': 'python'})
        await memory.add_interaction("How do I use lists?", "Lists are...", {'intent': 'python'})
        await memory.add_interaction("What about dictionaries?", "Dictionaries...", {'intent': 'python'})
        
        assert memory.short_term.is_topic_continuation()
    
    @pytest.mark.asyncio
    async def test_learning_from_feedback(self, memory):
        """Test learning from user feedback."""
        context = {'used_examples': True}
        await memory.learn_from_feedback("That was really helpful and clear!", context)
        
        prefs = await memory.user_preferences.get_all_preferences()
        assert 'explanation_style' in prefs
    
    @pytest.mark.asyncio
    async def test_context_retrieval(self, memory):
        """Test context retrieval for queries."""
        await memory.add_interaction("What is Python?", "Python is a programming language", {})
        
        context = await memory.get_context_for_query("Tell me more about Python")
        assert 'short_term_history' in context
        assert 'user_preferences' in context
        assert len(context['short_term_history']) > 0


class TestSemanticMatcher:
    """Test semantic matching."""
    
    @pytest.fixture
    def matcher(self):
        return SemanticMatcher()
    
    @pytest.mark.asyncio
    async def test_similarity_computation(self, matcher):
        """Test semantic similarity computation."""
        sim = await matcher.compute_similarity(
            "How do I create a list in Python?",
            "What's the way to make a Python list?"
        )
        assert sim > 0.5  # Should be similar
    
    @pytest.mark.asyncio
    async def test_fuzzy_matching(self, matcher):
        """Test fuzzy intent matching."""
        intents = {
            'greeting': ['hello', 'hi', 'hey there', 'good morning'],
            'farewell': ['goodbye', 'bye', 'see you later'],
            'help': ['help me', 'I need assistance', 'can you help']
        }
        
        result = await matcher.fuzzy_match("hiya", intents, threshold=0.5)
        if result:
            assert result[0] == 'greeting'
    
    @pytest.mark.asyncio
    async def test_semantic_search(self, matcher):
        """Test semantic search over documents."""
        documents = [
            {'text': 'Python is a programming language', 'id': 1},
            {'text': 'Java is used for enterprise applications', 'id': 2},
            {'text': 'JavaScript runs in browsers', 'id': 3}
        ]
        
        results = await matcher.semantic_search(
            "Tell me about Python",
            documents,
            top_k=2
        )
        
        assert len(results) <= 2
        if results:
            assert 'similarity_score' in results[0]


class TestSentimentAnalyzer:
    """Test sentiment analysis."""
    
    @pytest.fixture
    def analyzer(self):
        return SentimentAnalyzer()
    
    def test_frustrated_sentiment(self, analyzer):
        """Test frustrated sentiment detection."""
        sentiment = analyzer.analyze("I don't understand this at all, it's too confusing!")
        assert sentiment['mood'] == 'frustrated'
        assert sentiment['confidence'] > 0.5
    
    def test_confident_sentiment(self, analyzer):
        """Test confident sentiment detection."""
        sentiment = analyzer.analyze("Got it! That makes perfect sense now.")
        assert sentiment['mood'] == 'confident'
    
    def test_excited_sentiment(self, analyzer):
        """Test excited sentiment detection."""
        sentiment = analyzer.analyze("This is awesome! I love learning this!")
        assert sentiment['mood'] == 'excited'
    
    def test_intensity_calculation(self, analyzer):
        """Test emotional intensity calculation."""
        sentiment = analyzer.analyze("I REALLY REALLY don't understand this!!!")
        assert sentiment['intensity'] > 1.5  # Should detect high intensity
    
    def test_tone_recommendation(self, analyzer):
        """Test tone recommendation based on sentiment."""
        sentiment = analyzer.analyze("I'm stuck and confused")
        recommendation = analyzer.get_tone_recommendation(sentiment)
        
        assert recommendation['approach'] == 'extra_supportive'
        assert 'suggestions' in recommendation


class TestQueryDecomposer:
    """Test query decomposition."""
    
    @pytest.fixture
    def decomposer(self):
        return QueryDecomposer()
    
    @pytest.mark.asyncio
    async def test_sequential_decomposition(self, decomposer):
        """Test sequential task decomposition."""
        tasks = await decomposer.decompose(
            "First explain Python lists, then show me how to sort them, and finally create a quiz"
        )
        
        assert len(tasks) >= 3
        assert tasks[0]['type'] == 'sequential'
        # Check dependencies
        for i, task in enumerate(tasks[1:], 1):
            assert i-1 in task['dependencies']
    
    @pytest.mark.asyncio
    async def test_parallel_decomposition(self, decomposer):
        """Test parallel task decomposition."""
        tasks = await decomposer.decompose(
            "Search for Python tutorials and Java documentation and JavaScript guides"
        )
        
        assert len(tasks) >= 3
        # Parallel tasks should have no dependencies
        for task in tasks:
            if task['type'] == 'parallel':
                assert len(task['dependencies']) == 0
    
    @pytest.mark.asyncio
    async def test_conditional_decomposition(self, decomposer):
        """Test conditional task decomposition."""
        tasks = await decomposer.decompose(
            "If the weather is good, then go outside"
        )
        
        assert len(tasks) == 2
        assert tasks[0]['type'] == 'condition'
        assert tasks[1]['type'] == 'conditional_action'
    
    @pytest.mark.asyncio
    async def test_comparison_decomposition(self, decomposer):
        """Test comparison query decomposition."""
        tasks = await decomposer.decompose(
            "Compare Python and Java programming languages"
        )
        
        assert len(tasks) == 3
        assert tasks[2]['type'] == 'comparison_synthesis'
        assert 1 in tasks[2]['dependencies']


class TestIntegration:
    """Integration tests for complete workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_query_flow(self):
        """Test complete query processing flow."""
        # Initialize components
        classifier = EnhancedIntentClassifier()
        prompt_engine = EnhancedPromptEngine()
        memory = EnhancedContextualMemory()
        
        # Process query
        query = "How do I create a custom Minecraft mod in Forge?"
        
        # Classify intent
        intent = await classifier.classify(query)
        assert intent.category in [IntentCategory.CODE, IntentCategory.QUESTION]
        
        # Get context
        context = await memory.get_context_for_query(query)
        assert 'user_preferences' in context
        
        # Build prompt
        prompt = prompt_engine.build_prompt(query, intent, context=context)
        assert len(prompt) > 0
        assert "Minecraft" in prompt or "mod" in prompt
        
        # Add to memory
        await memory.add_interaction(query, "Here's how to create a mod...", {'intent': 'minecraft_modding'})
        
        # Verify memory
        recent = memory.short_term.get_recent_turns()
        assert len(recent) == 1
    
    @pytest.mark.asyncio
    async def test_learning_adaptation(self):
        """Test system learning and adaptation."""
        memory = EnhancedContextualMemory()
        
        # Simulate multiple interactions with examples
        for i in range(5):
            await memory.add_interaction(
                f"Question {i}",
                f"Answer {i}",
                {'asked_for_example': True}
            )
        
        # Check if preference was learned
        prefs = await memory.user_preferences.get_all_preferences()
        assert 'explanation_style' in prefs
        
        # System should now prefer examples
        use_examples = await memory.user_preferences.get_preference('explanation_style', 'use_examples')
        assert use_examples == True
    
    @pytest.mark.asyncio
    async def test_error_recovery(self):
        """Test error handling and recovery."""
        classifier = EnhancedIntentClassifier()
        
        # Test with malformed input
        try:
            intent = await classifier.classify("")
            # Should handle gracefully
            assert intent is not None
        except Exception as e:
            pytest.fail(f"Should handle empty input gracefully: {e}")
        
        # Test with very long input
        long_query = "word " * 1000
        try:
            intent = await classifier.classify(long_query)
            assert intent is not None
        except Exception as e:
            pytest.fail(f"Should handle long input gracefully: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
