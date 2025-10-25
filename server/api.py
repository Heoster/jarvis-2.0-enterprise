"""FastAPI server for local assistant API with Codeex personality."""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio

from core.logger import get_logger
from core.grammar_corrector import get_corrector
from core.codeex_personality import CodeexPersonality
from core.quiz_engine import get_quiz_engine

logger = get_logger(__name__)


# Request/Response models
class QueryRequest(BaseModel):
    """Query request model."""
    text: str
    context: Optional[Dict[str, Any]] = None
    stream: bool = False


class QueryResponse(BaseModel):
    """Query response model."""
    text: str
    intent: str
    sources: List[Dict[str, Any]] = []
    confidence: float
    execution_time: float


class StatusResponse(BaseModel):
    """Status response model."""
    status: str
    version: str
    uptime: float


class MemoryRequest(BaseModel):
    """Memory storage request."""
    key: str
    value: Any
    encrypt: bool = False


class CorrectionRequest(BaseModel):
    """Grammar correction request."""
    text: str
    language: str = 'en-US'


class QuizRequest(BaseModel):
    """Quiz generation request."""
    topic: str
    num_questions: int = 5
    difficulty: Optional[str] = None


class QuizAnswerRequest(BaseModel):
    """Quiz answer submission."""
    quiz_id: str
    answer: int


class LocalServer:
    """Local FastAPI server for assistant."""
    
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        cors_origins: Optional[List[str]] = None
    ):
        """
        Initialize local server.
        
        Args:
            host: Server host
            port: Server port
            cors_origins: Allowed CORS origins
        """
        self.host = host
        self.port = port
        self.app = FastAPI(title="On-Device Assistant API", version="0.1.0")
        
        # Configure CORS
        if cors_origins is None:
            cors_origins = ["http://localhost:*", "http://127.0.0.1:*"]
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize Codeex personality
        self.personality = CodeexPersonality()
        self.corrector = get_corrector()
        self.quiz_engine = get_quiz_engine()
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"Server initialized at {host}:{port}")
    
    def _setup_routes(self) -> None:
        """Setup API routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint."""
            greeting = self.personality.get_greeting()
            return {
                "message": "Codeex AI - Your Magical Learning Assistant",
                "version": "0.2.0",
                "greeting": greeting
            }
        
        @self.app.get("/api/v1/status", response_model=StatusResponse)
        async def get_status():
            """Get server status."""
            return StatusResponse(
                status="running",
                version="0.1.0",
                uptime=0.0  # Would track actual uptime
            )
        
        @self.app.post("/api/v1/query", response_model=QueryResponse)
        async def process_query(request: QueryRequest):
            """
            Process user query.
            
            Args:
                request: Query request
                
            Returns:
                Query response
            """
            try:
                # This would integrate with the main assistant pipeline
                # For now, return a placeholder
                return QueryResponse(
                    text="Response would be generated here",
                    intent="question",
                    sources=[],
                    confidence=0.8,
                    execution_time=0.5
                )
            except Exception as e:
                logger.error(f"Query processing failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/memory")
        async def store_memory(request: MemoryRequest):
            """
            Store data in memory.
            
            Args:
                request: Memory request
                
            Returns:
                Success status
            """
            try:
                # Would integrate with memory store
                return {"success": True, "key": request.key}
            except Exception as e:
                logger.error(f"Memory storage failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/memory/{key}")
        async def get_memory(key: str):
            """
            Retrieve data from memory.
            
            Args:
                key: Memory key
                
            Returns:
                Stored value
            """
            try:
                # Would integrate with memory store
                return {"key": key, "value": None}
            except Exception as e:
                logger.error(f"Memory retrieval failed: {e}")
                raise HTTPException(status_code=404, detail="Key not found")
        
        @self.app.get("/api/v1/permissions")
        async def get_permissions():
            """Get all permissions."""
            try:
                # Would integrate with consent manager
                return {"permissions": []}
            except Exception as e:
                logger.error(f"Permission retrieval failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/activity")
        async def get_activity(hours: int = 24):
            """
            Get recent activity.
            
            Args:
                hours: Hours to look back
                
            Returns:
                Activity logs
            """
            try:
                # Would integrate with activity monitor
                return {"activity": [], "hours": hours}
            except Exception as e:
                logger.error(f"Activity retrieval failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/config")
        async def get_config():
            """Get configuration."""
            try:
                # Would return sanitized config
                return {"config": {}}
            except Exception as e:
                logger.error(f"Config retrieval failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/correct")
        async def correct_text(request: CorrectionRequest):
            """
            Correct grammar and spelling.
            
            Args:
                request: Text to correct
                
            Returns:
                Corrected text with feedback
            """
            try:
                result = self.corrector.correct_text(request.text)
                
                # Add Codeex personality
                if result['has_errors']:
                    formatted = self.personality.format_correction(
                        result['original'],
                        result['corrected'],
                        [c.get('message', str(c)) for c in result['corrections']]
                    )
                else:
                    formatted = self.personality.wrap_response(
                        "Perfect! Your sentence is already magical!",
                        'success'
                    )
                
                return {
                    **result,
                    'formatted_message': formatted
                }
            except Exception as e:
                logger.error(f"Correction failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/magic")
        async def magic_response(request: QueryRequest):
            """
            Get magical Codeex-style response.
            
            Args:
                request: Query request
                
            Returns:
                Magical response
            """
            try:
                # Process query with personality
                greeting = self.personality.get_greeting()
                response = self.personality.wrap_response(
                    f"I received your question: '{request.text}'. Let me help you with that!",
                    'learning'
                )
                
                return {
                    'greeting': greeting,
                    'response': response,
                    'encouragement': self.personality.get_encouragement()
                }
            except Exception as e:
                logger.error(f"Magic response failed: {e}")
                error_msg = self.personality.get_error_message()
                raise HTTPException(status_code=500, detail=error_msg)
        
        @self.app.post("/api/v1/quiz/create")
        async def create_quiz(request: QuizRequest):
            """
            Create a new quiz.
            
            Args:
                request: Quiz parameters
                
            Returns:
                Quiz data
            """
            try:
                quiz = self.quiz_engine.generate_quiz(
                    request.topic,
                    request.num_questions,
                    request.difficulty
                )
                
                # Get first question
                first_question = self.quiz_engine.get_current_question(quiz['id'])
                
                # Format with personality
                if first_question:
                    formatted = self.personality.format_quiz_question(
                        first_question['question'],
                        first_question['options'],
                        first_question.get('difficulty', 'medium')
                    )
                    first_question['formatted'] = formatted
                
                return {
                    'quiz_id': quiz['id'],
                    'topic': quiz['topic'],
                    'total_questions': len(quiz['questions']),
                    'current_question': first_question
                }
            except Exception as e:
                logger.error(f"Quiz creation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/quiz/answer")
        async def submit_quiz_answer(request: QuizAnswerRequest):
            """
            Submit quiz answer.
            
            Args:
                request: Answer submission
                
            Returns:
                Answer result
            """
            try:
                result = self.quiz_engine.submit_answer(
                    request.quiz_id,
                    request.answer
                )
                
                if 'error' in result:
                    raise HTTPException(status_code=400, detail=result['error'])
                
                # Add personality
                if result['correct']:
                    message = self.personality.wrap_response(
                        f"Correct! {result['explanation']}",
                        'success'
                    )
                else:
                    message = self.personality.wrap_response(
                        f"Not quite! {result['explanation']}",
                        'learning'
                    )
                
                result['message'] = message
                
                # Get next question if not completed
                if not result['completed']:
                    next_q = self.quiz_engine.get_current_question(request.quiz_id)
                    if next_q:
                        next_q['formatted'] = self.personality.format_quiz_question(
                            next_q['question'],
                            next_q['options'],
                            next_q.get('difficulty', 'medium')
                        )
                    result['next_question'] = next_q
                else:
                    # Get final results
                    final = self.quiz_engine.get_quiz_results(request.quiz_id)
                    result['final_results'] = final
                
                return result
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Answer submission failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/quiz/results/{quiz_id}")
        async def get_quiz_results(quiz_id: str):
            """Get quiz results."""
            try:
                results = self.quiz_engine.get_quiz_results(quiz_id)
                if not results:
                    raise HTTPException(status_code=404, detail="Quiz not found")
                
                # Add celebration message
                results['celebration'] = self.personality.wrap_response(
                    results['message'],
                    'celebration'
                )
                
                return results
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Results retrieval failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/quiz/topics")
        async def get_quiz_topics():
            """Get available quiz topics."""
            try:
                topics = self.quiz_engine.get_topics()
                return {
                    'topics': topics,
                    'message': self.personality.wrap_response(
                        f"I have quizzes on {len(topics)} topics!",
                        'learning'
                    )
                }
            except Exception as e:
                logger.error(f"Topics retrieval failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/quiz/stats")
        async def get_quiz_stats():
            """Get quiz statistics."""
            try:
                stats = self.quiz_engine.get_quiz_stats()
                return {
                    **stats,
                    'message': self.personality.wrap_response(
                        f"You've completed {stats['total_quizzes']} quizzes! Keep learning!",
                        'celebration'
                    )
                }
            except Exception as e:
                logger.error(f"Stats retrieval failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.websocket("/ws/assistant")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time communication."""
            await self.handle_websocket(websocket)
    
    async def handle_websocket(self, websocket: WebSocket) -> None:
        """
        Handle WebSocket connection.
        
        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        logger.info("WebSocket connection established")
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_json()
                
                # Process message
                message_type = data.get('type', 'query')
                
                if message_type == 'query':
                    # Process query
                    response = {
                        'type': 'response',
                        'text': 'WebSocket response',
                        'timestamp': '2024-10-24T12:00:00Z'
                    }
                    await websocket.send_json(response)
                
                elif message_type == 'ping':
                    # Heartbeat
                    await websocket.send_json({'type': 'pong'})
                
        except WebSocketDisconnect:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
    
    async def start(self) -> None:
        """Start the server."""
        import uvicorn
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    
    async def stop(self) -> None:
        """Stop the server."""
        logger.info("Server stopping")
