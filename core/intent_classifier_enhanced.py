"""
Enhanced Intent Classification with spaCy NER, Rasa-style slot filling, and custom regex.
Implements multi-stage intent detection with confidence scoring and context awareness.
"""

import re
import spacy
from typing import Dict, Any, Optional, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
from pathlib import Path
import asyncio

from core.models import Intent, IntentCategory, Entity
from core.text_utils import normalize_text
from core.semantic_matcher import SemanticMatcher
from core.logger import get_logger

logger = get_logger(__name__)


class EnhancedIntentClassifier:
    """
    Enhanced intent classifier with:
    - spaCy NER for entity extraction
    - Rasa-style slot filling
    - Custom regex for CLI/modding syntax
    - Semantic similarity matching
    - Multi-stage confidence scoring
    """
    
    def __init__(self, model_path: Optional[str] = None, spacy_model: str = "en_core_web_sm"):
        self.model_path = Path(model_path) if model_path else Path("models/intent_classifier_enhanced.pkl")
        self.pipeline: Optional[Pipeline] = None
        self.nlp = None
        self.semantic_matcher = SemanticMatcher()
        
        # Initialize spaCy
        self._initialize_spacy(spacy_model)
        
        # Load or create ML model
        if self.model_path.exists():
            self.load_model()
        else:
            self._create_model()
            self._train_default()
        
        # Initialize slot patterns
        self.slot_patterns = self._initialize_slot_patterns()
        
        # Initialize CLI/modding patterns
        self.cli_patterns = self._initialize_cli_patterns()
        
        logger.info("Enhanced Intent Classifier initialized with spaCy NER and semantic matching")
    
    def _initialize_spacy(self, model_name: str):
        """Initialize spaCy model for NER."""
        try:
            self.nlp = spacy.load(model_name)
            logger.info(f"spaCy model loaded: {model_name}")
        except OSError:
            logger.warning(f"spaCy model {model_name} not found. Run: python -m spacy download {model_name}")
            self.nlp = None
    
    def _initialize_slot_patterns(self) -> Dict[str, List[Dict]]:
        """Initialize Rasa-style slot filling patterns."""
        return {
            'time': [
                {'pattern': r'\b(\d{1,2}):(\d{2})\s*(am|pm)?\b', 'type': 'time'},
                {'pattern': r'\b(morning|afternoon|evening|night)\b', 'type': 'time_period'},
                {'pattern': r'\b(today|tomorrow|yesterday)\b', 'type': 'relative_date'},
            ],
            'location': [
                {'pattern': r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', 'type': 'location'},
                {'pattern': r'\bat\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', 'type': 'location'},
            ],
            'application': [
                {'pattern': r'\b(chrome|firefox|vscode|notepad|calculator|spotify)\b', 'type': 'app_name'},
            ],
            'file_path': [
                {'pattern': r'([A-Za-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*)', 'type': 'windows_path'},
                {'pattern': r'(/(?:[^/\0]+/)*[^/\0]+)', 'type': 'unix_path'},
            ],
            'number': [
                {'pattern': r'\b(\d+\.?\d*)\b', 'type': 'numeric'},
                {'pattern': r'\b(one|two|three|four|five|six|seven|eight|nine|ten)\b', 'type': 'word_number'},
            ],
            'minecraft_mod': [
                {'pattern': r'\b(forge|fabric|bukkit|spigot|paper)\b', 'type': 'mod_loader'},
                {'pattern': r'\b(mod|plugin|datapack)\b', 'type': 'mod_type'},
                {'pattern': r'\b(1\.\d{1,2}(?:\.\d{1,2})?)\b', 'type': 'mc_version'},
            ]
        }
    
    def _initialize_cli_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize CLI and modding syntax patterns."""
        return {
            'git_command': re.compile(r'\bgit\s+(clone|pull|push|commit|add|status|branch|checkout|merge)\b'),
            'npm_command': re.compile(r'\bnpm\s+(install|run|start|build|test|init)\b'),
            'python_command': re.compile(r'\bpython\s+(-m\s+)?[\w.]+'),
            'gradle_command': re.compile(r'\b(gradle|gradlew)\s+(build|clean|run|test)\b'),
            'maven_command': re.compile(r'\bmvn\s+(clean|install|package|test)\b'),
            'docker_command': re.compile(r'\bdocker\s+(run|build|pull|push|ps|stop|start)\b'),
            'minecraft_command': re.compile(r'/(give|tp|gamemode|time|weather|summon|kill)\b'),
            'forge_setup': re.compile(r'\b(setupDecompWorkspace|genIntellijRuns|build)\b'),
        }
    
    def _create_model(self):
        """Create ML classification pipeline."""
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=2000,
                ngram_range=(1, 3),
                stop_words='english',
                min_df=1
            )),
            ('classifier', LogisticRegression(
                max_iter=2000,
                multi_class='multinomial',
                random_state=42,
                C=1.0
            ))
        ])
        logger.info("Created enhanced ML pipeline")
    
    def _train_default(self):
        """Train with enhanced training data."""
        training_data = [
            # Commands
            ("open chrome browser", "command"),
            ("launch visual studio code", "command"),
            ("close all windows", "command"),
            ("git clone repository", "command"),
            ("npm install dependencies", "command"),
            ("run gradle build", "command"),
            
            # Questions
            ("what is machine learning", "question"),
            ("how does forge modding work", "question"),
            ("explain python decorators", "question"),
            ("why is my mod not loading", "question"),
            
            # Math
            ("calculate 15 times 27", "math"),
            ("what is the derivative of x squared", "math"),
            ("solve for x in 2x plus 5 equals 15", "math"),
            
            # Code
            ("write a python function to sort list", "code"),
            ("debug this minecraft mod code", "code"),
            ("create a forge event handler", "code"),
            ("implement binary search algorithm", "code"),
            
            # Fetch
            ("search for forge documentation", "fetch"),
            ("find minecraft modding tutorials", "fetch"),
            ("get latest python news", "fetch"),
            ("look up java streams api", "fetch"),
            
            # Conversational
            ("hello jarvis", "conversational"),
            ("thank you for your help", "conversational"),
            ("that's perfect", "conversational"),
            ("goodbye", "conversational"),
        ]
        
        texts = [text for text, _ in training_data]
        labels = [label for _, label in training_data]
        
        self.pipeline.fit(texts, labels)
        self.save_model()
        logger.info(f"Trained enhanced classifier with {len(training_data)} examples")
    
    async def classify(self, text: str, context: Optional[Dict] = None) -> Intent:
        """
        Enhanced multi-stage intent classification.
        
        Args:
            text: User input
            context: Optional context (conversation history, user preferences)
        
        Returns:
            Intent with enhanced confidence and extracted entities
        """
        return await asyncio.to_thread(self._classify_sync, text, context)
    
    def _classify_sync(self, text: str, context: Optional[Dict] = None) -> Intent:
        """Synchronous classification with multi-stage analysis."""
        # Stage 1: Normalize text
        normalized = normalize_text(text, lowercase=True, remove_punctuation=False)
        
        # Stage 2: Extract entities with spaCy
        entities = self._extract_entities_spacy(text)
        
        # Stage 3: Fill slots with patterns
        slots = self._fill_slots(text)
        
        # Stage 4: Check CLI/modding patterns
        cli_match = self._match_cli_patterns(text)
        
        # Stage 5: ML classification
        ml_prediction = self.pipeline.predict([normalized])[0]
        ml_probabilities = self.pipeline.predict_proba([normalized])[0]
        ml_confidence = float(max(ml_probabilities))
        
        # Stage 6: Semantic similarity boost
        semantic_boost = 0.0
        if context and context.get('recent_intents'):
            semantic_boost = self._calculate_semantic_boost(text, context['recent_intents'])
        
        # Stage 7: Combine confidences
        final_confidence = min(ml_confidence + semantic_boost, 1.0)
        
        # Stage 8: Override based on patterns
        if cli_match:
            category = IntentCategory.COMMAND
            final_confidence = max(final_confidence, 0.9)
        else:
            category = IntentCategory(ml_prediction)
        
        # Stage 9: Build parameters
        parameters = {
            'entities': [e.to_dict() for e in entities],
            'slots': slots,
            'cli_match': cli_match,
            'ml_confidence': ml_confidence,
            'semantic_boost': semantic_boost
        }
        
        return Intent(
            category=category,
            confidence=final_confidence,
            parameters=parameters,
            context={'normalized': normalized, 'entities': entities}
        )
    
    def _extract_entities_spacy(self, text: str) -> List[Entity]:
        """Extract entities using spaCy NER."""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entity = Entity(
                text=ent.text,
                type=ent.label_,
                start=ent.start_char,
                end=ent.end_char,
                confidence=0.9  # spaCy doesn't provide confidence
            )
            entities.append(entity)
        
        return entities
    
    def _fill_slots(self, text: str) -> Dict[str, List[Dict]]:
        """Fill slots using pattern matching (Rasa-style)."""
        filled_slots = {}
        
        for slot_name, patterns in self.slot_patterns.items():
            matches = []
            for pattern_config in patterns:
                pattern = pattern_config['pattern']
                match_type = pattern_config['type']
                
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    matches.append({
                        'value': match.group(0),
                        'type': match_type,
                        'start': match.start(),
                        'end': match.end()
                    })
            
            if matches:
                filled_slots[slot_name] = matches
        
        return filled_slots
    
    def _match_cli_patterns(self, text: str) -> Optional[str]:
        """Match CLI and modding patterns."""
        for pattern_name, pattern in self.cli_patterns.items():
            if pattern.search(text):
                return pattern_name
        return None
    
    def _calculate_semantic_boost(self, text: str, recent_intents: List[str]) -> float:
        """Calculate confidence boost based on semantic similarity to recent intents."""
        if not recent_intents:
            return 0.0
        
        # Use semantic matcher to find similarity
        similarities = []
        for recent in recent_intents[-3:]:  # Last 3 intents
            try:
                sim = asyncio.run(self.semantic_matcher.compute_similarity(text, recent))
                similarities.append(sim)
            except:
                pass
        
        if similarities:
            max_sim = max(similarities)
            return min(max_sim * 0.2, 0.2)  # Max 20% boost
        
        return 0.0
    
    def train(self, texts: List[str], labels: List[str]):
        """
        Train classifier with custom data.
        
        Args:
            texts: List of training texts
            labels: List of corresponding labels
        """
        if len(texts) != len(labels):
            raise ValueError("Number of texts and labels must match")
        
        self.pipeline.fit(texts, labels)
        logger.info(f"Trained enhanced classifier with {len(texts)} examples")
        
        # Save updated model
        self.save_model()
    
    def save_model(self):
        """Save model to disk."""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, self.model_path)
        logger.info(f"Saved enhanced classifier to {self.model_path}")
    
    def load_model(self):
        """Load model from disk."""
        self.pipeline = joblib.load(self.model_path)
        logger.info(f"Loaded enhanced classifier from {self.model_path}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            'status': 'loaded' if self.pipeline else 'not_loaded',
            'spacy_enabled': self.nlp is not None,
            'semantic_matching_enabled': self.semantic_matcher.model is not None,
            'slot_types': list(self.slot_patterns.keys()),
            'cli_patterns': list(self.cli_patterns.keys())
        }
