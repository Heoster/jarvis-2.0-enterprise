"""Action execution framework for the On-Device Assistant."""

import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import time

from core.models import Action, ActionPlan, ActionType, ActionStatus
from core.logger import get_logger

logger = get_logger(__name__)


class ExecutionResult:
    """Result of action execution."""
    
    def __init__(
        self,
        action_id: str,
        success: bool,
        result: Any = None,
        error: Optional[str] = None,
        execution_time: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize execution result.
        
        Args:
            action_id: ID of the executed action
            success: Whether execution was successful
            result: Result data
            error: Error message if failed
            execution_time: Time taken to execute in seconds
            metadata: Additional metadata
        """
        self.action_id = action_id
        self.success = success
        self.result = result
        self.error = error
        self.execution_time = execution_time
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'action_id': self.action_id,
            'success': self.success,
            'result': self.result,
            'error': self.error,
            'execution_time': self.execution_time,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


class ActionExecutor:
    """
    Base class for action execution.
    
    Provides async execution, timeout handling, cancellation support,
    and result tracking.
    """
    
    def __init__(self, timeout: float = 30.0):
        """
        Initialize action executor.
        
        Args:
            timeout: Default timeout for action execution in seconds
        """
        self.timeout = timeout
        self.handlers: Dict[ActionType, Callable] = {}
        self.execution_history: List[ExecutionResult] = []
        self._register_handlers()
    
    def _register_handlers(self):
        """Register action type handlers. Override in subclasses."""
        pass
    
    def register_handler(
        self, 
        action_type: ActionType, 
        handler: Callable
    ):
        """
        Register a handler for an action type.
        
        Args:
            action_type: Type of action
            handler: Async function to handle the action
        """
        self.handlers[action_type] = handler
        logger.debug(f"Registered handler for {action_type.value}")
    
    async def execute(
        self, 
        action: Action, 
        timeout: Optional[float] = None
    ) -> ExecutionResult:
        """
        Execute a single action with timeout and error handling.
        
        Args:
            action: Action to execute
            timeout: Optional timeout override
            
        Returns:
            Execution result
        """
        timeout = timeout or self.timeout
        start_time = time.time()
        
        logger.info(f"Executing action {action.id} ({action.type.value})")
        
        # Update action status
        action.status = ActionStatus.RUNNING
        
        try:
            # Get handler for this action type
            handler = self.handlers.get(action.type)
            
            if handler is None:
                raise ValueError(f"No handler registered for action type: {action.type.value}")
            
            # Execute with timeout
            result = await asyncio.wait_for(
                handler(action),
                timeout=timeout
            )
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Update action
            action.status = ActionStatus.COMPLETED
            action.result = result
            
            # Create execution result
            exec_result = ExecutionResult(
                action_id=action.id,
                success=True,
                result=result,
                execution_time=execution_time
            )
            
            logger.info(f"Action {action.id} completed in {execution_time:.2f}s")
            
            # Store in history
            self.execution_history.append(exec_result)
            
            return exec_result
        
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            error_msg = f"Action timed out after {timeout}s"
            
            logger.error(f"Action {action.id} timed out")
            
            action.status = ActionStatus.FAILED
            action.error = error_msg
            
            exec_result = ExecutionResult(
                action_id=action.id,
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
            
            self.execution_history.append(exec_result)
            
            return exec_result
        
        except asyncio.CancelledError:
            execution_time = time.time() - start_time
            error_msg = "Action was cancelled"
            
            logger.warning(f"Action {action.id} was cancelled")
            
            action.status = ActionStatus.CANCELLED
            action.error = error_msg
            
            exec_result = ExecutionResult(
                action_id=action.id,
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
            
            self.execution_history.append(exec_result)
            
            raise  # Re-raise to allow proper cancellation handling
        
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Action failed: {str(e)}"
            
            logger.error(f"Action {action.id} failed: {e}", exc_info=True)
            
            action.status = ActionStatus.FAILED
            action.error = error_msg
            
            exec_result = ExecutionResult(
                action_id=action.id,
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
            
            self.execution_history.append(exec_result)
            
            return exec_result
    
    async def execute_parallel(
        self, 
        actions: List[Action], 
        timeout: Optional[float] = None
    ) -> List[ExecutionResult]:
        """
        Execute multiple actions in parallel.
        
        Args:
            actions: List of actions to execute
            timeout: Optional timeout for each action
            
        Returns:
            List of execution results
        """
        logger.info(f"Executing {len(actions)} actions in parallel")
        
        # Create tasks for all actions
        tasks = [
            asyncio.create_task(self.execute(action, timeout))
            for action in actions
        ]
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to failed results
        execution_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                action = actions[i]
                exec_result = ExecutionResult(
                    action_id=action.id,
                    success=False,
                    error=str(result),
                    execution_time=0.0
                )
                execution_results.append(exec_result)
            else:
                execution_results.append(result)
        
        return execution_results
    
    async def execute_sequential(
        self, 
        actions: List[Action], 
        timeout: Optional[float] = None,
        stop_on_failure: bool = False
    ) -> List[ExecutionResult]:
        """
        Execute actions sequentially.
        
        Args:
            actions: List of actions to execute
            timeout: Optional timeout for each action
            stop_on_failure: Whether to stop if an action fails
            
        Returns:
            List of execution results
        """
        logger.info(f"Executing {len(actions)} actions sequentially")
        
        results = []
        
        for action in actions:
            result = await self.execute(action, timeout)
            results.append(result)
            
            if stop_on_failure and not result.success:
                logger.warning(f"Stopping execution due to failure in action {action.id}")
                break
        
        return results
    
    async def execute_plan(
        self, 
        plan: ActionPlan,
        timeout: Optional[float] = None
    ) -> Dict[str, ExecutionResult]:
        """
        Execute a complete action plan with dependency management.
        
        Args:
            plan: Action plan to execute
            timeout: Optional timeout for each action
            
        Returns:
            Dictionary mapping action IDs to execution results
        """
        logger.info(f"Executing action plan with {len(plan.actions)} actions")
        
        start_time = time.time()
        
        # Import here to avoid circular dependency
        from core.action_planner import DependencyResolver
        
        resolver = DependencyResolver()
        
        # Resolve execution order into stages
        stages = resolver.resolve_execution_order(plan.actions, plan.dependencies)
        
        logger.info(f"Plan has {len(stages)} execution stages")
        
        # Track results
        results = {}
        
        # Execute each stage
        for stage_num, stage_actions in enumerate(stages):
            logger.info(f"Executing stage {stage_num + 1}/{len(stages)} with {len(stage_actions)} actions")
            
            # Execute all actions in this stage in parallel
            stage_results = await self.execute_parallel(stage_actions, timeout)
            
            # Store results
            for result in stage_results:
                results[result.action_id] = result
            
            # Check if any critical actions failed
            failed_actions = [r for r in stage_results if not r.success]
            if failed_actions:
                logger.warning(f"{len(failed_actions)} actions failed in stage {stage_num + 1}")
                
                # Try fallback actions if available
                for failed_result in failed_actions:
                    if failed_result.action_id in plan.fallbacks:
                        fallback_action = plan.fallbacks[failed_result.action_id]
                        logger.info(f"Executing fallback for action {failed_result.action_id}")
                        
                        fallback_result = await self.execute(fallback_action, timeout)
                        
                        # Update result with fallback
                        if fallback_result.success:
                            results[failed_result.action_id] = fallback_result
        
        total_time = time.time() - start_time
        
        # Calculate success rate
        successful = sum(1 for r in results.values() if r.success)
        total = len(results)
        success_rate = (successful / total * 100) if total > 0 else 0
        
        logger.info(
            f"Plan execution completed in {total_time:.2f}s "
            f"({successful}/{total} actions successful, {success_rate:.1f}%)"
        )
        
        return results
    
    def get_execution_history(
        self, 
        limit: Optional[int] = None
    ) -> List[ExecutionResult]:
        """
        Get execution history.
        
        Args:
            limit: Optional limit on number of results
            
        Returns:
            List of execution results
        """
        if limit:
            return self.execution_history[-limit:]
        return self.execution_history.copy()
    
    def clear_history(self):
        """Clear execution history."""
        self.execution_history.clear()
        logger.info("Execution history cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get execution statistics.
        
        Returns:
            Dictionary of statistics
        """
        if not self.execution_history:
            return {
                'total_executions': 0,
                'successful': 0,
                'failed': 0,
                'success_rate': 0.0,
                'average_execution_time': 0.0
            }
        
        total = len(self.execution_history)
        successful = sum(1 for r in self.execution_history if r.success)
        failed = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0.0
        
        avg_time = sum(r.execution_time for r in self.execution_history) / total
        
        return {
            'total_executions': total,
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate,
            'average_execution_time': avg_time
        }


class DefaultActionExecutor(ActionExecutor):
    """
    Default action executor with placeholder handlers.
    
    This provides a basic implementation that can be extended
    with actual execution logic for each action type.
    """
    
    def _register_handlers(self):
        """Register default handlers for all action types."""
        self.register_handler(ActionType.RETRIEVE_MEMORY, self._handle_retrieve_memory)
        self.register_handler(ActionType.RETRIEVE_KNOWLEDGE, self._handle_retrieve_knowledge)
        self.register_handler(ActionType.CALL_API, self._handle_call_api)
        self.register_handler(ActionType.SCRAPE_WEB, self._handle_scrape_web)
        self.register_handler(ActionType.COMPUTE_MATH, self._handle_compute_math)
        self.register_handler(ActionType.EXECUTE_CODE, self._handle_execute_code)
        self.register_handler(ActionType.CONTROL_DEVICE, self._handle_control_device)
        self.register_handler(ActionType.CONTROL_BROWSER, self._handle_control_browser)
        self.register_handler(ActionType.GENERATE_RESPONSE, self._handle_generate_response)
        self.register_handler(ActionType.SPEAK, self._handle_speak)
    
    async def _handle_retrieve_memory(self, action: Action) -> Any:
        """Handle memory retrieval action."""
        logger.debug(f"Retrieving memory: {action.parameters}")
        # Placeholder - will be implemented with actual memory store
        await asyncio.sleep(0.1)  # Simulate work
        return {'documents': [], 'count': 0}
    
    async def _handle_retrieve_knowledge(self, action: Action) -> Any:
        """Handle knowledge retrieval action."""
        logger.debug(f"Retrieving knowledge: {action.parameters}")
        # Placeholder - will be implemented with actual knowledge cache
        await asyncio.sleep(0.1)  # Simulate work
        return {'documents': [], 'count': 0}
    
    async def _handle_call_api(self, action: Action) -> Any:
        """Handle API call action."""
        api_name = action.parameters.get('api', 'generic')
        params = action.parameters.get('params', {})
        
        logger.debug(f"Calling API: {api_name} with params: {params}")
        
        # Weather API
        if api_name == 'weather':
            try:
                from execution.weather_api import WeatherAPI
                weather_api = WeatherAPI()
                city = params.get('city')
                result = await weather_api.get_current_weather(city=city)
                return {
                    'status': 'success',
                    'api': 'weather',
                    'data': result,
                    'text': weather_api.format_weather_text(result)
                }
            except Exception as e:
                logger.error(f"Weather API error: {e}")
                return {'status': 'error', 'error': str(e)}
        
        # News API
        elif api_name == 'news':
            try:
                from execution.news_api import NewsAPI
                news_api = NewsAPI()
                category = params.get('category')
                query = params.get('query')
                
                if query:
                    result = await news_api.search_news(query, page_size=5)
                else:
                    result = await news_api.get_top_headlines(category=category, page_size=5)
                
                return {
                    'status': 'success',
                    'api': 'news',
                    'data': result,
                    'text': news_api.format_news_text(result)
                }
            except Exception as e:
                logger.error(f"News API error: {e}")
                return {'status': 'error', 'error': str(e)}
        
        # Generic/placeholder
        else:
            await asyncio.sleep(0.2)  # Simulate network delay
            return {'status': 'success', 'data': {}, 'api': api_name}
    
    async def _handle_scrape_web(self, action: Action) -> Any:
        """Handle web scraping action."""
        logger.debug(f"Scraping web: {action.parameters}")
        # Placeholder - will be implemented with actual web scraper
        await asyncio.sleep(0.3)  # Simulate scraping
        return {'content': '', 'metadata': {}}
    
    async def _handle_compute_math(self, action: Action) -> Any:
        """Handle math computation action."""
        logger.debug(f"Computing math: {action.parameters}")
        # Placeholder - will be implemented with actual math engine
        await asyncio.sleep(0.05)  # Simulate computation
        return {'result': 0, 'steps': []}
    
    async def _handle_execute_code(self, action: Action) -> Any:
        """Handle code execution action."""
        logger.debug(f"Executing code: {action.parameters}")
        # Placeholder - will be implemented with actual code engine
        await asyncio.sleep(0.1)  # Simulate execution
        return {'stdout': '', 'stderr': '', 'return_code': 0}
    
    async def _handle_control_device(self, action: Action) -> Any:
        """Handle device control action."""
        logger.debug(f"Controlling device: {action.parameters}")
        # Placeholder - will be implemented with actual device controller
        await asyncio.sleep(0.1)  # Simulate device action
        return {'success': True, 'message': 'Device action completed'}
    
    async def _handle_control_browser(self, action: Action) -> Any:
        """Handle browser control action."""
        logger.debug(f"Controlling browser: {action.parameters}")
        # Placeholder - will be implemented with actual browser controller
        await asyncio.sleep(0.1)  # Simulate browser action
        return {'success': True, 'message': 'Browser action completed'}
    
    async def _handle_generate_response(self, action: Action) -> Any:
        """Handle response generation action."""
        logger.debug(f"Generating response: {action.parameters}")
        # Placeholder - will be implemented with actual response generator
        await asyncio.sleep(0.1)  # Simulate generation
        return {'text': 'Generated response', 'confidence': 0.9}
    
    async def _handle_speak(self, action: Action) -> Any:
        """Handle speech synthesis action."""
        logger.debug(f"Speaking: {action.parameters}")
        # Placeholder - will be implemented with actual TTS
        await asyncio.sleep(0.2)  # Simulate speech synthesis
        return {'success': True, 'duration': 1.0}
