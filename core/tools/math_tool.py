"""
Mathematical computation tool.
Standardized interface for math operations.
"""

from typing import Dict, Any, List
from .base_tool import BaseTool, ToolResult
from execution.math_engine import MathEngine


class MathTool(BaseTool):
    """Mathematical computation tool with standardized interface"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.math_engine = MathEngine()
    
    def get_required_fields(self) -> List[str]:
        """Get required input fields"""
        return ['expression']
    
    def get_optional_fields(self) -> List[str]:
        """Get optional input fields"""
        return ['operation_type', 'variable', 'precision']
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        if 'expression' not in input_data:
            return False
        
        expression = input_data['expression']
        if not isinstance(expression, str) or len(expression.strip()) == 0:
            return False
        
        # Basic validation for dangerous operations
        dangerous_patterns = ['import', 'exec', 'eval', '__', 'os.', 'sys.']
        expression_lower = expression.lower()
        
        for pattern in dangerous_patterns:
            if pattern in expression_lower:
                return False
        
        return True
    
    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        """
        Execute mathematical computation.
        
        Args:
            input_data: Math parameters
                - expression (str): Mathematical expression
                - operation_type (str, optional): Type of operation (evaluate, solve, differentiate, integrate)
                - variable (str, optional): Variable for calculus operations (default: 'x')
                - precision (int, optional): Decimal precision
        
        Returns:
            ToolResult with computation results
        """
        try:
            expression = input_data['expression'].strip()
            operation_type = input_data.get('operation_type', 'evaluate')
            variable = input_data.get('variable', 'x')
            
            self.logger.info(f"Computing: {expression} (operation: {operation_type})")
            
            # Route to appropriate math operation
            if operation_type == 'evaluate':
                result = await self.math_engine.evaluate(expression)
            elif operation_type == 'solve':
                result = await self.math_engine.solve_equation(expression, variable)
            elif operation_type == 'differentiate':
                result = await self.math_engine.differentiate(expression, variable)
            elif operation_type == 'integrate':
                result = await self.math_engine.integrate(expression, variable)
            else:
                return self._create_error_result(f"Unknown operation type: {operation_type}")
            
            if result.get('success'):
                metadata = {
                    'expression': expression,
                    'operation_type': operation_type,
                    'variable': variable if operation_type != 'evaluate' else None
                }
                
                return self._create_success_result(result, metadata)
            else:
                error_msg = result.get('error', 'Computation failed')
                return self._create_error_result(error_msg)
                
        except Exception as e:
            self.logger.error(f"Math computation failed: {e}")
            return self._create_error_result(str(e))
    
    async def evaluate_expression(self, expression: str) -> ToolResult:
        """
        Evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            ToolResult with evaluation result
        """
        return await self.execute({
            'expression': expression,
            'operation_type': 'evaluate'
        })
    
    async def solve_equation(self, equation: str, variable: str = 'x') -> ToolResult:
        """
        Solve an algebraic equation.
        
        Args:
            equation: Equation to solve
            variable: Variable to solve for
            
        Returns:
            ToolResult with solutions
        """
        return await self.execute({
            'expression': equation,
            'operation_type': 'solve',
            'variable': variable
        })
    
    async def differentiate(self, expression: str, variable: str = 'x') -> ToolResult:
        """
        Calculate derivative of expression.
        
        Args:
            expression: Expression to differentiate
            variable: Variable to differentiate with respect to
            
        Returns:
            ToolResult with derivative
        """
        return await self.execute({
            'expression': expression,
            'operation_type': 'differentiate',
            'variable': variable
        })
    
    async def integrate(self, expression: str, variable: str = 'x') -> ToolResult:
        """
        Calculate integral of expression.
        
        Args:
            expression: Expression to integrate
            variable: Variable to integrate with respect to
            
        Returns:
            ToolResult with integral
        """
        return await self.execute({
            'expression': expression,
            'operation_type': 'integrate',
            'variable': variable
        })
    
    async def convert_units(self, value: float, from_unit: str, to_unit: str) -> ToolResult:
        """
        Convert between units.
        
        Args:
            value: Value to convert
            from_unit: Source unit
            to_unit: Target unit
            
        Returns:
            ToolResult with conversion result
        """
        try:
            result = await self.math_engine.convert_units(value, from_unit, to_unit)
            
            if result.get('success'):
                metadata = {
                    'conversion': f"{value} {from_unit} to {to_unit}",
                    'from_value': value,
                    'from_unit': from_unit,
                    'to_unit': to_unit
                }
                
                return self._create_success_result(result, metadata)
            else:
                error_msg = result.get('error', 'Unit conversion failed')
                return self._create_error_result(error_msg)
                
        except Exception as e:
            self.logger.error(f"Unit conversion failed: {e}")
            return self._create_error_result(str(e))
    
    async def calculate_statistics(self, numbers: List[float]) -> ToolResult:
        """
        Calculate statistics for a list of numbers.
        
        Args:
            numbers: List of numbers
            
        Returns:
            ToolResult with statistics
        """
        try:
            if not numbers or not all(isinstance(n, (int, float)) for n in numbers):
                return self._create_error_result("Invalid number list")
            
            result = await self.math_engine.statistics(numbers)
            
            if result.get('success'):
                metadata = {
                    'data_points': len(numbers),
                    'min_value': min(numbers),
                    'max_value': max(numbers)
                }
                
                return self._create_success_result(result, metadata)
            else:
                error_msg = result.get('error', 'Statistics calculation failed')
                return self._create_error_result(error_msg)
                
        except Exception as e:
            self.logger.error(f"Statistics calculation failed: {e}")
            return self._create_error_result(str(e))
    
    async def health_check(self) -> bool:
        """Check if math engine is working"""
        try:
            # Try a simple calculation
            test_result = await self.math_engine.evaluate("2 + 2")
            return test_result.get('success', False) and test_result.get('result') == 4.0
        except Exception as e:
            self.logger.error(f"Math tool health check failed: {e}")
            return False