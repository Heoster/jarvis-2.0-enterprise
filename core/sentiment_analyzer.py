"""Sentiment Analysis for mood detection and tone adjustment."""

from typing import Dict, Any, Optional
import re

from core.logger import get_logger

logger = get_logger(__name__)


class SentimentAnalyzer:
    """
    Analyzes student sentiment to adjust Jarvis's tone and provide
    appropriate encouragement or support.
    """
    
    def __init__(self):
        self.sentiment_patterns = self._initialize_patterns()
        self.transformer_model = self._initialize_transformer()
    
    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize sentiment detection patterns."""
        return {
            'frustrated': {
                'keywords': [
                    'confused', 'stuck', 'help', "don't understand", 'frustrated',
                    'difficult', 'hard', 'impossible', "can't", 'struggling',
                    'lost', 'unclear', 'complicated', 'overwhelmed'
                ],
                'patterns': [
                    r"i don'?t (get|understand)",
                    r"this (is|seems) (too )?(hard|difficult|confusing)",
                    r"(help|stuck|lost)",
                    r"why (isn'?t|doesn'?t) (this|it) work"
                ],
                'tone_adjustment': 'extra_supportive'
            },
            'confident': {
                'keywords': [
                    'got it', 'understand', 'makes sense', 'clear', 'easy',
                    'simple', 'obvious', 'straightforward', 'perfect', 'excellent'
                ],
                'patterns': [
                    r"(got|get) it",
                    r"makes sense",
                    r"(i )?understand",
                    r"that'?s (clear|easy|simple)"
                ],
                'tone_adjustment': 'challenging'
            },
            'excited': {
                'keywords': [
                    'awesome', 'cool', 'amazing', 'love', 'excited', 'great',
                    'fantastic', 'wonderful', 'brilliant', 'perfect', 'wow'
                ],
                'patterns': [
                    r"(that'?s|this is) (awesome|cool|amazing|great)",
                    r"i love (this|it)",
                    r"(wow|amazing|fantastic)"
                ],
                'tone_adjustment': 'enthusiastic'
            },
            'curious': {
                'keywords': [
                    'what if', 'how about', 'could', 'would', 'interesting',
                    'wonder', 'curious', 'explore', 'learn more'
                ],
                'patterns': [
                    r"what if",
                    r"how about",
                    r"(could|would) (i|we|you)",
                    r"(tell|show) me more"
                ],
                'tone_adjustment': 'exploratory'
            },
            'bored': {
                'keywords': [
                    'boring', 'tedious', 'repetitive', 'again', 'already know',
                    'too easy', 'simple', 'basic'
                ],
                'patterns': [
                    r"(too|so) (easy|simple|basic)",
                    r"already know",
                    r"(boring|tedious)"
                ],
                'tone_adjustment': 'advanced'
            }
        }
    
    def _initialize_transformer(self):
        """Initialize transformer-based sentiment model."""
        try:
            from transformers import pipeline
            model = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            logger.info("Transformer sentiment model loaded")
            return model
        except ImportError:
            logger.warning("transformers not available, using pattern-based sentiment")
            return None
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            return None
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of student input.
        
        Args:
            text: Student's message
            
        Returns:
            Sentiment analysis with mood, confidence, and tone adjustment
        """
        text_lower = text.lower()
        
        # Pattern-based detection
        pattern_sentiment = self._analyze_patterns(text_lower)
        
        # Transformer-based detection (if available)
        transformer_sentiment = self._analyze_transformer(text)
        
        # Combine results
        if transformer_sentiment and pattern_sentiment:
            # Use pattern if high confidence, otherwise transformer
            if pattern_sentiment['confidence'] > 0.7:
                final_sentiment = pattern_sentiment
            else:
                final_sentiment = transformer_sentiment
        else:
            final_sentiment = pattern_sentiment or transformer_sentiment or {
                'mood': 'neutral',
                'confidence': 0.5,
                'tone_adjustment': 'balanced'
            }
        
        # Add intensity
        final_sentiment['intensity'] = self._calculate_intensity(text_lower)
        
        # Add specific indicators
        final_sentiment['indicators'] = self._extract_indicators(text_lower)
        
        return final_sentiment
    
    def _analyze_patterns(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze using keyword and regex patterns."""
        scores = {}
        
        for mood, config in self.sentiment_patterns.items():
            score = 0
            
            # Check keywords
            for keyword in config['keywords']:
                if keyword in text:
                    score += 1
            
            # Check patterns
            for pattern in config['patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 2  # Patterns weighted higher
            
            if score > 0:
                scores[mood] = score
        
        if not scores:
            return None
        
        # Get highest scoring mood
        best_mood = max(scores, key=scores.get)
        confidence = min(scores[best_mood] / 5.0, 1.0)  # Normalize to 0-1
        
        return {
            'mood': best_mood,
            'confidence': confidence,
            'tone_adjustment': self.sentiment_patterns[best_mood]['tone_adjustment'],
            'method': 'pattern'
        }
    
    def _analyze_transformer(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze using transformer model."""
        if not self.transformer_model:
            return None
        
        try:
            result = self.transformer_model(text)[0]
            label = result['label'].lower()
            score = result['score']
            
            # Map transformer labels to our moods
            mood_mapping = {
                'positive': 'confident',
                'negative': 'frustrated',
                'neutral': 'neutral'
            }
            
            mood = mood_mapping.get(label, 'neutral')
            
            return {
                'mood': mood,
                'confidence': score,
                'tone_adjustment': self.sentiment_patterns.get(mood, {}).get('tone_adjustment', 'balanced'),
                'method': 'transformer'
            }
        except Exception as e:
            logger.error(f"Transformer sentiment analysis failed: {e}")
            return None
    
    def _calculate_intensity(self, text: str) -> float:
        """Calculate emotional intensity."""
        intensity_markers = {
            'very': 1.5,
            'really': 1.5,
            'extremely': 2.0,
            'so': 1.3,
            'totally': 1.5,
            '!': 0.2,  # Per exclamation mark
            '?': 0.1,  # Per question mark
            'CAPS': 0.3  # Per capitalized word
        }
        
        intensity = 1.0
        
        for marker, multiplier in intensity_markers.items():
            if marker == '!':
                intensity += text.count('!') * multiplier
            elif marker == '?':
                intensity += text.count('?') * multiplier
            elif marker == 'CAPS':
                caps_words = sum(1 for word in text.split() if word.isupper() and len(word) > 1)
                intensity += caps_words * multiplier
            elif marker in text:
                intensity *= multiplier
        
        return min(intensity, 3.0)  # Cap at 3x
    
    def _extract_indicators(self, text: str) -> List[str]:
        """Extract specific emotional indicators."""
        indicators = []
        
        if '!' in text:
            indicators.append('emphatic')
        if '?' * 2 in text:
            indicators.append('very_confused')
        if any(word.isupper() for word in text.split() if len(word) > 1):
            indicators.append('strong_emotion')
        if '...' in text:
            indicators.append('uncertain')
        if ':)' in text or '😊' in text or '😄' in text:
            indicators.append('positive_emoji')
        if ':(' in text or '😞' in text or '😢' in text:
            indicators.append('negative_emoji')
        
        return indicators
    
    def get_tone_recommendation(self, sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get recommended tone adjustments based on sentiment.
        
        Args:
            sentiment: Sentiment analysis result
            
        Returns:
            Tone recommendations
        """
        mood = sentiment['mood']
        intensity = sentiment.get('intensity', 1.0)
        
        recommendations = {
            'frustrated': {
                'approach': 'extra_supportive',
                'suggestions': [
                    'Break down concepts into smaller steps',
                    'Use more analogies and examples',
                    'Provide extra encouragement',
                    'Offer alternative explanations',
                    'Check understanding frequently'
                ],
                'emoji_style': 'supportive',  # 💪🔧🌟
                'language': 'simple and clear'
            },
            'confident': {
                'approach': 'challenging',
                'suggestions': [
                    'Introduce advanced concepts',
                    'Provide optimization challenges',
                    'Discuss edge cases',
                    'Encourage exploration',
                    'Offer related topics'
                ],
                'emoji_style': 'achievement',  # 🎯🚀⭐
                'language': 'technical and precise'
            },
            'excited': {
                'approach': 'enthusiastic',
                'suggestions': [
                    'Match their energy',
                    'Celebrate their progress',
                    'Introduce fun challenges',
                    'Share interesting facts',
                    'Encourage creativity'
                ],
                'emoji_style': 'celebratory',  # 🎉✨🌟
                'language': 'energetic and engaging'
            },
            'curious': {
                'approach': 'exploratory',
                'suggestions': [
                    'Provide deeper explanations',
                    'Offer related resources',
                    'Encourage experimentation',
                    'Share interesting connections',
                    'Ask thought-provoking questions'
                ],
                'emoji_style': 'discovery',  # 🔍💡🧩
                'language': 'thought-provoking'
            },
            'bored': {
                'approach': 'advanced',
                'suggestions': [
                    'Skip basics',
                    'Introduce complex topics',
                    'Provide real-world applications',
                    'Discuss advanced techniques',
                    'Challenge with projects'
                ],
                'emoji_style': 'professional',  # 🎯⚡🔥
                'language': 'advanced and concise'
            }
        }
        
        base_rec = recommendations.get(mood, recommendations['confident'])
        
        # Adjust for intensity
        if intensity > 2.0:
            base_rec['intensity_note'] = 'Strong emotion detected - respond with extra care'
        
        return base_rec
