"""
Enhanced Prompt Engineering with structured templates, few-shot learning,
and magical Codeex AI personality integration.
"""

from typing import Dict, Any, List, Optional
from jinja2 import Template
from datetime import datetime

from core.models import Intent, IntentCategory, Document
from core.codeex_personality import CodeexPersonality
from core.logger import get_logger

logger = get_logger(__name__)


class EnhancedPromptEngine:
    """
    Enhanced prompt engine with:
    - Structured templates for different query types
    - Few-shot learning examples
    - Magical Codeex personality integration
    - Context-aware prompt building
    - Chain-of-thought reasoning templates
    """
    
    def __init__(self, personality: str = "magical"):
        self.personality = personality
        self.codeex = CodeexPersonality()
        self.system_prompts = self._create_system_prompts()
        self.templates = self._create_templates()
        self.few_shot_examples = self._create_few_shot_examples()
        
        logger.info("Enhanced Prompt Engine initialized with magical personality")
    
    def _create_system_prompts(self) -> Dict[str, str]:
        """Create enhanced system prompts."""
        return {
            'magical': self.codeex.create_system_prompt(),
            'technical': """You are Jarvis, a highly technical AI assistant.
You provide precise, detailed technical explanations with code examples.
You break down complex concepts into clear, logical steps.
You cite sources and provide documentation links when relevant.""",
            'teaching': """You are Jarvis, an expert teacher and mentor.
You explain concepts using analogies and real-world examples.
You check for understanding and adjust your explanations accordingly.
You encourage curiosity and celebrate learning progress.
You break complex topics into digestible chunks.""",
            'debugging': """You are Jarvis, an expert debugging assistant.
You systematically analyze errors and provide step-by-step solutions.
You explain why errors occur and how to prevent them.
You suggest best practices and optimization opportunities."""
        }
    
    def _create_templates(self) -> Dict[str, Template]:
        """Create enhanced Jinja2 templates."""
        return {
            'question_with_context': Template("""{{ system_prompt }}

{% if conversation_history %}
Recent Conversation:
{{ conversation_history }}
{% endif %}

{% if context_docs %}
Relevant Information:
{% for doc in context_docs %}
- {{ doc.text[:300] }}... (Source: {{ doc.source }})
{% endfor %}
{% endif %}

{% if web_results %}
Web Search Results:
{% for result in web_results %}
{{ loop.index }}. {{ result.title }}
   {{ result.content[:200] }}...
{% endfor %}
{% endif %}

Student Question: {{ query }}

{% if few_shot_examples %}
Here are some example responses:
{% for example in few_shot_examples %}
Q: {{ example.question }}
A: {{ example.answer }}
{% endfor %}
{% endif %}

Provide a clear, helpful answer that:
1. Directly addresses the question
2. Uses examples when helpful
3. Maintains the magical, encouraging tone
4. Checks for understanding
5. Offers to elaborate if needed"""),
            
            'code_with_chain_of_thought': Template("""{{ system_prompt }}

Coding Request: {{ query }}

{% if context %}
Context: {{ context }}
{% endif %}

Think through this step-by-step:
1. Understand the requirement
2. Plan the approach
3. Write clean, commented code
4. Explain key decisions
5. Suggest improvements

{% if few_shot_examples %}
Example approach:
{{ few_shot_examples[0].answer }}
{% endif %}

Provide:
- Well-commented code
- Explanation of approach
- Usage example
- Potential edge cases"""),
            
            'debugging_systematic': Template("""{{ system_prompt }}

Error/Issue: {{ query }}

{% if error_details %}
Error Details:
{{ error_details }}
{% endif %}

Systematic Debugging Approach:
1. **Identify**: What's the exact error?
2. **Locate**: Where does it occur?
3. **Analyze**: Why does it happen?
4. **Fix**: How to resolve it?
5. **Prevent**: How to avoid it?

{% if similar_issues %}
Similar Issues Resolved:
{% for issue in similar_issues %}
- {{ issue.description }}: {{ issue.solution }}
{% endfor %}
{% endif %}

Provide a clear, step-by-step solution."""),
            
            'minecraft_modding': Template("""{{ system_prompt }}

Minecraft Modding Query: {{ query }}

{% if mod_context %}
Mod Details:
- Minecraft Version: {{ mod_context.mc_version }}
- Mod Loader: {{ mod_context.loader }}
- Development Environment: {{ mod_context.ide }}
{% endif %}

{% if code_snippet %}
Current Code:
```java
{{ code_snippet }}
```
{% endif %}

Provide modding guidance that includes:
1. Clear explanation
2. Code examples with comments
3. Common pitfalls to avoid
4. Testing recommendations
5. Resources for learning more

Remember: Make it magical and encouraging! ✨"""),
            
            'math_with_steps': Template("""{{ system_prompt }}

Math Problem: {{ query }}

Show your work step-by-step:
1. Identify what we're solving for
2. Write out the equation/formula
3. Show each calculation step
4. Verify the answer
5. Explain the concept

{% if similar_problems %}
Similar Problems:
{% for problem in similar_problems %}
{{ problem.question }} = {{ problem.answer }}
{% endfor %}
{% endif %}

Make math magical! Use clear notation and celebrate the solution! 🎯"""),
            
            'clarification_request': Template("""{{ system_prompt }}

I need clarification on: {{ query }}

{% if ambiguities %}
I noticed these possible interpretations:
{% for option in ambiguities %}
{{ loop.index }}. {{ option }}
{% endfor %}
{% endif %}

Could you help me understand by:
- Being more specific about what you need
- Providing an example
- Clarifying your goal

I'm here to help! 💫"""),
        }
    
    def _create_few_shot_examples(self) -> Dict[str, List[Dict]]:
        """Create few-shot learning examples."""
        return {
            'python_basics': [
                {
                    'question': 'How do I create a list in Python?',
                    'answer': '''✨ Creating lists in Python is easy!

```python
# Empty list
my_list = []

# List with items
fruits = ['apple', 'banana', 'orange']

# List with mixed types
mixed = [1, 'hello', 3.14, True]
```

Lists are super versatile! You can add, remove, and modify items. Want to learn more list operations? 🎯'''
                },
                {
                    'question': 'What is a function in Python?',
                    'answer': '''🪄 Functions are like magical spells you can reuse!

```python
def greet(name):
    """This function greets someone"""
    return f"Hello, {name}! ✨"

# Use it
message = greet("Student")
print(message)  # Hello, Student! ✨
```

Functions help you organize code and avoid repetition. They're essential! 🌟'''
                }
            ],
            'minecraft_modding': [
                {
                    'question': 'How do I create a custom block in Forge?',
                    'answer': '''🎮 Let's create a magical block!

```java
public class MagicalBlock extends Block {
    public MagicalBlock() {
        super(Properties.of(Material.STONE)
            .strength(3.0f)
            .sound(SoundType.STONE)
            .lightLevel((state) -> 15));
    }
    
    @Override
    public InteractionResult use(BlockState state, Level world, 
                                  BlockPos pos, Player player, 
                                  InteractionHand hand, BlockHitResult hit) {
        // Add your magical behavior here!
        return InteractionResult.SUCCESS;
    }
}
```

Don't forget to register it in your mod's setup! 🔮'''
                }
            ],
            'debugging': [
                {
                    'question': 'Why is my code throwing NullPointerException?',
                    'answer': '''🔍 NullPointerException means you're trying to use something that doesn't exist yet!

**Common Causes:**
1. Variable not initialized
2. Method returns null
3. Array element is null

**Fix:**
```java
// Before (crashes)
String name = null;
System.out.println(name.length());  // 💥

// After (safe)
String name = null;
if (name != null) {
    System.out.println(name.length());
} else {
    System.out.println("Name is not set");
}
```

Always check for null before using objects! 🛡️'''
                }
            ]
        }
    
    def build_prompt(
        self,
        query: str,
        intent: Intent,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict]] = None,
        user_preferences: Optional[Dict] = None
    ) -> str:
        """
        Build enhanced prompt with all context.
        
        Args:
            query: User query
            intent: Classified intent
            context: Additional context (docs, web results, etc.)
            conversation_history: Recent conversation
            user_preferences: User learning preferences
        
        Returns:
            Formatted prompt string
        """
        context = context or {}
        
        # Select appropriate template
        template_name = self._select_template(intent, context)
        template = self.templates.get(template_name)
        
        if not template:
            logger.warning(f"No template for {template_name}, using default")
            return self._build_default_prompt(query, context)
        
        # Select system prompt based on query type
        system_prompt = self._select_system_prompt(intent, user_preferences)
        
        # Get few-shot examples if applicable
        few_shot = self._get_relevant_few_shot(intent, query)
        
        # Format conversation history
        history_text = self._format_conversation_history(conversation_history) if conversation_history else None
        
        # Build template variables
        template_vars = {
            'system_prompt': system_prompt,
            'query': query,
            'conversation_history': history_text,
            'few_shot_examples': few_shot,
            **context
        }
        
        # Render template
        try:
            prompt = template.render(**template_vars)
            return prompt
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return self._build_default_prompt(query, context)
    
    def _select_template(self, intent: Intent, context: Dict) -> str:
        """Select appropriate template based on intent and context."""
        if context.get('needs_clarification'):
            return 'clarification_request'
        
        category = intent.category
        
        if category == IntentCategory.CODE:
            if context.get('has_error'):
                return 'debugging_systematic'
            elif 'minecraft' in context.get('query', '').lower():
                return 'minecraft_modding'
            else:
                return 'code_with_chain_of_thought'
        
        elif category == IntentCategory.MATH:
            return 'math_with_steps'
        
        elif category == IntentCategory.QUESTION:
            return 'question_with_context'
        
        else:
            return 'question_with_context'
    
    def _select_system_prompt(self, intent: Intent, user_preferences: Optional[Dict]) -> str:
        """Select system prompt based on intent and user preferences."""
        # Check user preferences
        if user_preferences:
            if user_preferences.get('prefers_technical'):
                return self.system_prompts['technical']
            elif user_preferences.get('prefers_teaching'):
                return self.system_prompts['teaching']
        
        # Default to magical for most cases
        if intent.category in [IntentCategory.CODE, IntentCategory.MATH]:
            if intent.confidence < 0.7:
                return self.system_prompts['teaching']
        
        return self.system_prompts['magical']
    
    def _get_relevant_few_shot(self, intent: Intent, query: str) -> Optional[List[Dict]]:
        """Get relevant few-shot examples."""
        query_lower = query.lower()
        
        if intent.category == IntentCategory.CODE:
            if 'python' in query_lower:
                return self.few_shot_examples.get('python_basics', [])[:2]
            elif 'minecraft' in query_lower or 'forge' in query_lower:
                return self.few_shot_examples.get('minecraft_modding', [])[:1]
            elif 'error' in query_lower or 'bug' in query_lower:
                return self.few_shot_examples.get('debugging', [])[:1]
        
        return None
    
    def _format_conversation_history(self, history: List[Dict], max_turns: int = 3) -> str:
        """Format conversation history."""
        recent = history[-max_turns:] if len(history) > max_turns else history
        
        formatted = []
        for turn in recent:
            formatted.append(f"Student: {turn.get('user', '')}")
            formatted.append(f"Jarvis: {turn.get('assistant', '')}")
        
        return "\n".join(formatted)
    
    def _build_default_prompt(self, query: str, context: Dict) -> str:
        """Build default prompt when template fails."""
        prompt_parts = [
            self.system_prompts['magical'],
            f"\nStudent Query: {query}"
        ]
        
        if context.get('context_docs'):
            prompt_parts.append("\nRelevant Information:")
            for doc in context['context_docs'][:3]:
                prompt_parts.append(f"- {doc.get('text', '')[:200]}")
        
        prompt_parts.append("\nProvide a helpful, magical response:")
        
        return "\n".join(prompt_parts)
    
    def create_chain_of_thought_prompt(self, query: str, steps: List[str]) -> str:
        """Create chain-of-thought reasoning prompt."""
        prompt = f"{self.system_prompts['magical']}\n\n"
        prompt += f"Query: {query}\n\n"
        prompt += "Let's think through this step-by-step:\n\n"
        
        for i, step in enumerate(steps, 1):
            prompt += f"{i}. {step}\n"
        
        prompt += "\nNow, provide the complete solution with explanations for each step."
        
        return prompt
    
    def add_custom_template(self, name: str, template_string: str):
        """Add custom template."""
        self.templates[name] = Template(template_string)
        logger.info(f"Added custom template: {name}")
    
    def add_few_shot_example(self, category: str, example: Dict):
        """Add few-shot example."""
        if category not in self.few_shot_examples:
            self.few_shot_examples[category] = []
        self.few_shot_examples[category].append(example)
        logger.info(f"Added few-shot example to {category}")
