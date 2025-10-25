"""Code execution and analysis engine."""

import ast
import sys
from io import StringIO
from typing import Dict, Any, Optional
import asyncio
import pylint.lint
from pylint.reporters.text import TextReporter
import black

from core.logger import get_logger

logger = get_logger(__name__)


class CodeEngine:
    """Engine for code execution and analysis."""
    
    def __init__(
        self,
        timeout: int = 10,
        max_memory_mb: int = 100
    ):
        """
        Initialize code engine.
        
        Args:
            timeout: Execution timeout in seconds
            max_memory_mb: Maximum memory usage in MB
        """
        self.timeout = timeout
        self.max_memory_mb = max_memory_mb
        
        # Restricted builtins for sandboxing
        self.safe_builtins = {
            'abs': abs,
            'all': all,
            'any': any,
            'bool': bool,
            'dict': dict,
            'enumerate': enumerate,
            'filter': filter,
            'float': float,
            'int': int,
            'len': len,
            'list': list,
            'map': map,
            'max': max,
            'min': min,
            'print': print,
            'range': range,
            'reversed': reversed,
            'round': round,
            'set': set,
            'sorted': sorted,
            'str': str,
            'sum': sum,
            'tuple': tuple,
            'zip': zip,
        }
    
    async def execute_python(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code in sandboxed environment.
        
        Args:
            code: Python code to execute
            
        Returns:
            Execution result dictionary
        """
        return await asyncio.to_thread(self._execute_python_sync, code)
    
    def _execute_python_sync(self, code: str) -> Dict[str, Any]:
        """Synchronous Python execution."""
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        result = {
            'success': False,
            'output': '',
            'error': None,
            'return_value': None
        }
        
        try:
            # Parse code to check for dangerous operations
            tree = ast.parse(code)
            if not self._is_safe_code(tree):
                result['error'] = "Code contains restricted operations"
                return result
            
            # Create restricted globals
            restricted_globals = {
                '__builtins__': self.safe_builtins,
            }
            
            # Execute code
            exec(code, restricted_globals)
            
            result['success'] = True
            result['output'] = captured_output.getvalue()
            
        except SyntaxError as e:
            result['error'] = f"Syntax error: {e}"
        except Exception as e:
            result['error'] = f"Runtime error: {e}"
        finally:
            sys.stdout = old_stdout
        
        return result
    
    def _is_safe_code(self, tree: ast.AST) -> bool:
        """Check if code is safe to execute."""
        # List of dangerous operations
        dangerous_nodes = (
            ast.Import,
            ast.ImportFrom,
            ast.Open,  # File operations
        )
        
        for node in ast.walk(tree):
            if isinstance(node, dangerous_nodes):
                return False
            
            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'compile', '__import__', 'open']:
                        return False
        
        return True
    
    async def analyze_code(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """
        Analyze code for errors and issues.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Analysis results
        """
        if language.lower() == 'python':
            return await asyncio.to_thread(self._analyze_python_sync, code)
        else:
            return {
                'success': False,
                'error': f"Analysis not supported for {language}"
            }
    
    def _analyze_python_sync(self, code: str) -> Dict[str, Any]:
        """Synchronous Python code analysis."""
        issues = []
        
        # Syntax check
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append({
                'type': 'syntax_error',
                'line': e.lineno,
                'message': str(e)
            })
            return {
                'success': False,
                'issues': issues
            }
        
        # Pylint analysis (simplified)
        try:
            pylint_output = StringIO()
            reporter = TextReporter(pylint_output)
            
            # Write code to temp file for pylint
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run pylint
            pylint.lint.Run([temp_file, '--disable=all', '--enable=E,F'], reporter=reporter, exit=False)
            
            # Parse output
            output = pylint_output.getvalue()
            if output:
                issues.append({
                    'type': 'lint',
                    'message': output
                })
            
            # Clean up
            import os
            os.unlink(temp_file)
            
        except Exception as e:
            logger.warning(f"Pylint analysis failed: {e}")
        
        return {
            'success': len(issues) == 0,
            'issues': issues
        }
    
    async def format_code(self, code: str, language: str = 'python') -> Dict[str, Any]:
        """
        Format code using language-specific formatter.
        
        Args:
            code: Code to format
            language: Programming language
            
        Returns:
            Formatted code
        """
        if language.lower() == 'python':
            return await asyncio.to_thread(self._format_python_sync, code)
        else:
            return {
                'success': False,
                'formatted_code': code,
                'error': f"Formatting not supported for {language}"
            }
    
    def _format_python_sync(self, code: str) -> Dict[str, Any]:
        """Synchronous Python code formatting."""
        try:
            formatted = black.format_str(code, mode=black.FileMode())
            return {
                'success': True,
                'formatted_code': formatted
            }
        except Exception as e:
            logger.error(f"Code formatting failed: {e}")
            return {
                'success': False,
                'formatted_code': code,
                'error': str(e)
            }
    
    async def explain_code(self, code: str) -> Dict[str, Any]:
        """
        Generate explanation for code (placeholder for LLM integration).
        
        Args:
            code: Code to explain
            
        Returns:
            Explanation
        """
        # This would integrate with LLM for actual explanation
        return {
            'success': True,
            'explanation': "Code explanation would be generated by LLM",
            'code': code
        }
    
    async def debug_code(self, code: str, error: str) -> Dict[str, Any]:
        """
        Suggest fixes for code errors (placeholder for LLM integration).
        
        Args:
            code: Code with error
            error: Error message
            
        Returns:
            Debug suggestions
        """
        # This would integrate with LLM for actual debugging
        return {
            'success': True,
            'suggestions': ["Debug suggestions would be generated by LLM"],
            'code': code,
            'error': error
        }
