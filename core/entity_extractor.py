"""Advanced entity extraction and classification."""

from typing import List, Dict, Any, Optional
import re
from datetime import datetime

from core.models import Entity
from core.logger import get_logger

logger = get_logger(__name__)


class EntityExtractor:
    """
    Advanced entity extraction with custom types and confidence scoring.
    
    Supports standard NER entities plus custom types for:
    - Commands and actions
    - Applications
    - File paths
    - URLs and emails
    - Phone numbers
    - Dates and times
    """
    
    def __init__(self):
        """Initialize entity extractor."""
        self.custom_patterns = self._initialize_patterns()
        self.entity_cache = {}
    
    def _initialize_patterns(self) -> Dict[str, str]:
        """Initialize regex patterns for custom entity types."""
        return {
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'URL': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            'PHONE': r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
            'FILE_PATH': r'(?:[a-zA-Z]:\\|/)?(?:[\w\-]+[/\\])*[\w\-]+\.[\w]+',
            'IP_ADDRESS': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'TIME': r'\b(?:[01]?[0-9]|2[0-3]):[0-5][0-9](?::[0-5][0-9])?\s*(?:AM|PM|am|pm)?\b',
            'MONEY': r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?',
            'PERCENTAGE': r'\b\d+(?:\.\d+)?%\b',
        }
    
    def extract_custom_entities(self, text: str) -> List[Entity]:
        """
        Extract custom entity types using regex patterns.
        
        Args:
            text: Input text
            
        Returns:
            List of Entity objects
        """
        entities = []
        
        for entity_type, pattern in self.custom_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                entity = Entity(
                    text=match.group(),
                    type=entity_type,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.95  # High confidence for regex matches
                )
                entities.append(entity)
        
        return entities
    
    def extract_application_names(self, text: str) -> List[Entity]:
        """
        Extract application names from command text.
        
        Args:
            text: Command text
            
        Returns:
            List of application entities
        """
        # Common application names
        common_apps = [
            'chrome', 'firefox', 'safari', 'edge', 'brave',
            'vscode', 'visual studio code', 'sublime', 'atom', 'notepad',
            'word', 'excel', 'powerpoint', 'outlook',
            'spotify', 'itunes', 'vlc', 'media player',
            'terminal', 'command prompt', 'powershell',
            'calculator', 'calendar', 'mail', 'notes',
            'slack', 'teams', 'zoom', 'discord',
            'photoshop', 'illustrator', 'gimp',
        ]
        
        entities = []
        text_lower = text.lower()
        
        for app in common_apps:
            if app in text_lower:
                start = text_lower.index(app)
                end = start + len(app)
                
                entity = Entity(
                    text=text[start:end],
                    type='APPLICATION',
                    start=start,
                    end=end,
                    confidence=0.9
                )
                entities.append(entity)
        
        return entities
    
    def extract_action_verbs(self, text: str) -> List[Entity]:
        """
        Extract action verbs from command text.
        
        Args:
            text: Command text
            
        Returns:
            List of action entities
        """
        action_verbs = [
            'open', 'close', 'start', 'stop', 'run', 'execute', 'launch',
            'show', 'hide', 'minimize', 'maximize', 'restore',
            'set', 'get', 'change', 'adjust', 'modify',
            'create', 'delete', 'remove', 'add', 'insert',
            'play', 'pause', 'resume', 'skip', 'rewind',
            'search', 'find', 'locate', 'lookup',
            'go', 'navigate', 'browse', 'visit',
            'turn', 'switch', 'toggle', 'enable', 'disable',
            'increase', 'decrease', 'raise', 'lower',
            'send', 'receive', 'download', 'upload',
            'install', 'uninstall', 'update', 'upgrade',
        ]
        
        entities = []
        words = text.lower().split()
        
        for i, word in enumerate(words):
            if word in action_verbs:
                # Find position in original text
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
    
    def classify_entity_context(self, entity: Entity, text: str) -> str:
        """
        Classify entity based on surrounding context.
        
        Args:
            entity: Entity to classify
            text: Full text context
            
        Returns:
            Refined entity type
        """
        # Get context window around entity
        start = max(0, entity.start - 50)
        end = min(len(text), entity.end + 50)
        context = text[start:end].lower()
        
        # Context-based classification
        if entity.type == 'ORG':
            if any(word in context for word in ['open', 'launch', 'start', 'run']):
                return 'APPLICATION'
            elif any(word in context for word in ['company', 'corporation', 'inc', 'ltd']):
                return 'ORGANIZATION'
        
        elif entity.type == 'GPE':
            if any(word in context for word in ['weather', 'forecast', 'temperature']):
                return 'LOCATION_WEATHER'
            elif any(word in context for word in ['time', 'timezone', 'clock']):
                return 'LOCATION_TIME'
            else:
                return 'LOCATION'
        
        elif entity.type == 'DATE':
            if any(word in context for word in ['remind', 'reminder', 'schedule', 'meeting']):
                return 'DATE_REMINDER'
            elif any(word in context for word in ['deadline', 'due', 'by']):
                return 'DATE_DEADLINE'
        
        return entity.type
    
    def resolve_coreferences(self, entities: List[Entity], text: str) -> List[Entity]:
        """
        Resolve pronoun references to entities.
        
        Args:
            entities: List of entities
            text: Full text
            
        Returns:
            Entities with resolved references
        """
        # Simple coreference resolution
        pronouns = ['it', 'this', 'that', 'these', 'those', 'they', 'them']
        
        resolved = []
        last_entity = None
        
        for entity in entities:
            if entity.text.lower() in pronouns and last_entity:
                # Replace pronoun with last entity
                resolved_entity = Entity(
                    text=last_entity.text,
                    type=last_entity.type,
                    start=entity.start,
                    end=entity.end,
                    confidence=entity.confidence * 0.8  # Lower confidence for resolved
                )
                resolved.append(resolved_entity)
            else:
                resolved.append(entity)
                if entity.type in ['PERSON', 'ORG', 'APPLICATION', 'LOCATION']:
                    last_entity = entity
        
        return resolved
    
    def merge_overlapping_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        Merge overlapping entities, keeping the one with higher confidence.
        
        Args:
            entities: List of entities
            
        Returns:
            Merged entity list
        """
        if not entities:
            return []
        
        # Sort by start position
        sorted_entities = sorted(entities, key=lambda e: e.start)
        
        merged = [sorted_entities[0]]
        
        for entity in sorted_entities[1:]:
            last = merged[-1]
            
            # Check for overlap
            if entity.start < last.end:
                # Keep entity with higher confidence
                if entity.confidence > last.confidence:
                    merged[-1] = entity
            else:
                merged.append(entity)
        
        return merged
    
    def score_entity_confidence(self, entity: Entity, text: str) -> float:
        """
        Calculate confidence score for an entity.
        
        Factors:
        - Entity length
        - Capitalization
        - Context quality
        - Pattern match strength
        
        Args:
            entity: Entity to score
            text: Full text context
            
        Returns:
            Confidence score (0-1)
        """
        confidence = entity.confidence
        
        # Length factor
        if len(entity.text) > 10:
            confidence = min(confidence + 0.05, 1.0)
        elif len(entity.text) < 3:
            confidence = max(confidence - 0.1, 0.0)
        
        # Capitalization factor
        if entity.text[0].isupper() and entity.type in ['PERSON', 'ORG', 'GPE']:
            confidence = min(confidence + 0.05, 1.0)
        
        # Multiple word entities are more reliable
        if ' ' in entity.text:
            confidence = min(confidence + 0.1, 1.0)
        
        return confidence
    
    def extract_all_entities(
        self, 
        text: str, 
        spacy_entities: Optional[List[Entity]] = None
    ) -> List[Entity]:
        """
        Extract all entities from text using multiple methods.
        
        Args:
            text: Input text
            spacy_entities: Entities from spaCy NER (optional)
            
        Returns:
            Combined list of all entities
        """
        all_entities = []
        
        # Add spaCy entities if provided
        if spacy_entities:
            all_entities.extend(spacy_entities)
        
        # Add custom pattern entities
        all_entities.extend(self.extract_custom_entities(text))
        
        # Add application names
        all_entities.extend(self.extract_application_names(text))
        
        # Add action verbs
        all_entities.extend(self.extract_action_verbs(text))
        
        # Merge overlapping entities
        all_entities = self.merge_overlapping_entities(all_entities)
        
        # Classify based on context
        for entity in all_entities:
            entity.type = self.classify_entity_context(entity, text)
            entity.confidence = self.score_entity_confidence(entity, text)
        
        # Resolve coreferences
        all_entities = self.resolve_coreferences(all_entities, text)
        
        return all_entities
    
    def get_entity_summary(self, entities: List[Entity]) -> Dict[str, Any]:
        """
        Get summary statistics about extracted entities.
        
        Args:
            entities: List of entities
            
        Returns:
            Summary dictionary
        """
        entity_types = {}
        for entity in entities:
            entity_types[entity.type] = entity_types.get(entity.type, 0) + 1
        
        return {
            'total_entities': len(entities),
            'entity_types': entity_types,
            'avg_confidence': sum(e.confidence for e in entities) / len(entities) if entities else 0,
            'high_confidence_count': sum(1 for e in entities if e.confidence > 0.8),
        }
