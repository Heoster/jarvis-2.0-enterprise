"""Decision engine for intent classification and context management."""

from typing import Dict, Any, List, Optional
from collections import deque

from core.models import Intent, IntentCategory, UserInput
from core.intent_classifier import IntentClassifier
from core.input_processor import InputProcessor, SemanticMatcher
from core.logger import get_logger

logger = get_logger(__name__)


class DecisionEngine:
    """Core decision engine for classifying intents and managing context."""
    
    def __init__(
        self,
        classifier: Optional[IntentClassifier] = None,
        context_window: int = 5,
        clarification_threshold: float = 0.15
    ):
        """
        Initialize decision engine.
        
        Args:
            classifier: Intent classifier instance
            context_window: Number of previous interactions to keep in context
            clarification_threshold: Confidence threshold below which to ask for clarification
        """
        self.classifier = classifier or IntentClassifier()
        self.context_window = context_window
        self.clarification_threshold = clarification_threshold
        
        # Initialize input processing
        self.input_processor = InputProcessor()
        self.semantic_matcher = SemanticMatcher()
        
        # Conversation context
        self.context_history: deque = deque(maxlen=context_window)
        self.current_context: Dict[str, Any] = {}
    
    async def classify_intent(self, user_input: UserInput) -> Intent:
        """
        Classify user intent with advanced processing.
        
        Args:
            user_input: User input object
            
        Returns:
            Intent object
        """
        # Preprocess input
        processed = self.input_processor.preprocess(user_input.text)
        
        if not processed['valid']:
            return Intent(
                category=IntentCategory.CONVERSATIONAL,
                confidence=0.1,
                parameters={},
                context={}
            )
        
        # Use pattern-based intent if confidence is high
        if processed['confidence'] >= 0.7:
            category = self._map_intent_to_category(processed['intent'])
            intent = Intent(
                category=category,
                confidence=processed['confidence'],
                parameters=processed['entities'],
                context={'preprocessed': processed}
            )
        else:
            # Fallback to ML classifier
            intent = await self.classifier.classify(processed['normalized'])
        
        # Add context information
        intent.context = self._build_context()
        intent.context['preprocessed'] = processed
        
        # Update context history
        self._update_context(user_input, intent)
        
        logger.info(f"Classified intent: {intent.category.value} (confidence: {intent.confidence:.2f})")
        
        return intent
    
    def _map_intent_to_category(self, intent: str) -> IntentCategory:
        """Map string intent to IntentCategory."""
        mapping = {
            'greeting': IntentCategory.CONVERSATIONAL,
            'farewell': IntentCategory.CONVERSATIONAL,
            'thanks': IntentCategory.CONVERSATIONAL,
            'question': IntentCategory.QUESTION,
            'command': IntentCategory.COMMAND,
            'math': IntentCategory.MATH,
            'search': IntentCategory.FETCH,
            'weather': IntentCategory.QUESTION,
            'news': IntentCategory.FETCH,
            'unknown': IntentCategory.CONVERSATIONAL
        }
        return mapping.get(intent, IntentCategory.CONVERSATIONAL)
    
    def _build_context(self) -> Dict[str, Any]:
        """Build context from conversation history."""
        context = {
            'previous_intents': [
                item['intent'].category.value
                for item in self.context_history
                if 'intent' in item
            ],
            'conversation_length': len(self.context_history),
            **self.current_context
        }
        
        return context
    
    def _update_context(self, user_input: UserInput, intent: Intent) -> None:
        """Update conversation context."""
        # Add to history
        self.context_history.append({
            'user_input': user_input.text,
            'intent': intent,
            'timestamp': user_input.timestamp
        })
        
        # Store current user input for ambiguity checking
        self.current_context['user_input'] = user_input.text
        
        # Update current context based on intent
        if intent.category == IntentCategory.COMMAND:
            self.current_context['last_command'] = intent.parameters.get('action')
        
        elif intent.category == IntentCategory.QUESTION:
            self.current_context['last_question_type'] = intent.parameters.get('question_type')
    
    def get_confidence(self, intent: Intent) -> float:
        """
        Get confidence score for an intent.
        
        Args:
            intent: Intent object
            
        Returns:
            Confidence score (0-1)
        """
        return intent.confidence
    
    def should_clarify(self, intent: Intent) -> bool:
        """
        Determine if clarification is needed.
        
        Args:
            intent: Intent object
            
        Returns:
            True if clarification should be requested
        """
        # Check if confidence is below threshold
        if intent.confidence < self.clarification_threshold:
            logger.info(f"Low confidence ({intent.confidence:.2f}), clarification needed")
            return True
        
        # Check for ambiguous patterns
        if self._is_ambiguous(intent):
            logger.info("Ambiguous intent detected, clarification needed")
            return True
        
        return False
    
    def _is_ambiguous(self, intent: Intent) -> bool:
        """Check if intent is ambiguous."""
        # Check if multiple intents have similar probabilities
        # This would require access to all probabilities from classifier
        # For now, use simple heuristics
        
        # Don't treat conversational intents as ambiguous
        if intent.category == IntentCategory.CONVERSATIONAL:
            return False
        
        # If it's a very short input (1-2 words) and not conversational, it might be ambiguous
        if 'user_input' in self.current_context:
            text = self.current_context['user_input']
            word_count = len(text.split())
            
            # Single word inputs that are not greetings/farewells/thanks are ambiguous
            if word_count <= 1:
                # Check if it's a known conversational pattern
                preprocessed = intent.context.get('preprocessed', {})
                if preprocessed.get('intent') in ['greeting', 'farewell', 'thanks']:
                    return False
                return True
        
        return False
    
    def update_context(self, key: str, value: Any) -> None:
        """
        Manually update context.
        
        Args:
            key: Context key
            value: Context value
        """
        self.current_context[key] = value
        logger.debug(f"Updated context: {key} = {value}")
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get current context.
        
        Returns:
            Context dictionary
        """
        return self.current_context.copy()
    
    def clear_context(self) -> None:
        """Clear conversation context."""
        self.context_history.clear()
        self.current_context.clear()
        logger.info("Cleared conversation context")
    
    def get_context_summary(self) -> str:
        """
        Get a human-readable summary of the context.
        
        Returns:
            Context summary string
        """
        if not self.context_history:
            return "No conversation history"
        
        summary_parts = []
        summary_parts.append(f"Conversation length: {len(self.context_history)} turns")
        
        if 'last_command' in self.current_context:
            summary_parts.append(f"Last command: {self.current_context['last_command']}")
        
        if 'last_question_type' in self.current_context:
            summary_parts.append(f"Last question type: {self.current_context['last_question_type']}")
        
        return " | ".join(summary_parts)
