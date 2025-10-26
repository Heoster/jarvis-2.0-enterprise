"""
Base tool class for standardized tool interface.
All tools inherit from this base class for consistency.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
import asyncio

from core.logger import get_logger
from core.constants import APISettings


@dataclass
class ToolResult:
    """Standardized tool result format"""
    tool_name: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'tool_name': self.tool_name,
            'success': self.success,
            'result': self.result,
            'error': self.error,
            'metadata': self.metadata or {},
            'execution_time': self.execution_time,
            'timestamp': self.timestamp
        }


class BaseTool(ABC):
    """
    Base class for all tool modules.
    Provides standardized interface and common functionality.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize tool with configuration.
        
        Args:
            config: Tool-specific configuration
        """
        self.config = config or {}
        self.name = self.__class__.__name__
        self.logger = get_logger(self.name)
        self.timeout = self.config.get('timeout', APISettings.REQUEST_TIMEOUT)
        self.max_retries = self.config.get('max_retries', APISettings.MAX_RETRIES)
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        """
        Execute tool with standardized input/output.
        
        Args:
            input_data: Tool input parameters
            
        Returns:
            ToolResult with standardized format
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input before execution.
        
        Args:
            input_data: Input to validate
            
        Returns:
            True if input is valid
        """
        pass
    
    def get_required_fields(self) -> List[str]:
        """
        Get list of required input fields.
        
        Returns:
            List of required field names
        """
        return []
    
    def get_optional_fields(self) -> List[str]:
        """
        Get list of optional input fields.
        
        Returns:
            List of optional field names
        """
        return []
    
    async def execute_with_retry(self, input_data: Dict[str, Any]) -> ToolResult:
        """
        Execute tool with retry logic.
        
        Args:
            input_data: Tool input parameters
            
        Returns:
            ToolResult with execution outcome
        """
        start_time = datetime.now()
        
        for attempt in range(self.max_retries):
            try:
                # Validate input
                if not self.validate_input(input_data):
                    return self._create_error_result(
                        "Invalid input parameters",
                        start_time
                    )
                
                # Execute with timeout
                result = await asyncio.wait_for(
                    self.execute(input_data),
                    timeout=self.timeout
                )
                
                # Calculate execution time
                execution_time = (datetime.now() - start_time).total_seconds()
                result.execution_time = execution_time
                
                return result
                
            except asyncio.TimeoutError:
                self.logger.warning(f"Tool {self.name} timed out on attempt {attempt + 1}")
                if attempt == self.max_retries - 1:
                    return self._create_error_result(
                        f"Tool execution timed out after {self.timeout}s",
                        start_time
                    )
                
            except Exception as e:
                self.logger.error(f"Tool {self.name} failed on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    return self._create_error_result(str(e), start_time)
                
                # Wait before retry
                await asyncio.sleep(APISettings.RATE_LIMIT_DELAY * (attempt + 1))
        
        return self._create_error_result("Max retries exceeded", start_time)
    
    def _create_success_result(
        self,
        result: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """Create successful result"""
        return ToolResult(
            tool_name=self.name,
            success=True,
            result=result,
            metadata=metadata or {}
        )
    
    def _create_error_result(
        self,
        error: str,
        start_time: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ToolResult:
        """Create error result"""
        execution_time = 0.0
        if start_time:
            execution_time = (datetime.now() - start_time).total_seconds()
        
        return ToolResult(
            tool_name=self.name,
            success=False,
            error=error,
            metadata=metadata or {},
            execution_time=execution_time
        )
    
    def get_tool_info(self) -> Dict[str, Any]:
        """
        Get tool information and capabilities.
        
        Returns:
            Tool information dictionary
        """
        return {
            'name': self.name,
            'description': self.__doc__ or "No description available",
            'required_fields': self.get_required_fields(),
            'optional_fields': self.get_optional_fields(),
            'timeout': self.timeout,
            'max_retries': self.max_retries
        }
    
    async def health_check(self) -> bool:
        """
        Perform health check on tool.
        
        Returns:
            True if tool is healthy
        """
        try:
            # Basic validation - can be overridden by subclasses
            return True
        except Exception as e:
            self.logger.error(f"Health check failed for {self.name}: {e}")
            return False


class ToolRegistry:
    """Registry for managing available tools"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self.logger = get_logger(__name__)
    
    def register_tool(self, tool: BaseTool) -> None:
        """Register a tool"""
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get tool by name"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self.tools.keys())
    
    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        tool = self.get_tool(name)
        return tool.get_tool_info() if tool else None
    
    async def execute_tool(
        self,
        name: str,
        input_data: Dict[str, Any]
    ) -> Optional[ToolResult]:
        """Execute a tool by name"""
        tool = self.get_tool(name)
        if not tool:
            return None
        
        return await tool.execute_with_retry(input_data)


# Global tool registry
_tool_registry = ToolRegistry()

def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry"""
    return _tool_registry