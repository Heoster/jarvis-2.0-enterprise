"""
Codeex Personality Layer - Magical AI Assistant for Students
Adds warmth, creativity, and branded responses to Jarvis
"""

import random
from typing import Dict, List, Optional
from datetime import datetime


class CodeexPersonality:
    """Magical personality wrapper for student-friendly interactions"""
    
    # Magical greetings based on time of day
    GREETINGS = {
        'morning': [
            "🌅 Good morning, brilliant student! Ready to learn some magic today?",
            "☀️ Rise and shine! Codeex is here to make your morning magical!",
            "🌄 Morning, superstar! Let's conjure up some knowledge together!"
        ],
        'afternoon': [
            "🌞 Good afternoon! Time for some magical learning!",
            "✨ Hey there! Codeex is ready to help you shine this afternoon!",
            "🎯 Afternoon, champion! Let's tackle those challenges together!"
        ],
        'evening': [
            "🌙 Good evening! Let's make tonight's study session magical!",
            "⭐ Evening, star student! Codeex is here to light up your learning!",
            "🌃 Hey night owl! Ready for some enchanted problem-solving?"
        ],
        'night': [
            "🌟 Burning the midnight oil? Codeex is here to help!",
            "🦉 Late night study session? Let's make it magical!",
            "✨ Still going strong? You're amazing! How can Codeex help?"
        ]
    }
    
    # Magical emojis for different contexts
    EMOJIS = {
        'success': ['✨', '🎉', '🌟', '⭐', '🎊', '🏆', '💫'],
        'thinking': ['🤔', '💭', '🧠', '🔮', '🪄'],
        'learning': ['📚', '📖', '✏️', '🎓', '🧙‍♂️', '🧪'],
        'coding': ['💻', '⚡', '🚀', '🔧', '🛠️', '⚙️'],
        'error': ['🔍', '🐛', '🔧', '⚠️'],
        'magic': ['✨', '🪄', '🌟', '💫', '⚡', '🔮'],
        'celebration': ['🎉', '🎊', '🥳', '🎈', '🎆', '🌈']
    }
    
    # Fallback responses for unclear queries
    FALLBACK_RESPONSES = [
        "🪄 Hmm, that spell didn't quite work. Could you try rephrasing?",
        "🔮 My crystal ball is a bit foggy on that one. Can you be more specific?",
        "✨ Oops! I didn't catch that magic word. Mind trying again?",
        "🧙‍♂️ Even wizards need clarity! Could you explain that differently?",
        "💫 That's a tricky one! Can you give me more details?",
        "🌟 I want to help, but I need a bit more info. What exactly do you need?"
    ]
    
    # Encouragement messages
    ENCOURAGEMENTS = [
        "You're doing great! 🌟",
        "Keep up the amazing work! ✨",
        "You're a natural! 🎯",
        "Brilliant thinking! 💡",
        "You've got this! 💪",
        "That's the spirit! 🎉"
    ]
    
    # Error handling messages
    ERROR_MESSAGES = [
        "🔧 Oops! Something went wrong, but don't worry - we'll fix it!",
        "⚠️ Hit a small bump, but Codeex is on it!",
        "🐛 Found a tiny bug, but we're debugging together!",
        "🔍 Hmm, let me try a different approach..."
    ]
    
    def __init__(self):
        self.session_start = datetime.now()
        self.interaction_count = 0
    
    def get_greeting(self) -> str:
        """Get time-appropriate magical greeting"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            time_period = 'morning'
        elif 12 <= hour < 17:
            time_period = 'afternoon'
        elif 17 <= hour < 21:
            time_period = 'evening'
        else:
            time_period = 'night'
        
        return random.choice(self.GREETINGS[time_period])
    
    def get_emoji(self, context: str) -> str:
        """Get random emoji for context"""
        emojis = self.EMOJIS.get(context, self.EMOJIS['magic'])
        return random.choice(emojis)
    
    def get_fallback(self) -> str:
        """Get fallback response for unclear queries"""
        return random.choice(self.FALLBACK_RESPONSES)
    
    def get_encouragement(self) -> str:
        """Get random encouragement"""
        return random.choice(self.ENCOURAGEMENTS)
    
    def get_error_message(self) -> str:
        """Get friendly error message"""
        return random.choice(self.ERROR_MESSAGES)
    
    def wrap_response(self, response: str, context: str = 'general') -> str:
        """
        Wrap response with Codeex personality
        
        Args:
            response: Original response text
            context: Context type (success, error, learning, etc.)
        
        Returns:
            Personality-enhanced response
        """
        self.interaction_count += 1
        
        # Add opening emoji
        emoji = self.get_emoji(context)
        
        # Add encouragement occasionally
        if self.interaction_count % 3 == 0 and context == 'success':
            encouragement = f"\n\n{self.get_encouragement()}"
        else:
            encouragement = ""
        
        # Wrap the response
        wrapped = f"{emoji} {response}{encouragement}"
        
        return wrapped
    
    def format_correction(self, original: str, corrected: str, 
                         feedback: List[str]) -> str:
        """
        Format grammar correction with magical flair
        
        Args:
            original: Original text
            corrected: Corrected text
            feedback: List of corrections made
        
        Returns:
            Formatted correction message
        """
        if original == corrected:
            return f"✨ Perfect! Your sentence is already magical! ✨"
        
        message = f"🪄 **Codeex's Grammar Magic** ✨\n\n"
        message += f"📝 **You said:** {original}\n\n"
        message += f"✅ **Codeex suggests:** {corrected}\n\n"
        
        if feedback:
            message += "💡 **What changed:**\n"
            for i, fix in enumerate(feedback, 1):
                message += f"   {i}. {fix}\n"
        
        message += f"\n{self.get_encouragement()}"
        
        return message
    
    def format_code_help(self, question: str, answer: str, 
                        code_snippet: Optional[str] = None) -> str:
        """
        Format coding help with student-friendly style
        
        Args:
            question: Student's question
            answer: Answer/explanation
            code_snippet: Optional code example
        
        Returns:
            Formatted help message
        """
        message = f"💻 **Codeex Code Helper** ⚡\n\n"
        message += f"❓ **Your Question:** {question}\n\n"
        message += f"💡 **Answer:** {answer}\n\n"
        
        if code_snippet:
            message += f"```\n{code_snippet}\n```\n\n"
        
        message += "🎯 **Pro Tip:** Practice makes perfect! Try it yourself!\n"
        
        return message
    
    def format_quiz_question(self, question: str, options: List[str], 
                           difficulty: str = 'medium') -> str:
        """
        Format quiz question with magical theme
        
        Args:
            question: Quiz question
            options: List of answer options
            difficulty: Question difficulty
        
        Returns:
            Formatted quiz question
        """
        difficulty_emojis = {
            'easy': '🌱',
            'medium': '🌟',
            'hard': '🔥',
            'expert': '🏆'
        }
        
        emoji = difficulty_emojis.get(difficulty, '🌟')
        
        message = f"{emoji} **Codeex Quiz Time!** {emoji}\n\n"
        message += f"❓ {question}\n\n"
        
        for i, option in enumerate(options, 1):
            message += f"   {i}. {option}\n"
        
        message += f"\n💭 Take your time and think it through!"
        
        return message
    
    def format_modding_help(self, mod_name: str, issue: str, 
                          solution: str) -> str:
        """
        Format Minecraft modding help
        
        Args:
            mod_name: Name of the mod
            issue: Issue description
            solution: Solution steps
        
        Returns:
            Formatted modding help
        """
        message = f"🎮 **Codeex Modding Wizard** 🛠️\n\n"
        message += f"📦 **Mod:** {mod_name}\n"
        message += f"⚠️ **Issue:** {issue}\n\n"
        message += f"✅ **Solution:**\n{solution}\n\n"
        message += "🚀 Happy modding! Let me know if you need more help!"
        
        return message
    
    def create_system_prompt(self) -> str:
        """
        Create system prompt for AI with Codeex personality
        
        Returns:
            System prompt string
        """
        return """You are Codeex AI, a magical assistant designed for students.

Your personality:
- Warm, encouraging, and supportive
- Use emojis and sparkles to make learning fun
- Explain complex topics in simple, relatable ways
- Celebrate student successes enthusiastically
- Patient and never judgmental
- Creative and engaging in your responses

Your expertise:
- Homework help across all subjects
- Coding and programming guidance
- Grammar and writing assistance
- Minecraft modding support
- Study tips and learning strategies
- Problem-solving and critical thinking

Response style:
- Start with a friendly emoji
- Use clear, concise language
- Break down complex topics into steps
- Provide examples when helpful
- End with encouragement or a helpful tip
- Make learning feel like an adventure

Remember: Every student is capable of greatness. Your job is to help them discover it! ✨"""
    
    def get_themed_response(self, category: str, content: str) -> str:
        """
        Get themed response based on category
        
        Args:
            category: Response category
            content: Response content
        
        Returns:
            Themed response
        """
        themes = {
            'math': ('🔢', '📐', 'Math Magic'),
            'science': ('🧪', '🔬', 'Science Sorcery'),
            'coding': ('💻', '⚡', 'Code Wizardry'),
            'writing': ('✍️', '📝', 'Writing Wonders'),
            'history': ('📜', '🏛️', 'History Quest'),
            'language': ('🗣️', '🌍', 'Language Adventure'),
            'general': ('✨', '🌟', 'Codeex Wisdom')
        }
        
        emoji1, emoji2, title = themes.get(category, themes['general'])
        
        return f"{emoji1} **{title}** {emoji2}\n\n{content}"


class EnhancedCodeexPersonality(CodeexPersonality):
    """Enhanced personality with dynamic tone adjustment and context awareness"""
    
    def __init__(self):
        super().__init__()
        from core.constants import PersonalitySettings
        self.tone_modifiers = PersonalitySettings.TONE_MODIFIERS
        self.tone_threshold = PersonalitySettings.TONE_ADJUSTMENT_THRESHOLD
        self.context_memory = []
    
    def adjust_tone(self, response: str, sentiment: str, context: Dict) -> str:
        """
        Dynamically adjust tone based on context and sentiment.
        
        Args:
            response: Original response
            sentiment: Detected sentiment
            context: Conversation context
            
        Returns:
            Tone-adjusted response
        """
        # Determine appropriate tone based on context
        tone = self._select_tone(sentiment, context)
        
        # Apply tone modifier
        if tone in self.tone_modifiers:
            import random
            modifier = random.choice(self.tone_modifiers[tone])
            return f"{modifier} {response}"
        
        return response
    
    def _select_tone(self, sentiment: str, context: Dict) -> str:
        """Select appropriate tone based on sentiment and context"""
        # If user is struggling, be supportive
        if context.get('difficulty_level') == 'high' or sentiment == 'frustrated':
            return 'supportive'
        
        # If user succeeded, celebrate
        elif context.get('success') or sentiment == 'happy':
            return 'celebratory'
        
        # If user is learning, encourage
        elif context.get('learning_mode') or sentiment == 'curious':
            return 'encouraging'
        
        # Default to excited for positive interactions
        elif sentiment in ['positive', 'neutral']:
            return 'excited'
        
        # Professional tone for serious contexts
        elif context.get('formal_context'):
            return 'professional'
        
        return 'encouraging'  # Default fallback
    
    def create_themed_response(self, content: str, theme: str) -> str:
        """
        Create themed responses for different contexts.
        
        Args:
            content: Response content
            theme: Theme identifier
            
        Returns:
            Themed response
        """
        themes = {
            'debugging': {
                'prefix': '🔍 Debug Mode Activated!',
                'emoji': '🐛',
                'style': 'Let\'s hunt down that bug together!',
                'color': 'red'
            },
            'learning': {
                'prefix': '📚 Learning Time!',
                'emoji': '✨',
                'style': 'Every expert was once a beginner!',
                'color': 'blue'
            },
            'achievement': {
                'prefix': '🏆 Achievement Unlocked!',
                'emoji': '🎊',
                'style': 'You\'re crushing it!',
                'color': 'gold'
            },
            'coding': {
                'prefix': '💻 Code Wizard Mode!',
                'emoji': '⚡',
                'style': 'Time to write some magical code!',
                'color': 'green'
            },
            'math': {
                'prefix': '🔢 Math Magic!',
                'emoji': '📐',
                'style': 'Numbers are just another language!',
                'color': 'purple'
            },
            'search': {
                'prefix': '🔍 Information Quest!',
                'emoji': '🌐',
                'style': 'Let\'s discover something amazing!',
                'color': 'cyan'
            }
        }
        
        theme_config = themes.get(theme, themes['learning'])
        
        response = f"{theme_config['prefix']} {theme_config['emoji']}\n\n"
        response += f"{content}\n\n"
        response += f"✨ {theme_config['style']}"
        
        return response
    
    def adapt_to_user_style(self, user_history: List[Dict], response: str) -> str:
        """
        Adapt response style based on user interaction history.
        
        Args:
            user_history: List of previous interactions
            response: Original response
            
        Returns:
            Style-adapted response
        """
        if not user_history:
            return response
        
        # Analyze user preferences from history
        preferences = self._analyze_user_preferences(user_history)
        
        # Adjust response based on preferences
        if preferences.get('prefers_concise'):
            response = self._make_concise(response)
        elif preferences.get('prefers_detailed'):
            response = self._add_details(response)
        
        if preferences.get('likes_examples'):
            response = self._add_example_hint(response)
        
        if preferences.get('formal_tone'):
            response = self._formalize_tone(response)
        
        return response
    
    def _analyze_user_preferences(self, history: List[Dict]) -> Dict[str, bool]:
        """Analyze user preferences from interaction history"""
        preferences = {
            'prefers_concise': False,
            'prefers_detailed': False,
            'likes_examples': False,
            'formal_tone': False
        }
        
        # Simple analysis based on user queries
        for interaction in history[-10:]:  # Last 10 interactions
            query = interaction.get('query', '').lower()
            
            if any(word in query for word in ['brief', 'short', 'quick', 'tldr']):
                preferences['prefers_concise'] = True
            
            if any(word in query for word in ['detail', 'explain', 'elaborate', 'more']):
                preferences['prefers_detailed'] = True
            
            if any(word in query for word in ['example', 'show me', 'demonstrate']):
                preferences['likes_examples'] = True
            
            if any(word in query for word in ['please', 'could you', 'would you']):
                preferences['formal_tone'] = True
        
        return preferences
    
    def _make_concise(self, response: str) -> str:
        """Make response more concise"""
        # Simple approach - could be enhanced with NLP
        sentences = response.split('. ')
        if len(sentences) > 3:
            # Keep first 2 and last sentence
            concise = '. '.join(sentences[:2] + [sentences[-1]])
            return concise
        return response
    
    def _add_details(self, response: str) -> str:
        """Add more details to response"""
        # Add helpful context
        return f"{response}\n\n💡 **Additional Context:** This information can help you understand the topic better. Feel free to ask for more specific details!"
    
    def _add_example_hint(self, response: str) -> str:
        """Add hint about examples"""
        return f"{response}\n\n🎯 **Tip:** Ask me for examples if you'd like to see this in action!"
    
    def _formalize_tone(self, response: str) -> str:
        """Make tone more formal"""
        # Replace casual expressions
        formal_replacements = {
            "Let's": "Let us",
            "You're": "You are",
            "It's": "It is",
            "We're": "We are",
            "That's": "That is"
        }
        
        for casual, formal in formal_replacements.items():
            response = response.replace(casual, formal)
        
        return response
    
    def generate_contextual_greeting(self, context: Dict) -> str:
        """
        Generate contextual greeting based on situation.
        
        Args:
            context: Current context information
            
        Returns:
            Contextual greeting
        """
        time_greeting = self.get_greeting()
        
        # Add context-specific elements
        if context.get('returning_user'):
            return f"{time_greeting} Welcome back! Ready to continue our learning journey?"
        
        if context.get('first_time'):
            return f"{time_greeting} Welcome to Codeex! I'm excited to help you learn and grow! ✨"
        
        if context.get('error_context'):
            return f"{time_greeting} I see you might be facing a challenge. Don't worry, we'll solve it together! 💪"
        
        return time_greeting
    
    def create_celebration_message(self, achievement: str, difficulty: str = 'medium') -> str:
        """
        Create celebration message for achievements.
        
        Args:
            achievement: What was achieved
            difficulty: Difficulty level of achievement
            
        Returns:
            Celebration message
        """
        celebration_levels = {
            'easy': {
                'emoji': '🌟',
                'message': 'Great job!',
                'encouragement': 'You\'re building momentum!'
            },
            'medium': {
                'emoji': '🎉',
                'message': 'Excellent work!',
                'encouragement': 'You\'re really getting the hang of this!'
            },
            'hard': {
                'emoji': '🏆',
                'message': 'Outstanding achievement!',
                'encouragement': 'You\'ve mastered something challenging!'
            },
            'expert': {
                'emoji': '👑',
                'message': 'Legendary performance!',
                'encouragement': 'You\'re becoming a true expert!'
            }
        }
        
        level = celebration_levels.get(difficulty, celebration_levels['medium'])
        
        return f"{level['emoji']} {level['message']} {level['emoji']}\n\n" \
               f"Achievement: {achievement}\n\n" \
               f"✨ {level['encouragement']} Keep up the amazing work!"


# Enhanced personality instance
def get_enhanced_personality() -> EnhancedCodeexPersonality:
    """Get enhanced personality instance"""
    return EnhancedCodeexPersonality()