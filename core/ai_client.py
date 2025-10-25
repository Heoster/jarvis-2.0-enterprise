"""AI client integrating multiple frameworks for conversational AI."""

import asyncio
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import os

from core.models import IntentCategory
from core.logger import get_logger

logger = get_logger(__name__)


class AIBackend(ABC):
    """Abstract base class for AI backends."""
    
    @abstractmethod
    async def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Generate response from prompt."""
        pass
    
    @abstractmethod
    async def analyze_intent(self, text: str) -> Dict[str, Any]:
        """Analyze user intent."""
        pass


class DialogflowBackend(AIBackend):
    """Google Dialogflow backend for conversational AI."""
    
    def __init__(self, project_id: str, language_code: str = "en"):
        """
        Initialize Dialogflow backend.
        
        Args:
            project_id: Google Cloud project ID
            language_code: Language code for detection
        """
        self.project_id = project_id
        self.language_code = language_code
        self.session_client = None
        
        try:
            from google.cloud import dialogflow
            self.dialogflow = dialogflow
            self.session_client = dialogflow.SessionsClient()
            logger.info(f"Dialogflow initialized for project: {project_id}")
        except ImportError:
            logger.warning("Dialogflow not available - install google-cloud-dialogflow")
        except Exception as e:
            logger.error(f"Failed to initialize Dialogflow: {e}")
    
    async def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        Generate response using Dialogflow.
        
        Args:
            prompt: User input text
            context: Additional context
            
        Returns:
            Generated response
        """
        if not self.session_client:
            return "Dialogflow not available"
        
        try:
            session_id = context.get('session_id', 'default') if context else 'default'
            session = self.session_client.session_path(self.project_id, session_id)
            
            text_input = self.dialogflow.TextInput(
                text=prompt,
                language_code=self.language_code
            )
            query_input = self.dialogflow.QueryInput(text=text_input)
            
            response = await asyncio.to_thread(
                self.session_client.detect_intent,
                request={"session": session, "query_input": query_input}
            )
            
            return response.query_result.fulfillment_text
            
        except Exception as e:
            logger.error(f"Dialogflow generation failed: {e}")
            return f"Error: {str(e)}"
    
    async def analyze_intent(self, text: str) -> Dict[str, Any]:
        """
        Analyze intent using Dialogflow.
        
        Args:
            text: Input text
            
        Returns:
            Intent analysis results
        """
        if not self.session_client:
            return {"intent": "unknown", "confidence": 0.0}
        
        try:
            session = self.session_client.session_path(self.project_id, 'default')
            text_input = self.dialogflow.TextInput(
                text=text,
                language_code=self.language_code
            )
            query_input = self.dialogflow.QueryInput(text=text_input)
            
            response = await asyncio.to_thread(
                self.session_client.detect_intent,
                request={"session": session, "query_input": query_input}
            )
            
            return {
                "intent": response.query_result.intent.display_name,
                "confidence": response.query_result.intent_detection_confidence,
                "parameters": dict(response.query_result.parameters),
                "fulfillment_text": response.query_result.fulfillment_text
            }
            
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            return {"intent": "unknown", "confidence": 0.0, "error": str(e)}


class JarvisBackend(AIBackend):
    """Jarvis AI backend using Transformers + LangChain."""
    
    def __init__(self, model_name: str = "facebook/blenderbot-400M-distill"):
        """
        Initialize Jarvis backend.
        
        Args:
            model_name: Hugging Face model name
        """
        self.model_name = model_name
        self.jarvis_brain = None
        
        try:
            from core.jarvis_brain import JarvisBrain
            self.jarvis_brain = JarvisBrain(model_name=model_name)
            logger.info("Jarvis AI backend initialized with Transformers + LangChain")
        except ImportError as e:
            logger.warning(f"Jarvis backend not fully available: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize Jarvis: {e}")
    
    async def generate(self, prompt: str, context: Optional[Dict] = None) -> str:
        """
        Generate response using Jarvis.
        
        Args:
            prompt: Input prompt
            context: Additional context
            
        Returns:
            Jarvis's response
        """
        if not self.jarvis_brain:
            return "Jarvis is not available at the moment."
        
        try:
            response = await self.jarvis_brain.generate_response(prompt, context)
            return response
            
        except Exception as e:
            logger.error(f"Jarvis generation failed: {e}")
            return "I apologize, but I encountered an error processing your request."
    
    async def analyze_intent(self, text: str) -> Dict[str, Any]:
        """
        Analyze intent using Jarvis.
        
        Args:
            text: Input text
            
        Returns:
            Intent analysis
        """
        # Enhanced keyword-based intent detection
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['what', 'who', 'where', 'when', 'why', 'how', 'tell me']):
            return {"intent": "question", "confidence": 0.85, "assistant": "jarvis"}
        elif any(word in text_lower for word in ['open', 'close', 'start', 'stop', 'run', 'launch']):
            return {"intent": "command", "confidence": 0.85, "assistant": "jarvis"}
        elif any(word in text_lower for word in ['calculate', '+', '-', '*', '/', 'solve', 'compute']):
            return {"intent": "math", "confidence": 0.85, "assistant": "jarvis"}
        elif any(word in text_lower for word in ['weather', 'temperature', 'forecast']):
            return {"intent": "weather", "confidence": 0.9, "assistant": "jarvis"}
        elif any(word in text_lower for word in ['news', 'headlines', 'latest']):
            return {"intent": "news", "confidence": 0.9, "assistant": "jarvis"}
        elif any(word in text_lower for word in ['search', 'find', 'look up']):
            return {"intent": "search", "confidence": 0.85, "assistant": "jarvis"}
        else:
            return {"intent": "general", "confidence": 0.7, "assistant": "jarvis"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get Jarvis status."""
        if self.jarvis_brain:
            return self.jarvis_brain.get_status()
        return {"name": "Jarvis", "status": "unavailable"}


class AIClient:
    """Unified AI client managing multiple backends."""
    
    def __init__(
        self,
        use_dialogflow: bool = False,
        dialogflow_project_id: Optional[str] = None,
        local_model: str = "facebook/blenderbot-400M-distill"
    ):
        """
        Initialize AI client.
        
        Args:
            use_dialogflow: Whether to use Dialogflow
            dialogflow_project_id: Google Cloud project ID
            local_model: Local model name
        """
        self.backends: List[AIBackend] = []
        
        # Initialize Dialogflow if configured
        if use_dialogflow and dialogflow_project_id:
            try:
                dialogflow_backend = DialogflowBackend(dialogflow_project_id)
                self.backends.append(dialogflow_backend)
                logger.info("Dialogflow backend enabled")
            except Exception as e:
                logger.warning(f"Dialogflow initialization failed: {e}")
        
        # Always initialize Jarvis backend as primary/fallback
        try:
            jarvis_backend = JarvisBackend(local_model)
            self.backends.append(jarvis_backend)
            logger.info("Jarvis AI backend enabled (Transformers + LangChain)")
        except Exception as e:
            logger.error(f"Jarvis backend initialization failed: {e}")
        
        if not self.backends:
            logger.error("No AI backends available!")
    
    async def generate(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        backend_preference: Optional[str] = None
    ) -> str:
        """
        Generate response using available backends.
        
        Args:
            prompt: Input prompt
            context: Additional context
            backend_preference: Preferred backend ('dialogflow' or 'local')
            
        Returns:
            Generated response
        """
        if not self.backends:
            return "No AI backends available"
        
        # Try preferred backend first
        if backend_preference == 'dialogflow':
            for backend in self.backends:
                if isinstance(backend, DialogflowBackend):
                    return await backend.generate(prompt, context)
        
        # Use first available backend
        return await self.backends[0].generate(prompt, context)
    
    async def analyze_intent(self, text: str) -> Dict[str, Any]:
        """
        Analyze intent using available backends.
        
        Args:
            text: Input text
            
        Returns:
            Intent analysis
        """
        if not self.backends:
            return {"intent": "unknown", "confidence": 0.0}
        
        # Try Dialogflow first if available
        for backend in self.backends:
            if isinstance(backend, DialogflowBackend):
                result = await backend.analyze_intent(text)
                if result.get('confidence', 0) > 0.5:
                    return result
        
        # Fallback to local backend
        return await self.backends[-1].analyze_intent(text)
    
    def get_available_backends(self) -> List[str]:
        """Get list of available backend names."""
        return [type(backend).__name__ for backend in self.backends]
