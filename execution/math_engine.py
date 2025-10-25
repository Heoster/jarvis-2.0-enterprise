"""Mathematical computation engine."""

import sympy as sp
import numpy as np
from scipy import stats
from typing import Any, Dict, Optional, List
import re
import asyncio

from core.logger import get_logger

logger = get_logger(__name__)


class MathEngine:
    """Engine for mathematical computations."""
    
    def __init__(self):
        """Initialize math engine."""
        self.symbols = {}
    
    async def evaluate(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate mathematical expression.
        
        Args:
            expression: Math expression string
            
        Returns:
            Result dictionary with answer and steps
        """
        return await asyncio.to_thread(self._evaluate_sync, expression)
    
    def _evaluate_sync(self, expression: str) -> Dict[str, Any]:
        """Synchronous evaluation."""
        try:
            # Clean expression
            expr = self._clean_expression(expression)
            
            # Parse and evaluate
            result = sp.sympify(expr)
            evaluated = float(result.evalf())
            
            return {
                'result': evaluated,
                'expression': str(result),
                'success': True
            }
        except Exception as e:
            logger.error(f"Math evaluation failed: {e}")
            return {
                'result': None,
                'error': str(e),
                'success': False
            }
    
    def _clean_expression(self, expr: str) -> str:
        """Clean and normalize expression."""
        # Convert common words to operators
        expr = expr.lower()
        expr = expr.replace('plus', '+')
        expr = expr.replace('minus', '-')
        expr = expr.replace('times', '*')
        expr = expr.replace('divided by', '/')
        expr = expr.replace('x', '*')
        
        # Remove extra spaces
        expr = re.sub(r'\s+', '', expr)
        
        return expr
    
    async def solve_equation(self, equation: str, variable: str = 'x') -> Dict[str, Any]:
        """
        Solve algebraic equation.
        
        Args:
            equation: Equation string (e.g., "x^2 - 4 = 0")
            variable: Variable to solve for
            
        Returns:
            Solutions dictionary
        """
        return await asyncio.to_thread(self._solve_equation_sync, equation, variable)
    
    def _solve_equation_sync(self, equation: str, variable: str) -> Dict[str, Any]:
        """Synchronous equation solving."""
        try:
            # Parse equation
            if '=' in equation:
                left, right = equation.split('=')
                expr = sp.sympify(left) - sp.sympify(right)
            else:
                expr = sp.sympify(equation)
            
            # Solve
            var = sp.Symbol(variable)
            solutions = sp.solve(expr, var)
            
            return {
                'solutions': [float(sol.evalf()) if sol.is_number else str(sol) for sol in solutions],
                'equation': equation,
                'variable': variable,
                'success': True
            }
        except Exception as e:
            logger.error(f"Equation solving failed: {e}")
            return {
                'solutions': [],
                'error': str(e),
                'success': False
            }
    
    async def differentiate(self, expression: str, variable: str = 'x') -> Dict[str, Any]:
        """
        Calculate derivative.
        
        Args:
            expression: Expression to differentiate
            variable: Variable to differentiate with respect to
            
        Returns:
            Derivative result
        """
        return await asyncio.to_thread(self._differentiate_sync, expression, variable)
    
    def _differentiate_sync(self, expression: str, variable: str) -> Dict[str, Any]:
        """Synchronous differentiation."""
        try:
            expr = sp.sympify(expression)
            var = sp.Symbol(variable)
            derivative = sp.diff(expr, var)
            
            return {
                'derivative': str(derivative),
                'simplified': str(sp.simplify(derivative)),
                'original': expression,
                'success': True
            }
        except Exception as e:
            logger.error(f"Differentiation failed: {e}")
            return {
                'derivative': None,
                'error': str(e),
                'success': False
            }
    
    async def integrate(self, expression: str, variable: str = 'x') -> Dict[str, Any]:
        """
        Calculate integral.
        
        Args:
            expression: Expression to integrate
            variable: Variable to integrate with respect to
            
        Returns:
            Integral result
        """
        return await asyncio.to_thread(self._integrate_sync, expression, variable)
    
    def _integrate_sync(self, expression: str, variable: str) -> Dict[str, Any]:
        """Synchronous integration."""
        try:
            expr = sp.sympify(expression)
            var = sp.Symbol(variable)
            integral = sp.integrate(expr, var)
            
            return {
                'integral': str(integral),
                'simplified': str(sp.simplify(integral)),
                'original': expression,
                'success': True
            }
        except Exception as e:
            logger.error(f"Integration failed: {e}")
            return {
                'integral': None,
                'error': str(e),
                'success': False
            }
    
    async def convert_units(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """
        Convert between units.
        
        Args:
            value: Value to convert
            from_unit: Source unit
            to_unit: Target unit
            
        Returns:
            Conversion result
        """
        return await asyncio.to_thread(self._convert_units_sync, value, from_unit, to_unit)
    
    def _convert_units_sync(self, value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """Synchronous unit conversion."""
        conversions = {
            ('celsius', 'fahrenheit'): lambda x: x * 9/5 + 32,
            ('fahrenheit', 'celsius'): lambda x: (x - 32) * 5/9,
            ('meters', 'feet'): lambda x: x * 3.28084,
            ('feet', 'meters'): lambda x: x / 3.28084,
            ('kilometers', 'miles'): lambda x: x * 0.621371,
            ('miles', 'kilometers'): lambda x: x / 0.621371,
            ('kilograms', 'pounds'): lambda x: x * 2.20462,
            ('pounds', 'kilograms'): lambda x: x / 2.20462,
        }
        
        key = (from_unit.lower(), to_unit.lower())
        
        if key in conversions:
            result = conversions[key](value)
            return {
                'result': result,
                'from_value': value,
                'from_unit': from_unit,
                'to_unit': to_unit,
                'success': True
            }
        else:
            return {
                'result': None,
                'error': f"Conversion from {from_unit} to {to_unit} not supported",
                'success': False
            }
    
    async def statistics(self, numbers: List[float]) -> Dict[str, Any]:
        """
        Calculate statistics for a list of numbers.
        
        Args:
            numbers: List of numbers
            
        Returns:
            Statistics dictionary
        """
        return await asyncio.to_thread(self._statistics_sync, numbers)
    
    def _statistics_sync(self, numbers: List[float]) -> Dict[str, Any]:
        """Synchronous statistics calculation."""
        try:
            arr = np.array(numbers)
            
            return {
                'mean': float(np.mean(arr)),
                'median': float(np.median(arr)),
                'std': float(np.std(arr)),
                'min': float(np.min(arr)),
                'max': float(np.max(arr)),
                'count': len(numbers),
                'success': True
            }
        except Exception as e:
            logger.error(f"Statistics calculation failed: {e}")
            return {
                'error': str(e),
                'success': False
            }
