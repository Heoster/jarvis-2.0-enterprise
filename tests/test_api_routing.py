"""
Tests for Intelligent API Routing
"""

import pytest
import asyncio
from core.api_router import get_api_router, APIEndpoint


class TestIntentDetection:
    """Test intent detection accuracy"""
    
    def setup_method(self):
        """Setup test router"""
        self.router = get_api_router()
    
    def test_grammar_correction_detection(self):
        """Test grammar correction intent detection"""
        test_cases = [
            "correct this sentence: hlo how r u",
            "fix my grammar",
            "is this spelled correctly",
            "check my writing",
            "/correct test"
        ]
        
        for text in test_cases:
            endpoint = self.router._detect_endpoint(text, None)
            assert endpoint == APIEndpoint.CORRECT, f"Failed for: {text}"
    
    def test_quiz_creation_detection(self):
        """Test quiz creation intent detection"""
        test_cases = [
            "quiz me on Python",
            "start a test",
            "I want to take a quiz",
            "test my knowledge",
            "/quiz python 5"
        ]
        
        for text in test_cases:
            endpoint = self.router._detect_endpoint(text, None)
            assert endpoint == APIEndpoint.QUIZ_CREATE, f"Failed for: {text}"
    
    def test_quiz_topics_detection(self):
        """Test quiz topics intent detection"""
        test_cases = [
            "what quiz topics are available",
            "list quiz subjects",
            "show quiz options",
            "/quiz topics"
        ]
        
        for text in test_cases:
            endpoint = self.router._detect_endpoint(text, None)
            assert endpoint == APIEndpoint.QUIZ_TOPICS, f"Failed for: {text}"
    
    def test_quiz_stats_detection(self):
        """Test quiz stats intent detection"""
        test_cases = [
            "my quiz stats",
            "how am I doing on quizzes",
            "show my quiz performance",
            "/quiz stats"
        ]
        
        for text in test_cases:
            endpoint = self.router._detect_endpoint(text, None)
            assert endpoint == APIEndpoint.QUIZ_STATS, f"Failed for: {text}"
    
    def test_feedback_detection(self):
        """Test feedback intent detection"""
        test_cases = [
            "that was helpful",
            "good response",
            "great explanation",
            "/feedback positive"
        ]
        
        for text in test_cases:
            endpoint = self.router._detect_endpoint(text, None)
            assert endpoint == APIEndpoint.FEEDBACK, f"Failed for: {text}"
    
    def test_quiz_answer_detection(self):
        """Test quiz answer detection with context"""
        context = {'active_quiz_id': 'quiz_123'}
        
        test_cases = ["1", "2", "3", "4"]
        
        for text in test_cases:
            endpoint = self.router._detect_endpoint(text, context)
            assert endpoint == APIEndpoint.QUIZ_ANSWER, f"Failed for: {text}"
    
    def test_no_detection(self):
        """Test cases that should not match any endpoint"""
        test_cases = [
            "hello",
            "what is 2+2",
            "tell me about Python",
            "how are you"
        ]
        
        for text in test_cases:
            endpoint = self.router._detect_endpoint(text, None)
            assert endpoint is None, f"False positive for: {text}"


class TestPatternMatching:
    """Test pattern matching logic"""
    
    def setup_method(self):
        """Setup test router"""
        self.router = get_api_router()
    
    def test_grammar_patterns(self):
        """Test grammar correction patterns"""
        patterns = [
            "correct my sentence",
            "fix this grammar",
            "check spelling",
            "is this correct"
        ]
        
        for text in patterns:
            matches = self.router._matches_pattern(text.lower(), APIEndpoint.CORRECT)
            assert matches, f"Pattern should match: {text}"
    
    def test_quiz_patterns(self):
        """Test quiz creation patterns"""
        patterns = [
            "quiz me on Python",
            "start a test",
            "test my knowledge",
            "begin quiz"
        ]
        
        for text in patterns:
            matches = self.router._matches_pattern(text.lower(), APIEndpoint.QUIZ_CREATE)
            assert matches, f"Pattern should match: {text}"


class TestContextAwareness:
    """Test context-aware routing"""
    
    def setup_method(self):
        """Setup test router"""
        self.router = get_api_router()
    
    def test_active_quiz_context(self):
        """Test routing with active quiz"""
        context = {'active_quiz_id': 'quiz_123'}
        
        # Numeric input should route to quiz answer
        endpoint = self.router._detect_endpoint("1", context)
        assert endpoint == APIEndpoint.QUIZ_ANSWER
        
        # Non-numeric should not
        endpoint = self.router._detect_endpoint("hello", context)
        assert endpoint != APIEndpoint.QUIZ_ANSWER
    
    def test_no_active_quiz(self):
        """Test routing without active quiz"""
        context = {}
        
        # Numeric input should not route to quiz answer
        endpoint = self.router._detect_endpoint("1", context)
        assert endpoint != APIEndpoint.QUIZ_ANSWER


class TestKeywordTriggers:
    """Test keyword-based triggers"""
    
    def setup_method(self):
        """Setup test router"""
        self.router = get_api_router()
    
    def test_keyword_detection(self):
        """Test keyword triggers"""
        test_cases = {
            'correct': APIEndpoint.CORRECT,
            'quiz': APIEndpoint.QUIZ_CREATE,
            'feedback': APIEndpoint.FEEDBACK,
        }
        
        for keyword, expected_endpoint in test_cases.items():
            text = f"I want to {keyword} something"
            endpoint = self.router._detect_endpoint(text, None)
            # Should detect the endpoint (may need pattern verification)
            assert endpoint is not None, f"Should detect endpoint for: {keyword}"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def setup_method(self):
        """Setup test router"""
        self.router = get_api_router()
    
    def test_empty_input(self):
        """Test empty input"""
        endpoint = self.router._detect_endpoint("", None)
        assert endpoint is None
    
    def test_very_short_input(self):
        """Test very short input"""
        endpoint = self.router._detect_endpoint("a", None)
        assert endpoint is None
    
    def test_mixed_case(self):
        """Test case insensitivity"""
        test_cases = [
            "CORRECT THIS",
            "Quiz Me",
            "FeedBack"
        ]
        
        for text in test_cases:
            endpoint = self.router._detect_endpoint(text, None)
            assert endpoint is not None, f"Should handle case: {text}"
    
    def test_special_characters(self):
        """Test input with special characters"""
        text = "correct this: hello!!! how are you???"
        endpoint = self.router._detect_endpoint(text, None)
        assert endpoint == APIEndpoint.CORRECT


class TestSuggestions:
    """Test endpoint suggestions"""
    
    def setup_method(self):
        """Setup test router"""
        self.router = get_api_router()
    
    def test_get_suggestion(self):
        """Test getting suggestions"""
        text = "I want to correct something"
        suggestion = self.router.get_endpoint_suggestion(text)
        assert suggestion is not None
        assert "correct" in suggestion.lower()
    
    def test_no_suggestion(self):
        """Test no suggestion for general queries"""
        text = "hello how are you"
        suggestion = self.router.get_endpoint_suggestion(text)
        assert suggestion is None


# Integration tests (require running server)
@pytest.mark.asyncio
@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests with actual API calls"""
    
    async def test_full_routing_flow(self):
        """Test complete routing flow"""
        router = get_api_router()
        
        # This would require a running server
        # Skipping actual API calls in unit tests
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
