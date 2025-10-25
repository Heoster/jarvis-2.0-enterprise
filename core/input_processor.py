"""Advanced input processing with fuzzy matching and normalization."""

import re
from typing import Dict, Any, List, Tuple, Optional
from difflib import SequenceMatcher
import asyncio

from core.logger import get_logger

logger = get_logger(__name__)


class InputProcessor:
    """Process and normalize user input for better understanding."""
    
    def __init__(self):
        """Initialize input processor."""
        self.common_corrections = {
            # Greetings
            'hlo': 'hello',
            'hii': 'hi',
            'heelo': 'hello',
            'helo': 'hello',
            'hlw': 'hello',
            'hy': 'hi',
            'hye': 'hi',
            'hiii': 'hi',
            
            # Common words
            'u': 'you',
            'ur': 'your',
            'r': 'are',
            'y': 'why',
            'wat': 'what',
            'wht': 'what',
            'hw': 'how',
            'plz': 'please',
            'pls': 'please',
            'thx': 'thanks',
            'thnx': 'thanks',
            'ty': 'thank you',
            
            # Questions
            'wats': 'what is',
            'whats': 'what is',
            'whos': 'who is',
            'hows': 'how is',
            'wheres': 'where is',
            
            # Commands
            'calc': 'calculate',
            'tel': 'tell',
            'shw': 'show',
            'srch': 'search',
            'fnd': 'find',
        }
        
        self.intent_patterns = {
            'greeting': [
                'hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon',
                'good evening', 'howdy', 'sup', 'yo', 'hola'
            ],
            'farewell': [
                'bye', 'goodbye', 'see you', 'farewell', 'later', 'cya', 'peace'
            ],
            'thanks': [
                'thank', 'thanks', 'thx', 'ty', 'appreciate', 'grateful'
            ],
            'question': [
                'what', 'who', 'where', 'when', 'why', 'how', 'which', 'whose',
                'tell me', 'explain', 'describe', 'define'
            ],
            'command': [
                'open', 'close', 'start', 'stop', 'run', 'launch', 'execute',
                'show', 'display', 'get', 'fetch'
            ],
            'math': [
                'calculate', 'compute', 'solve', 'what is', '+', '-', '*', '/',
                'plus', 'minus', 'times', 'divided', 'equals'
            ],
            'search': [
                'search', 'find', 'look up', 'look for', 'google', 'browse'
            ],
            'weather': [
                'weather', 'temperature', 'forecast', 'climate', 'hot', 'cold', 'rain'
            ],
            'news': [
                'news', 'headlines', 'latest', 'current events', 'breaking'
            ]
        }
        
        logger.info("Input processor initialized")
    
    def normalize(self, text: str) -> str:
        """
        Normalize user input.
        
        Args:
            text: Raw user input
            
        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common typos
        words = text.split()
        corrected_words = []
        
        for word in words:
            # Check if word needs correction
            if word in self.common_corrections:
                corrected_words.append(self.common_corrections[word])
            else:
                # Try fuzzy matching for close matches
                corrected = self._fuzzy_correct(word)
                corrected_words.append(corrected)
        
        normalized = ' '.join(corrected_words)
        
        if normalized != text:
            logger.info(f"Normalized '{text}' to '{normalized}'")
        
        return normalized
    
    def _fuzzy_correct(self, word: str) -> str:
        """
        Fuzzy match word against common corrections.
        
        Args:
            word: Word to correct
            
        Returns:
            Corrected word or original
        """
        if len(word) < 3:
            return word
        
        best_match = word
        best_score = 0.0
        
        for typo, correct in self.common_corrections.items():
            score = SequenceMatcher(None, word, typo).ratio()
            if score > best_score and score > 0.8:
                best_score = score
                best_match = correct
        
        return best_match
    
    def detect_intent_pattern(self, text: str) -> Tuple[str, float]:
        """
        Detect intent using pattern matching.
        
        Args:
            text: Normalized text
            
        Returns:
            Tuple of (intent, confidence)
        """
        text_lower = text.lower()
        
        # Check each intent pattern
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    # Calculate confidence based on pattern match
                    confidence = 0.8 if len(pattern) > 3 else 0.7
                    return intent, confidence
        
        return 'unknown', 0.3
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {
            'numbers': [],
            'locations': [],
            'operators': []
        }
        
        # Extract numbers
        numbers = re.findall(r'\b\d+\.?\d*\b', text)
        entities['numbers'] = [float(n) for n in numbers]
        
        # Extract math operators
        operators = re.findall(r'[+\-*/^]', text)
        entities['operators'] = operators
        
        # Extract potential locations (simple approach)
        # Look for "in [location]" or "at [location]"
        location_match = re.search(r'\b(?:in|at|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
        if location_match:
            entities['locations'].append(location_match.group(1))
        
        return entities
    
    def is_valid_input(self, text: str) -> bool:
        """
        Check if input is valid.
        
        Args:
            text: Input text
            
        Returns:
            True if valid
        """
        if not text or len(text.strip()) == 0:
            return False
        
        if len(text.strip()) > 1000:
            return False
        
        return True
    
    def preprocess(self, text: str) -> Dict[str, Any]:
        """
        Complete preprocessing pipeline.
        
        Args:
            text: Raw user input
            
        Returns:
            Preprocessed data
        """
        # Validate
        if not self.is_valid_input(text):
            return {
                'original': text,
                'normalized': '',
                'valid': False,
                'intent': 'invalid',
                'confidence': 0.0
            }
        
        # Normalize
        normalized = self.normalize(text)
        
        # Detect intent
        intent, confidence = self.detect_intent_pattern(normalized)
        
        # Extract entities
        entities = self.extract_entities(text)
        
        return {
            'original': text,
            'normalized': normalized,
            'valid': True,
            'intent': intent,
            'confidence': confidence,
            'entities': entities
        }


class SemanticMatcher:
    """Semantic similarity matching using embeddings."""
    
    def __init__(self):
        """Initialize semantic matcher."""
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Semantic matcher initialized")
        except ImportError:
            logger.warning("Sentence transformers not available")
        except Exception as e:
            logger.error(f"Failed to load semantic matcher: {e}")
    
    async def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        if not self.model:
            return 0.0
        
        try:
            embeddings = await asyncio.to_thread(
                self.model.encode,
                [text1, text2]
            )
            
            # Compute cosine similarity
            from numpy import dot
            from numpy.linalg import norm
            
            similarity = dot(embeddings[0], embeddings[1]) / (
                norm(embeddings[0]) * norm(embeddings[1])
            )
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Similarity computation failed: {e}")
            return 0.0
    
    async def find_best_match(
        self,
        query: str,
        candidates: List[str],
        threshold: float = 0.7
    ) -> Tuple[Optional[str], float]:
        """
        Find best matching candidate.
        
        Args:
            query: Query text
            candidates: List of candidate texts
            threshold: Minimum similarity threshold
            
        Returns:
            Tuple of (best_match, similarity_score)
        """
        if not self.model or not candidates:
            return None, 0.0
        
        try:
            # Encode all texts
            all_texts = [query] + candidates
            embeddings = await asyncio.to_thread(
                self.model.encode,
                all_texts
            )
            
            query_embedding = embeddings[0]
            candidate_embeddings = embeddings[1:]
            
            # Find best match
            from numpy import dot
            from numpy.linalg import norm
            
            best_score = 0.0
            best_match = None
            
            for i, candidate_embedding in enumerate(candidate_embeddings):
                similarity = dot(query_embedding, candidate_embedding) / (
                    norm(query_embedding) * norm(candidate_embedding)
                )
                
                if similarity > best_score:
                    best_score = float(similarity)
                    best_match = candidates[i]
            
            if best_score >= threshold:
                return best_match, best_score
            
            return None, best_score
            
        except Exception as e:
            logger.error(f"Best match search failed: {e}")
            return None, 0.0
