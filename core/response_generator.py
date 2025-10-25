"""Response generation with personality and templates."""

from typing import List, Dict, Any, Optional
from jinja2 import Template

from core.models import Document, Intent, IntentCategory
from core.logger import get_logger

logger = get_logger(__name__)


class ResponseGenerator:
    """Generates friendly, context-aware responses."""
    
    def __init__(self, personality: str = "friendly"):
        """
        Initialize response generator.
        
        Args:
            personality: Response personality style
        """
        self.personality = personality
        self.templates = self._create_templates()
    
    def _create_templates(self) -> Dict[str, Template]:
        """Create response templates."""
        return {
            'command_executed': Template("{{ action }} {{ target }}{% if success %} successfully{% else %} - there was an issue{% endif %}."),
            'answer': Template("{{ answer }}{% if sources %}\n\nSources: {{ sources }}{% endif %}"),
            'math_result': Template("The answer is {{ result }}.{% if steps %}\n\nSteps:\n{{ steps }}{% endif %}"),
            'code_result': Template("{% if success %}Here's the result:\n{{ output }}{% else %}Error: {{ error }}{% endif %}"),
            'fetch_result': Template("{{ content }}"),
            'conversational': Template("{{ response }}"),
            'error': Template("I'm sorry, {{ error_message }}. {{ suggestion }}"),
            'clarification': Template("I'm not sure I understand. Did you mean {{ options }}?"),
        }
    
    async def generate(
        self,
        intent: Intent,
        context: Dict[str, Any],
        sources: Optional[List[Document]] = None,
        ai_response: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate response based on intent and context.
        
        Args:
            intent: Classified intent
            context: Response context
            sources: Source documents
            ai_response: AI-generated response (optional)
            
        Returns:
            Response dictionary
        """
        # If AI response is provided, use it as primary response
        if ai_response:
            text = ai_response
            confidence = context.get('confidence', 0.8)
        else:
            # Select template
            template_name = self._select_template(intent, context)
            template = self.templates.get(template_name)
            
            if not template:
                return {
                    'text': context.get('text', 'I processed your request.'),
                    'confidence': 0.5,
                    'sources': sources or []
                }
            
            # Prepare template variables
            template_vars = self._prepare_variables(intent, context, sources)
            
            # Apply personality
            template_vars = self.apply_personality(template_vars)
            
            # Render template
            try:
                text = template.render(**template_vars)
            except Exception as e:
                logger.error(f"Template rendering failed: {e}")
                text = "I processed your request."
            
            confidence = context.get('confidence', 0.8)
        
        # Add suggestions
        suggestions = self.add_suggestions(intent, context)
        
        return {
            'text': text,
            'confidence': confidence,
            'sources': sources or [],
            'suggestions': suggestions,
            'metadata': {
                'intent': intent.category.value,
                'template': 'ai_generated' if ai_response else self._select_template(intent, context)
            }
        }
    
    def _select_template(self, intent: Intent, context: Dict[str, Any]) -> str:
        """Select appropriate template."""
        if context.get('error'):
            return 'error'
        
        if intent.category == IntentCategory.COMMAND:
            return 'command_executed'
        elif intent.category == IntentCategory.QUESTION:
            return 'answer'
        elif intent.category == IntentCategory.MATH:
            return 'math_result'
        elif intent.category == IntentCategory.CODE:
            return 'code_result'
        elif intent.category == IntentCategory.FETCH:
            return 'fetch_result'
        else:
            return 'conversational'
    
    def _prepare_variables(
        self,
        intent: Intent,
        context: Dict[str, Any],
        sources: Optional[List[Document]]
    ) -> Dict[str, Any]:
        """Prepare template variables."""
        variables = {
            'personality': self.personality,
            **context
        }
        
        # Add source attribution
        if sources:
            source_text = ', '.join([f"{s.source}" for s in sources[:3]])
            variables['sources'] = source_text
        
        return variables
    
    def apply_personality(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Apply personality adjustments to variables."""
        personality = variables.get('personality', self.personality)
        
        if personality == 'sophisticated':
            # Jarvis-style: professional yet personable
            if 'action' in variables:
                variables['action'] = self._make_sophisticated(variables['action'])
            if 'response' in variables:
                variables['response'] = self._make_sophisticated(variables['response'])
        
        elif personality == 'friendly':
            # Add friendly touches
            if 'action' in variables:
                variables['action'] = self._make_friendly(variables['action'])
        
        elif personality == 'formal':
            # Make more formal
            if 'response' in variables:
                variables['response'] = self._make_formal(variables['response'])
        
        return variables
    
    def _make_friendly(self, text: str) -> str:
        """Add friendly tone."""
        friendly_prefixes = {
            'opening': 'Opening',
            'closing': 'Closing',
            'starting': 'Starting',
            'setting': 'Setting'
        }
        
        for key, value in friendly_prefixes.items():
            if text.lower().startswith(key):
                return value
        
        return text.capitalize()
    
    def _make_formal(self, text: str) -> str:
        """Make text more formal."""
        # Simple formalization (could be enhanced)
        return text.replace("I'm", "I am").replace("can't", "cannot")
    
    def _make_sophisticated(self, text: str) -> str:
        """Make text sophisticated (Jarvis-style)."""
        # Professional yet personable
        text = text.replace("I'm", "I am").replace("can't", "cannot")
        
        # Add subtle sophistication
        replacements = {
            "ok": "very well",
            "sure": "certainly",
            "yeah": "indeed",
            "nope": "I'm afraid not",
            "dunno": "I'm uncertain"
        }
        
        text_lower = text.lower()
        for old, new in replacements.items():
            if old in text_lower:
                text = text.replace(old, new)
        
        return text
    
    def add_suggestions(self, intent: Intent, context: Dict[str, Any]) -> List[str]:
        """
        Generate follow-up suggestions.
        
        Args:
            intent: User intent
            context: Response context
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        if intent.category == IntentCategory.QUESTION:
            suggestions.extend([
                "Would you like more details?",
                "Should I search for related information?"
            ])
        
        elif intent.category == IntentCategory.COMMAND:
            suggestions.extend([
                "Anything else I can help with?"
            ])
        
        elif intent.category == IntentCategory.MATH:
            suggestions.extend([
                "Would you like to see the steps?",
                "Need help with another calculation?"
            ])
        
        return suggestions[:2]  # Limit to 2 suggestions
    
    def generate_error_response(
        self,
        error_message: str,
        suggestion: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate error response.
        
        Args:
            error_message: Error description
            suggestion: Suggested action
            
        Returns:
            Error response dictionary
        """
        template = self.templates['error']
        
        text = template.render(
            error_message=error_message,
            suggestion=suggestion or "Please try again."
        )
        
        return {
            'text': text,
            'confidence': 0.0,
            'sources': [],
            'suggestions': ["Try rephrasing your request"],
            'metadata': {'error': True}
        }
    
    def generate_clarification_request(
        self,
        options: List[str]
    ) -> Dict[str, Any]:
        """
        Generate clarification request.
        
        Args:
            options: Possible interpretations
            
        Returns:
            Clarification response
        """
        template = self.templates['clarification']
        
        options_text = " or ".join(options)
        text = template.render(options=options_text)
        
        return {
            'text': text,
            'confidence': 0.0,
            'sources': [],
            'suggestions': options,
            'metadata': {'clarification': True}
        }
