"""Enhanced Entity Extraction with advanced NER and slot filling."""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime

from core.models import Entity
from core.logger import get_logger

logger = get_logger(__name__)


class EnhancedEntityExtractor:
    """
    Advanced entity extraction with:
    - spaCy/Stanza NER
    - Custom domain-specific patterns
    - Context-aware classification
    - Coreference resolution
    """
    
    def __init__(self):
        self.spacy_nlp = None
        self.custom_patterns = self._initialize_patterns()
        self.entity_cache = {}
        self._initialize_spacy()
    
    def _initialize_spacy(self):
        """Initialize spaCy for advanced NER."""
        try:
            import spacy
            try:
                self.spacy_nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy NER initialized for entity extraction")
            except OSError:
                logger.warning("spaCy model not found")
        except ImportError:
            logger.warning("spaCy not available")
    
    def _initialize_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize comprehensive regex patterns."""
        return {
            'EMAIL': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'URL': re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'),
            'PHONE': re.compile(r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b'),
            'FILE_PATH': re.compile(r'(?:[a-zA-Z]:\\|/)?(?:[\w\-]+[/\\])*[\w\-]+\.[\w]+'),
            'IP_ADDRESS': re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            'TIME': re.compile(r'\b(?:[01]?[0-9]|2[0-3]):[0-5][0-9](?::[0-5][0-9])?\s*(?:AM|PM|am|pm)?\b'),
            'MONEY': re.compile(r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?'),
            'PERCENTAGE': re.compile(r'\b\d+(?:\.\d+)?%\b'),
            'VERSION': re.compile(r'\bv?\d+\.\d+(?:\.\d+)?(?:-[\w.]+)?\b'),
            'HEX_COLOR': re.compile(r'#[0-9A-Fa-f]{6}\b'),
            'MINECRAFT_COMMAND': re.compile(r'/\w+(?:\s+\w+)*'),
            'CLI_COMMAND': re.compile(r'\b(npm|pip|git|docker|kubectl|yarn|cargo|mvn|gradle)\s+[\w-]+'),
            'CODE_BLOCK': re.compile(r'```[\w]*\n(.*?)\n```', re.DOTALL),
            'FUNCTION_CALL': re.compile(r'\b\w+\([^)]*\)'),
        }
    
    def extract_all_entities(
        self,
        text: str,
        use_spacy: bool = True,
        use_custom: bool = True
    ) -> List[Entity]:
        """
        Extract all entities using multiple methods.
        
        Args:
            text: Input text
            use_spacy: Use spaCy NER
            use_custom: Use custom patterns
            
        Returns:
            List of extracted entities
        """
        entities = []
        
        # spaCy NER
        if use_spacy and self.spacy_nlp:
            entities.extend(self._extract_spacy_entities(text))
        
        # Custom patterns
        if use_custom:
            entities.extend(self._extract_custom_entities(text))
        
        # Application names
        entities.extend(self._extract_applications(text))
        
        # Action verbs
        entities.extend(self._extract_actions(text))
        
        # Merge overlapping
        entities = self._merge_overlapping(entities)
        
        # Context classification
        for entity in entities:
            entity.type = self._classify_context(entity, text)
            entity.confidence = self._score_confidence(entity, text)
        
        # Resolve coreferences
        entities = self._resolve_coreferences(entities, text)
        
        return entities
    
    def _extract_spacy_entities(self, text: str) -> List[Entity]:
        """Extract entities using spaCy."""
        entities = []
        try:
            doc = self.spacy_nlp(text)
            for ent in doc.ents:
                entity = Entity(
                    text=ent.text,
                    type=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.85
                )
                entities.append(entity)
        except Exception as e:
            logger.error(f"spaCy extraction failed: {e}")
        return entities
    
    def _extract_custom_entities(self, text: str) -> List[Entity]:
        """Extract using custom patterns."""
        entities = []
        for pattern_name, pattern in self.custom_patterns.items():
            for match in pattern.finditer(text):
                entity = Entity(
                    text=match.group(),
                    type=pattern_name,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.95
                )
                entities.append(entity)
        return entities
    
    def _extract_applications(self, text: str) -> List[Entity]:
        """Extract application names."""
        apps = [
            'chrome', 'firefox', 'vscode', 'minecraft', 'spotify',
            'discord', 'slack', 'docker', 'git', 'npm', 'python'
        ]
        entities = []
        text_lower = text.lower()
        for app in apps:
            if app in text_lower:
                start = text_lower.index(app)
                entity = Entity(
                    text=text[start:start+len(app)],
                    type='APPLICATION',
                    start=start,
                    end=start+len(app),
                    confidence=0.9
                )
                entities.append(entity)
        return entities
    
    def _extract_actions(self, text: str) -> List[Entity]:
        """Extract action verbs."""
        actions = [
            'open', 'close', 'start', 'stop', 'install', 'run',
            'create', 'delete', 'update', 'search', 'find'
        ]
        entities = []
        words = text.lower().split()
        for word in words:
            if word in actions:
                pattern = r'\b' + re.escape(word) + r'\b'
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entity = Entity(
                        text=match.group(),
                        type='ACTION',
                        start=match.start(),
                        end=match.end(),
                        confidence=0.95
                    )
                    entities.append(entity)
        return entities
    
    def _merge_overlapping(self, entities: List[Entity]) -> List[Entity]:
        """Merge overlapping entities."""
        if not entities:
            return []
        sorted_entities = sorted(entities, key=lambda e: e.start)
        merged = [sorted_entities[0]]
        for entity in sorted_entities[1:]:
            last = merged[-1]
            if entity.start < last.end:
                if entity.confidence > last.confidence:
                    merged[-1] = entity
            else:
                merged.append(entity)
        return merged
    
    def _classify_context(self, entity: Entity, text: str) -> str:
        """Classify entity based on context."""
        start = max(0, entity.start - 50)
        end = min(len(text), entity.end + 50)
        context = text[start:end].lower()
        
        if entity.type == 'ORG':
            if any(w in context for w in ['open', 'launch', 'start']):
                return 'APPLICATION'
        elif entity.type == 'GPE':
            if 'weather' in context:
                return 'LOCATION_WEATHER'
        
        return entity.type
    
    def _score_confidence(self, entity: Entity, text: str) -> float:
        """Calculate confidence score."""
        confidence = entity.confidence
        if len(entity.text) > 10:
            confidence = min(confidence + 0.05, 1.0)
        if ' ' in entity.text:
            confidence = min(confidence + 0.1, 1.0)
        return confidence
    
    def _resolve_coreferences(self, entities: List[Entity], text: str) -> List[Entity]:
        """Simple coreference resolution."""
        pronouns = ['it', 'this', 'that']
        resolved = []
        last_entity = None
        
        for entity in entities:
            if entity.text.lower() in pronouns and last_entity:
                resolved_entity = Entity(
                    text=last_entity.text,
                    type=last_entity.type,
                    start=entity.start,
                    end=entity.end,
                    confidence=entity.confidence * 0.8
                )
                resolved.append(resolved_entity)
            else:
                resolved.append(entity)
                if entity.type in ['PERSON', 'ORG', 'APPLICATION']:
                    last_entity = entity
        
        return resolved
