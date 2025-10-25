"""Prompt engineering and template management."""

from typing import Dict, Any, List, Optional
from jinja2 import Template

from core.models import Intent, IntentCategory, Document
from core.logger import get_logger

logger = get_logger(__name__)


class PromptEngine:
    """Manages prompts and templates for LLM generation."""
    
    def __init__(self, personality: str = "friendly"):
        """
        Initialize prompt engine.
        
        Args:
            personality: Assistant personality style
        """
        self.personality = personality
        self.system_prompts = self._create_system_prompts()
        self.templates = self._create_templates()
    
    def _create_system_prompts(self) -> Dict[str, str]:
        """Create system prompts for different personalities."""
        prompts = {
            "friendly": """You are a helpful, friendly AI assistant. You provide clear, accurate, and conversational responses. 
You are knowledgeable but humble, and you admit when you don't know something. 
Keep responses concise but informative. Use a warm, approachable tone.""",
            
            "formal": """You are a professional AI assistant. You provide precise, well-structured responses.
You maintain a formal but helpful tone. You cite sources when available and provide detailed explanations.""",
            
            "concise": """You are an efficient AI assistant. You provide direct, to-the-point answers.
You avoid unnecessary elaboration while ensuring accuracy. You use clear, simple language."""
        }
        
        return prompts
    
    def _create_templates(self) -> Dict[str, Template]:
        """Create Jinja2 templates for different query types."""
        templates = {
            "question": Template("""Based on the following context, answer the question.

Context:
{% for doc in context_docs %}
- {{ doc.text }} (Source: {{ doc.source }})
{% endfor %}

Question: {{ query }}

Provide a clear, accurate answer based on the context. If the context doesn't contain enough information, say so."""),
            
            "command": Template("""The user wants to execute a command: {{ command }}

Confirm the action in a friendly way. Example: "Opening Chrome now" or "Setting volume to 50%"."""),
            
            "math": Template("""Solve the following mathematical problem:

{{ query }}

Provide the answer and show your work if it's a complex calculation."""),
            
            "code": Template("""{{ query }}

{% if context %}
Context:
{{ context }}
{% endif %}

Provide clear, well-commented code. Explain your approach briefly."""),
            
            "conversational": Template("""{{ query }}

Respond in a {{ personality }} and natural way."""),
            
            "summary": Template("""Summarize the following information concisely:

{% for doc in documents %}
{{ doc.text }}
{% endfor %}

Provide a clear, concise summary.""")
        }
        
        return templates
    
    def get_system_prompt(self, personality: Optional[str] = None) -> str:
        """
        Get system prompt for personality.
        
        Args:
            personality: Personality style (uses default if None)
            
        Returns:
            System prompt string
        """
        personality = personality or self.personality
        return self.system_prompts.get(personality, self.system_prompts["friendly"])
    
    def build_prompt(
        self,
        intent: Intent,
        query: str,
        context_docs: Optional[List[Document]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """
        Build prompt for LLM based on intent.
        
        Args:
            intent: Classified intent
            query: User query
            context_docs: Retrieved context documents
            conversation_history: Previous conversation turns
            **kwargs: Additional template variables
            
        Returns:
            Formatted prompt string
        """
        # Select template based on intent
        template_name = self._get_template_name(intent.category)
        template = self.templates.get(template_name)
        
        if not template:
            logger.warning(f"No template for intent {intent.category}, using default")
            return query
        
        # Prepare template variables
        template_vars = {
            'query': query,
            'personality': self.personality,
            'context_docs': context_docs or [],
            **kwargs
        }
        
        # Add intent-specific variables
        if intent.category == IntentCategory.COMMAND:
            template_vars['command'] = query
        
        # Add conversation history if available
        if conversation_history:
            history_text = self._format_conversation_history(conversation_history)
            template_vars['conversation_history'] = history_text
        
        # Render template
        try:
            prompt = template.render(**template_vars)
            return prompt
        except Exception as e:
            logger.error(f"Failed to render template: {e}")
            return query
    
    def _get_template_name(self, category: IntentCategory) -> str:
        """Map intent category to template name."""
        mapping = {
            IntentCategory.QUESTION: "question",
            IntentCategory.COMMAND: "command",
            IntentCategory.MATH: "math",
            IntentCategory.CODE: "code",
            IntentCategory.CONVERSATIONAL: "conversational",
            IntentCategory.FETCH: "question"
        }
        return mapping.get(category, "conversational")
    
    def _format_conversation_history(
        self,
        history: List[Dict[str, str]],
        max_turns: int = 3
    ) -> str:
        """Format conversation history for context."""
        recent_history = history[-max_turns:] if len(history) > max_turns else history
        
        formatted = []
        for turn in recent_history:
            formatted.append(f"User: {turn.get('user', '')}")
            formatted.append(f"Assistant: {turn.get('assistant', '')}")
        
        return "\n".join(formatted)
    
    def add_few_shot_examples(
        self,
        prompt: str,
        intent_category: IntentCategory
    ) -> str:
        """
        Add few-shot examples to prompt.
        
        Args:
            prompt: Base prompt
            intent_category: Intent category
            
        Returns:
            Prompt with examples
        """
        examples = self._get_few_shot_examples(intent_category)
        
        if examples:
            examples_text = "\n\nExamples:\n" + "\n".join(examples)
            return prompt + examples_text
        
        return prompt
    
    def _get_few_shot_examples(self, category: IntentCategory) -> List[str]:
        """Get few-shot examples for intent category."""
        examples = {
            IntentCategory.MATH: [
                "Q: What is 15 + 27? A: 42",
                "Q: Calculate 8 * 9. A: 72"
            ],
            IntentCategory.CODE: [
                "Q: Write a function to reverse a string. A: def reverse(s): return s[::-1]"
            ]
        }
        
        return examples.get(category, [])
    
    def create_response_template(
        self,
        template_name: str,
        template_string: str
    ) -> None:
        """
        Add a custom response template.
        
        Args:
            template_name: Name for the template
            template_string: Jinja2 template string
        """
        self.templates[template_name] = Template(template_string)
        logger.info(f"Added custom template: {template_name}")
