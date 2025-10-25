"""Core data models for the On-Device Assistant."""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json
import numpy as np


class IntentCategory(Enum):
    """Intent classification categories."""
    COMMAND = "command"
    QUESTION = "question"
    MATH = "math"
    CODE = "code"
    FETCH = "fetch"
    CONVERSATIONAL = "conversational"


class ActionType(Enum):
    """Types of actions the assistant can perform."""
    RETRIEVE_MEMORY = "retrieve_memory"
    RETRIEVE_KNOWLEDGE = "retrieve_knowledge"
    CALL_API = "call_api"
    SCRAPE_WEB = "scrape_web"
    COMPUTE_MATH = "compute_math"
    EXECUTE_CODE = "execute_code"
    CONTROL_DEVICE = "control_device"
    CONTROL_BROWSER = "control_browser"
    GENERATE_RESPONSE = "generate_response"
    SPEAK = "speak"


class ActionStatus(Enum):
    """Status of action execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class UserInput:
    """Raw user input from any source."""
    text: str
    source: str  # voice, text, api
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserInput':
        """Create from dictionary."""
        data = data.copy()
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)



@dataclass
class Entity:
    """Named entity extracted from text."""
    text: str
    type: str  # PERSON, ORG, DATE, GPE, etc.
    start: int
    end: int
    confidence: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Sentiment:
    """Sentiment analysis result."""
    polarity: float  # -1 to 1
    subjectivity: float  # 0 to 1
    label: str  # positive, negative, neutral
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Sentiment':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Token:
    """Token from text analysis."""
    text: str
    lemma: str
    pos: str  # Part of speech
    tag: str  # Detailed POS tag
    dep: str  # Dependency relation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Dependency:
    """Dependency relation between tokens."""
    head: str
    dependent: str
    relation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class NLPResult:
    """Output from NLP analysis."""
    text: str
    language: str
    entities: List[Entity]
    sentiment: Sentiment
    tokens: List[Token] = field(default_factory=list)
    dependencies: List[Dependency] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'text': self.text,
            'language': self.language,
            'entities': [e.to_dict() for e in self.entities],
            'sentiment': self.sentiment.to_dict(),
            'tokens': [t.to_dict() for t in self.tokens],
            'dependencies': [d.to_dict() for d in self.dependencies],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NLPResult':
        """Create from dictionary."""
        return cls(
            text=data['text'],
            language=data['language'],
            entities=[Entity.from_dict(e) for e in data['entities']],
            sentiment=Sentiment.from_dict(data['sentiment']),
            tokens=[Token(**t) for t in data.get('tokens', [])],
            dependencies=[Dependency(**d) for d in data.get('dependencies', [])],
        )



@dataclass
class Intent:
    """Classified user intent."""
    category: IntentCategory
    confidence: float
    parameters: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'category': self.category.value,
            'confidence': self.confidence,
            'parameters': self.parameters,
            'context': self.context,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Intent':
        """Create from dictionary."""
        return cls(
            category=IntentCategory(data['category']),
            confidence=data['confidence'],
            parameters=data.get('parameters', {}),
            context=data.get('context', {}),
        )


@dataclass
class Action:
    """Single executable action."""
    id: str
    type: ActionType
    parameters: Dict[str, Any]
    estimated_time: float
    priority: int
    status: ActionStatus = ActionStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'type': self.type.value,
            'parameters': self.parameters,
            'estimated_time': self.estimated_time,
            'priority': self.priority,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        """Create from dictionary."""
        return cls(
            id=data['id'],
            type=ActionType(data['type']),
            parameters=data['parameters'],
            estimated_time=data['estimated_time'],
            priority=data['priority'],
            status=ActionStatus(data.get('status', 'pending')),
            result=data.get('result'),
            error=data.get('error'),
        )


@dataclass
class ActionPlan:
    """Complete execution plan."""
    actions: List[Action]
    dependencies: Dict[str, List[str]]  # action_id -> list of dependency action_ids
    estimated_time: float
    fallbacks: Dict[str, Action] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'actions': [a.to_dict() for a in self.actions],
            'dependencies': self.dependencies,
            'estimated_time': self.estimated_time,
            'fallbacks': {k: v.to_dict() for k, v in self.fallbacks.items()},
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionPlan':
        """Create from dictionary."""
        return cls(
            actions=[Action.from_dict(a) for a in data['actions']],
            dependencies=data['dependencies'],
            estimated_time=data['estimated_time'],
            fallbacks={k: Action.from_dict(v) for k, v in data.get('fallbacks', {}).items()},
        )



@dataclass
class Document:
    """Retrieved document with metadata."""
    id: str
    text: str
    source: str  # memory, web, api, training
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 1.0
    
    def to_dict(self, include_embedding: bool = False) -> Dict[str, Any]:
        """
        Convert to dictionary.
        
        Args:
            include_embedding: Whether to include the embedding array
        """
        data = {
            'id': self.id,
            'text': self.text,
            'source': self.source,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'confidence': self.confidence,
        }
        
        if include_embedding and self.embedding is not None:
            data['embedding'] = self.embedding.tolist()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create from dictionary."""
        data = data.copy()
        
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        if 'embedding' in data and data['embedding'] is not None:
            data['embedding'] = np.array(data['embedding'])
        
        return cls(**data)


@dataclass
class Response:
    """Final assistant response."""
    text: str
    sources: List[Document]
    confidence: float
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'text': self.text,
            'sources': [s.to_dict() for s in self.sources],
            'confidence': self.confidence,
            'suggestions': self.suggestions,
            'metadata': self.metadata,
            'execution_time': self.execution_time,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Response':
        """Create from dictionary."""
        return cls(
            text=data['text'],
            sources=[Document.from_dict(s) for s in data['sources']],
            confidence=data['confidence'],
            suggestions=data.get('suggestions', []),
            metadata=data.get('metadata', {}),
            execution_time=data.get('execution_time', 0.0),
        )


@dataclass
class Conversation:
    """Conversation turn."""
    id: str
    user_input: str
    assistant_response: str
    intent: Intent
    actions: List[Action]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_input': self.user_input,
            'assistant_response': self.assistant_response,
            'intent': self.intent.to_dict(),
            'actions': [a.to_dict() for a in self.actions],
            'timestamp': self.timestamp.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create from dictionary."""
        data = data.copy()
        
        if isinstance(data.get('timestamp'), str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        return cls(
            id=data['id'],
            user_input=data['user_input'],
            assistant_response=data['assistant_response'],
            intent=Intent.from_dict(data['intent']),
            actions=[Action.from_dict(a) for a in data['actions']],
            timestamp=data['timestamp'],
        )


def serialize_model(obj: Any) -> str:
    """
    Serialize a model object to JSON string.
    
    Args:
        obj: Model object with to_dict method
        
    Returns:
        JSON string
    """
    if hasattr(obj, 'to_dict'):
        return json.dumps(obj.to_dict())
    return json.dumps(obj)


def deserialize_model(json_str: str, model_class: type) -> Any:
    """
    Deserialize JSON string to model object.
    
    Args:
        json_str: JSON string
        model_class: Model class with from_dict method
        
    Returns:
        Model object
    """
    data = json.loads(json_str)
    if hasattr(model_class, 'from_dict'):
        return model_class.from_dict(data)
    return model_class(**data)
