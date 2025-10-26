"""
Entertainment content formatter.
Formats jokes, quotes, images, and fun content.
"""

from typing import Dict, Any
from .base_formatter import ResponseFormatter


class EntertainmentFormatter(ResponseFormatter):
    """Format entertainment content (jokes, quotes, images, etc.)"""
    
    def format(self, data: Dict[str, Any]) -> str:
        """
        Format entertainment content.
        
        Args:
            data: Entertainment data dictionary
            
        Returns:
            Formatted entertainment content
        """
        content = data.get('content', {})
        content_type = data.get('type', 'joke')
        
        if not content or content.get('error'):
            return self.format_no_data("No entertainment content available")
        
        # Route to specific formatter based on type
        if content_type in ['joke', 'programming_joke']:
            return self._format_joke(content, content_type)
        elif content_type == 'dog':
            return self._format_dog_image(content)
        elif content_type == 'cat':
            return self._format_cat_fact(content)
        elif content_type == 'quote':
            return self._format_quote(content)
        else:
            return self._format_generic_entertainment(content, content_type)
    
    def _format_joke(self, joke_data: Dict[str, Any], joke_type: str) -> str:
        """Format joke content"""
        emoji = "💻" if joke_type == 'programming_joke' else "😄"
        title = "Programming Joke" if joke_type == 'programming_joke' else "Random Joke"
        
        response = self.add_header(title, emoji)
        
        # Joke type
        joke_category = joke_data.get('type', 'general').title()
        response += f"**Category:** {joke_category}\n\n"
        
        # Setup and punchline format
        if joke_data.get('setup') and joke_data.get('punchline'):
            response += f"🎭 **Setup:** {joke_data['setup']}\n\n"
            response += f"😂 **Punchline:** {joke_data['punchline']}\n\n"
        elif joke_data.get('joke'):
            # Single line joke
            response += f"😂 {joke_data['joke']}\n\n"
        else:
            response += "😅 Here's a joke for you!\n\n"
        
        # Add rating if available
        if joke_data.get('rating'):
            stars = "⭐" * int(joke_data['rating'])
            response += f"**Rating:** {stars} ({joke_data['rating']}/5)\n\n"
        
        response += self.add_footer("Hope that made you smile! 😊")
        
        return response
    
    def _format_dog_image(self, dog_data: Dict[str, Any]) -> str:
        """Format dog image content"""
        response = self.add_header("Random Dog Image", "🐕")
        
        # Image URL
        if dog_data.get('image_url'):
            response += f"**Image URL:** {dog_data['image_url']}\n\n"
        elif dog_data.get('url'):
            response += f"**Image URL:** {dog_data['url']}\n\n"
        
        # Breed information if available
        if dog_data.get('breed'):
            response += f"**Breed:** {dog_data['breed']}\n\n"
        
        # Fun fact about dogs
        dog_facts = [
            "Dogs have been human companions for over 15,000 years!",
            "A dog's sense of smell is 10,000 to 100,000 times stronger than humans.",
            "Dogs can learn over 150 words and can count up to 4 or 5.",
            "The average dog can run about 19 mph, but Greyhounds can reach 45 mph!",
            "Dogs dream just like humans do!"
        ]
        
        import random
        fun_fact = random.choice(dog_facts)
        response += f"🐶 **Fun Fact:** {fun_fact}\n\n"
        
        response += self.add_footer("Enjoy this adorable pup! 🐾")
        
        return response
    
    def _format_cat_fact(self, cat_data: Dict[str, Any]) -> str:
        """Format cat fact content"""
        response = self.add_header("Random Cat Fact", "🐱")
        
        # Cat fact
        fact = cat_data.get('fact', cat_data.get('text', 'Cats are amazing!'))
        response += f"**Did you know?**\n\n"
        response += f"🐈 {fact}\n\n"
        
        # Upvotes if available
        if cat_data.get('upvotes'):
            response += f"**Community Rating:** 👍 {cat_data['upvotes']} upvotes\n\n"
        
        # Length info if available
        if cat_data.get('length'):
            response += f"**Fact Length:** {cat_data['length']} characters\n\n"
        
        response += self.add_footer("Cats are truly fascinating creatures! 🐾")
        
        return response
    
    def _format_quote(self, quote_data: Dict[str, Any]) -> str:
        """Format inspirational quote"""
        response = self.add_header("Inspirational Quote", "💭")
        
        # Quote text
        quote_text = quote_data.get('quote', quote_data.get('text', ''))
        if quote_text:
            response += f'**Quote:**\n\n"{quote_text}"\n\n'
        
        # Author
        author = quote_data.get('author', 'Unknown')
        response += f"**— {author}**\n\n"
        
        # Category if available
        if quote_data.get('category'):
            response += f"**Category:** {quote_data['category'].title()}\n\n"
        
        # Tags if available
        if quote_data.get('tags'):
            tags = quote_data['tags']
            if isinstance(tags, list):
                response += f"**Tags:** {', '.join(tags)}\n\n"
            else:
                response += f"**Tags:** {tags}\n\n"
        
        response += self.add_footer("Stay inspired! ✨")
        
        return response
    
    def _format_generic_entertainment(self, content: Dict[str, Any], content_type: str) -> str:
        """Format generic entertainment content"""
        response = self.add_header(f"{content_type.title()} Content", "🎉")
        
        # Try to format whatever content we have
        if content.get('title'):
            response += f"**Title:** {content['title']}\n\n"
        
        if content.get('description'):
            response += f"**Description:** {content['description']}\n\n"
        
        if content.get('content'):
            response += f"**Content:** {content['content']}\n\n"
        
        if content.get('url'):
            response += f"**URL:** {content['url']}\n\n"
        
        # Add any other fields
        for key, value in content.items():
            if key not in ['title', 'description', 'content', 'url', 'error'] and value:
                formatted_key = key.replace('_', ' ').title()
                response += f"**{formatted_key}:** {value}\n\n"
        
        response += self.add_footer("Enjoy the entertainment! 🎊")
        
        return response
    
    def format_entertainment_error(self, error: str, content_type: str = "entertainment") -> str:
        """
        Format entertainment content error.
        
        Args:
            error: Error message
            content_type: Type of entertainment content
            
        Returns:
            Formatted error message
        """
        response = self.add_header(f"{content_type.title()} Error", self.emojis['error'])
        response += f"❌ Failed to retrieve {content_type} content\n\n"
        response += f"Error: {error}\n\n"
        
        # Add suggestions based on content type
        suggestions = []
        if content_type == 'joke':
            suggestions = [
                "Try asking for a different type of joke",
                "Ask for programming jokes if you're a developer",
                "Request a random joke instead"
            ]
        elif content_type == 'quote':
            suggestions = [
                "Ask for motivational quotes",
                "Try requesting quotes by a specific author",
                "Ask for quotes about a particular topic"
            ]
        elif content_type in ['dog', 'cat']:
            suggestions = [
                "Try asking for cute animal pictures",
                "Request animal facts instead",
                "Ask for a different type of entertainment"
            ]
        else:
            suggestions = [
                "Try a different entertainment request",
                "Ask for jokes, quotes, or animal pictures",
                "Check your internet connection"
            ]
        
        response += "**Suggestions:**\n"
        response += self.format_list_items(suggestions)
        response += "\n"
        
        response += self.add_footer("Please try again later")
        
        return response