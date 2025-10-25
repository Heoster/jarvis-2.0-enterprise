"""
Grammar and Sentence Correction Engine
Uses language_tool_python for grammar checking and correction
"""

import re
from typing import Dict, List, Tuple, Optional
try:
    import language_tool_python
    LANGUAGE_TOOL_AVAILABLE = True
except ImportError:
    LANGUAGE_TOOL_AVAILABLE = False

from core.logger import get_logger

logger = get_logger(__name__)


class GrammarCorrector:
    """Grammar correction and text improvement engine"""
    
    def __init__(self, language: str = 'en-US'):
        """
        Initialize grammar corrector
        
        Args:
            language: Language code (default: en-US)
        """
        self.language = language
        self.tool = None
        
        if LANGUAGE_TOOL_AVAILABLE:
            try:
                self.tool = language_tool_python.LanguageTool(language)
                logger.info(f"Grammar corrector initialized for {language}")
            except Exception as e:
                logger.warning(f"Could not initialize LanguageTool: {e}")
                self.tool = None
        else:
            logger.warning("language_tool_python not available. Using basic corrections.")
    
    def correct_text(self, text: str) -> Dict[str, any]:
        """
        Correct grammar and spelling in text
        
        Args:
            text: Input text to correct
        
        Returns:
            Dictionary with corrected text and feedback
        """
        if not text or not text.strip():
            return {
                'original': text,
                'corrected': text,
                'corrections': [],
                'has_errors': False
            }
        
        # Use LanguageTool if available
        if self.tool:
            return self._correct_with_languagetool(text)
        else:
            return self._correct_basic(text)
    
    def _correct_with_languagetool(self, text: str) -> Dict[str, any]:
        """Correct using LanguageTool"""
        try:
            matches = self.tool.check(text)
            corrected = language_tool_python.utils.correct(text, matches)
            
            corrections = []
            for match in matches:
                correction_info = {
                    'message': match.message,
                    'context': match.context,
                    'replacements': match.replacements[:3],  # Top 3 suggestions
                    'rule': match.ruleId,
                    'category': match.category
                }
                corrections.append(correction_info)
            
            return {
                'original': text,
                'corrected': corrected,
                'corrections': corrections,
                'has_errors': len(matches) > 0,
                'error_count': len(matches)
            }
        
        except Exception as e:
            logger.error(f"LanguageTool correction failed: {e}")
            return self._correct_basic(text)
    
    def _correct_basic(self, text: str) -> Dict[str, any]:
        """Basic corrections without LanguageTool"""
        corrected = text
        corrections = []
        
        # Common text speak corrections
        text_speak = {
            r'\bhlo\b': 'hello',
            r'\bhw\b': 'how',
            r'\br\b': 'are',
            r'\bu\b': 'you',
            r'\bur\b': 'your',
            r'\bpls\b': 'please',
            r'\bthx\b': 'thanks',
            r'\bthnx\b': 'thanks',
            r'\bty\b': 'thank you',
            r'\bomg\b': 'oh my god',
            r'\bidk\b': "I don't know",
            r'\bbtw\b': 'by the way',
            r'\bbrb\b': 'be right back',
            r'\bgtg\b': 'got to go',
            r'\bttyl\b': 'talk to you later',
        }
        
        for pattern, replacement in text_speak.items():
            if re.search(pattern, corrected, re.IGNORECASE):
                corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
                corrections.append(f"Expanded '{pattern}' to '{replacement}'")
        
        # Capitalize first letter
        if corrected and corrected[0].islower():
            corrected = corrected[0].upper() + corrected[1:]
            corrections.append("Capitalized first letter")
        
        # Add period at end if missing
        if corrected and corrected[-1] not in '.!?':
            corrected += '.'
            corrections.append("Added ending punctuation")
        
        # Fix multiple spaces
        if '  ' in corrected:
            corrected = re.sub(r'\s+', ' ', corrected)
            corrections.append("Fixed spacing")
        
        # Fix multiple punctuation
        corrected = re.sub(r'([.!?]){2,}', r'\1', corrected)
        
        return {
            'original': text,
            'corrected': corrected,
            'corrections': corrections,
            'has_errors': len(corrections) > 0,
            'error_count': len(corrections)
        }
    
    def get_suggestions(self, text: str) -> List[str]:
        """
        Get improvement suggestions for text
        
        Args:
            text: Input text
        
        Returns:
            List of suggestions
        """
        suggestions = []
        
        # Check length
        if len(text.split()) < 3:
            suggestions.append("Try to be more specific in your question")
        
        # Check for questions
        if '?' not in text and any(text.lower().startswith(q) for q in ['what', 'how', 'why', 'when', 'where', 'who']):
            suggestions.append("Don't forget the question mark!")
        
        # Check for politeness
        polite_words = ['please', 'thanks', 'thank you', 'could you', 'would you']
        if not any(word in text.lower() for word in polite_words):
            suggestions.append("Adding 'please' makes your request more polite")
        
        return suggestions
    
    def analyze_writing_quality(self, text: str) -> Dict[str, any]:
        """
        Analyze overall writing quality
        
        Args:
            text: Input text
        
        Returns:
            Quality analysis
        """
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        analysis = {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_words_per_sentence': len(words) / max(len(sentences), 1),
            'has_capitalization': text[0].isupper() if text else False,
            'has_punctuation': text[-1] in '.!?' if text else False,
            'readability': 'good'  # Simplified
        }
        
        # Determine readability
        if analysis['avg_words_per_sentence'] > 25:
            analysis['readability'] = 'complex'
        elif analysis['avg_words_per_sentence'] < 5:
            analysis['readability'] = 'simple'
        
        return analysis
    
    def close(self):
        """Close the grammar tool"""
        if self.tool:
            try:
                self.tool.close()
            except:
                pass


# Singleton instance
_corrector_instance = None

def get_corrector(language: str = 'en-US') -> GrammarCorrector:
    """Get or create grammar corrector instance"""
    global _corrector_instance
    if _corrector_instance is None:
        _corrector_instance = GrammarCorrector(language)
    return _corrector_instance
