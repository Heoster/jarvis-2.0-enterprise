"""NLP engine for text analysis and understanding."""

import spacy
from textblob import TextBlob
from typing import List, Optional, Dict, Any
import asyncio

from core.models import NLPResult, Entity, Sentiment, Token, Dependency
from core.entity_extractor import EntityExtractor
from core.logger import get_logger

logger = get_logger(__name__)

# Try to import transformers for advanced sentiment analysis
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers not available, using TextBlob for sentiment analysis")


class NLPEngine:
    """Natural language processing engine using spaCy."""
    
    def __init__(self, model_name: str = "en_core_web_sm", use_transformers: bool = False):
        """
        Initialize NLP engine.
        
        Args:
            model_name: spaCy model to load
            use_transformers: Use transformers for sentiment analysis (slower but more accurate)
        """
        self.model_name = model_name
        self.nlp = None
        self.use_transformers = use_transformers and TRANSFORMERS_AVAILABLE
        self.sentiment_pipeline = None
        self.entity_extractor = EntityExtractor()
        self._load_model()
        
        if self.use_transformers:
            self._load_sentiment_model()
    
    def _load_model(self) -> None:
        """Load spaCy model."""
        try:
            self.nlp = spacy.load(self.model_name)
            logger.info(f"Loaded spaCy model: {self.model_name}")
        except OSError:
            logger.warning(f"Model {self.model_name} not found. Using blank English model as fallback.")
            # Use blank model as fallback
            self.nlp = spacy.blank("en")
            # Add basic components
            if "sentencizer" not in self.nlp.pipe_names:
                self.nlp.add_pipe("sentencizer")
            logger.info("Using blank spaCy model with basic components")
    
    def _load_sentiment_model(self) -> None:
        """Load transformer-based sentiment analysis model."""
        try:
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=-1  # CPU
            )
            logger.info("Loaded transformer sentiment analysis model")
        except Exception as e:
            logger.warning(f"Failed to load transformer sentiment model: {e}")
            self.use_transformers = False
    
    async def analyze(self, text: str) -> NLPResult:
        """
        Perform complete NLP analysis on text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            NLPResult with entities, sentiment, tokens, and dependencies
        """
        return await asyncio.to_thread(self._analyze_sync, text)
    
    def _analyze_sync(self, text: str) -> NLPResult:
        """Synchronous NLP analysis with enhanced entity extraction."""
        # Process with spaCy
        doc = self.nlp(text)
        
        # Extract entities from spaCy
        spacy_entities = self._extract_entities(doc)
        
        # Enhance with custom entity extraction
        entities = self.entity_extractor.extract_all_entities(text, spacy_entities)
        
        # Detect sentiment
        sentiment = self._detect_sentiment(text)
        
        # Extract tokens
        tokens = self._extract_tokens(doc)
        
        # Extract dependencies
        dependencies = self._extract_dependencies(doc)
        
        # Detect language (simple heuristic)
        language = doc.lang_
        
        return NLPResult(
            text=text,
            language=language,
            entities=entities,
            sentiment=sentiment,
            tokens=tokens,
            dependencies=dependencies
        )
    
    def _extract_entities(self, doc) -> List[Entity]:
        """
        Extract named entities from spaCy doc with confidence scoring.
        
        Confidence is estimated based on entity length and context.
        """
        entities = []
        
        for ent in doc.ents:
            # Estimate confidence based on entity characteristics
            confidence = self._estimate_entity_confidence(ent, doc)
            
            entity = Entity(
                text=ent.text,
                type=ent.label_,
                start=ent.start_char,
                end=ent.end_char,
                confidence=confidence
            )
            entities.append(entity)
        
        return entities
    
    def _estimate_entity_confidence(self, ent, doc) -> float:
        """
        Estimate confidence score for an entity.
        
        Factors considered:
        - Entity length (longer entities are more reliable)
        - Capitalization (proper capitalization increases confidence)
        - Context (entities in well-formed sentences are more reliable)
        """
        confidence = 0.7  # Base confidence
        
        # Longer entities are more reliable
        if len(ent.text.split()) > 1:
            confidence += 0.15
        
        # Proper capitalization
        if ent.text[0].isupper():
            confidence += 0.1
        
        # Check if entity is in a well-formed sentence
        if ent.sent and len(ent.sent) > 3:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _detect_sentiment(self, text: str) -> Sentiment:
        """
        Detect sentiment using TextBlob or transformers.
        
        Uses transformer model if available and enabled, otherwise falls back to TextBlob.
        """
        if self.use_transformers and self.sentiment_pipeline:
            return self._detect_sentiment_transformers(text)
        else:
            return self._detect_sentiment_textblob(text)
    
    def _detect_sentiment_textblob(self, text: str) -> Sentiment:
        """Detect sentiment using TextBlob."""
        blob = TextBlob(text)
        
        # Get polarity and subjectivity
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        
        # Determine label
        if polarity > 0.1:
            label = "positive"
        elif polarity < -0.1:
            label = "negative"
        else:
            label = "neutral"
        
        return Sentiment(
            polarity=polarity,
            subjectivity=subjectivity,
            label=label
        )
    
    def _detect_sentiment_transformers(self, text: str) -> Sentiment:
        """Detect sentiment using transformer model."""
        try:
            result = self.sentiment_pipeline(text[:512])[0]  # Limit text length
            
            # Convert transformer output to our format
            label = result['label'].lower()  # POSITIVE, NEGATIVE, NEUTRAL
            score = result['score']
            
            # Map to polarity (-1 to 1)
            if label == 'positive':
                polarity = score
            elif label == 'negative':
                polarity = -score
            else:
                polarity = 0.0
            
            # Estimate subjectivity (transformers don't provide this)
            subjectivity = 0.5  # Default neutral subjectivity
            
            return Sentiment(
                polarity=polarity,
                subjectivity=subjectivity,
                label=label
            )
        except Exception as e:
            logger.warning(f"Transformer sentiment analysis failed: {e}, falling back to TextBlob")
            return self._detect_sentiment_textblob(text)
    
    def _extract_tokens(self, doc) -> List[Token]:
        """Extract tokens with linguistic features."""
        tokens = []
        
        for token in doc:
            # Skip punctuation and whitespace
            if token.is_punct or token.is_space:
                continue
            
            t = Token(
                text=token.text,
                lemma=token.lemma_,
                pos=token.pos_,
                tag=token.tag_,
                dep=token.dep_
            )
            tokens.append(t)
        
        return tokens
    
    def _extract_dependencies(self, doc) -> List[Dependency]:
        """Extract dependency relations."""
        dependencies = []
        
        for token in doc:
            if token.head != token:  # Skip root
                dep = Dependency(
                    head=token.head.text,
                    dependent=token.text,
                    relation=token.dep_
                )
                dependencies.append(dep)
        
        return dependencies

    
    async def extract_entities(self, text: str) -> List[Entity]:
        """
        Extract named entities from text.
        
        Args:
            text: Input text
            
        Returns:
            List of Entity objects
        """
        return await asyncio.to_thread(self._extract_entities_sync, text)
    
    def _extract_entities_sync(self, text: str) -> List[Entity]:
        """Synchronous entity extraction."""
        doc = self.nlp(text)
        return self._extract_entities(doc)
    
    async def detect_sentiment(self, text: str) -> Sentiment:
        """
        Detect sentiment in text.
        
        Args:
            text: Input text
            
        Returns:
            Sentiment object
        """
        return await asyncio.to_thread(self._detect_sentiment, text)
    
    async def parse_semantics(self, text: str) -> dict:
        """
        Parse semantic structure of text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with semantic information
        """
        return await asyncio.to_thread(self._parse_semantics_sync, text)
    
    def _parse_semantics_sync(self, text: str) -> dict:
        """
        Synchronous semantic parsing with enhanced analysis.
        
        Extracts:
        - Noun chunks (noun phrases)
        - Verb phrases
        - Subject-Verb-Object triples
        - Root verb and main action
        - Prepositional phrases
        """
        doc = self.nlp(text)
        
        # Extract noun chunks
        noun_chunks = [chunk.text for chunk in doc.noun_chunks]
        
        # Extract verb phrases
        verb_phrases = []
        for token in doc:
            if token.pos_ == "VERB":
                # Get verb and its direct objects
                phrase = [token.text]
                for child in token.children:
                    if child.dep_ in ("dobj", "pobj", "attr"):
                        phrase.append(child.text)
                verb_phrases.append(" ".join(phrase))
        
        # Extract subject-verb-object triples
        svo_triples = []
        for token in doc:
            if token.pos_ == "VERB":
                subject = None
                obj = None
                
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        subject = child.text
                    elif child.dep_ in ("dobj", "attr", "pobj"):
                        obj = child.text
                
                if subject and obj:
                    svo_triples.append({
                        "subject": subject,
                        "verb": token.text,
                        "object": obj
                    })
        
        # Find root verb (main action)
        root_verb = None
        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                root_verb = token.text
                break
        
        # Extract prepositional phrases
        prep_phrases = []
        for token in doc:
            if token.pos_ == "ADP":  # Preposition
                phrase = [token.text]
                for child in token.children:
                    if child.dep_ == "pobj":
                        phrase.append(child.text)
                if len(phrase) > 1:
                    prep_phrases.append(" ".join(phrase))
        
        return {
            "noun_chunks": noun_chunks,
            "verb_phrases": verb_phrases,
            "svo_triples": svo_triples,
            "root_verb": root_verb,
            "prepositional_phrases": prep_phrases,
            "sentence_count": len(list(doc.sents))
        }
    
    def add_custom_entity_patterns(self, patterns: List[Dict[str, Any]]) -> None:
        """
        Add custom entity patterns for command and action recognition.
        
        Args:
            patterns: List of pattern dictionaries with 'label' and 'pattern' keys
        """
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        else:
            ruler = self.nlp.get_pipe("entity_ruler")
        
        ruler.add_patterns(patterns)
        logger.info(f"Added {len(patterns)} custom entity patterns")
    
    def resolve_entity(self, entity: Entity, context: str) -> Entity:
        """
        Resolve ambiguous entity references using context.
        
        Args:
            entity: Entity to resolve
            context: Surrounding context text
            
        Returns:
            Resolved entity with updated type or confidence
        """
        # Simple resolution based on context keywords
        context_lower = context.lower()
        
        # If entity is ambiguous, try to resolve based on context
        if entity.type == "ORG" and any(word in context_lower for word in ["open", "launch", "start"]):
            # Likely an application name
            entity.type = "APPLICATION"
            entity.confidence = min(entity.confidence + 0.1, 1.0)
        
        elif entity.type == "GPE" and any(word in context_lower for word in ["weather", "time", "news"]):
            # Likely a location for information query
            entity.type = "LOCATION"
            entity.confidence = min(entity.confidence + 0.1, 1.0)
        
        return entity
    
    def extract_command_entities(self, text: str) -> Dict[str, Any]:
        """
        Extract entities specific to commands (apps, actions, targets).
        
        Args:
            text: Command text
            
        Returns:
            Dictionary with command-specific entities
        """
        doc = self.nlp(text)
        
        command_entities = {
            "action": None,
            "target": None,
            "parameters": []
        }
        
        # Find action verb (usually the root or first verb)
        for token in doc:
            if token.pos_ == "VERB" and not command_entities["action"]:
                command_entities["action"] = token.lemma_
                break
        
        # Find target (usually a direct object or proper noun)
        for token in doc:
            if token.dep_ in ("dobj", "pobj") or (token.pos_ == "PROPN" and token.dep_ != "nsubj"):
                if not command_entities["target"]:
                    command_entities["target"] = token.text
                else:
                    command_entities["parameters"].append(token.text)
        
        return command_entities
    
    def get_entity_summary(self, entities: List[Entity]) -> Dict[str, Any]:
        """
        Get summary of extracted entities.
        
        Args:
            entities: List of entities
            
        Returns:
            Summary dictionary
        """
        return self.entity_extractor.get_entity_summary(entities)
    
    def get_model_info(self) -> dict:
        """Get information about loaded model."""
        return {
            "model_name": self.model_name,
            "language": self.nlp.lang,
            "pipeline": self.nlp.pipe_names,
            "vocab_size": len(self.nlp.vocab),
            "use_transformers": self.use_transformers
        }
