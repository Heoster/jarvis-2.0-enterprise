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
