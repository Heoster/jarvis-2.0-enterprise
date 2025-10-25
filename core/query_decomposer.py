"""Multi-Stage Query Decomposition using ReAct/PAL chains."""

from typing import List, Dict, Any, Optional, Tuple
import re
import asyncio

from core.logger import get_logger

logger = get_logger(__name__)


class QueryDecomposer:
    """
    Decomposes compound queries into sequential sub-intents using ReAct/PAL patterns.
    """
    
    def __init__(self):
        self.decomposition_patterns = self._initialize_patterns()
        self.langchain_chain = self._initialize_langchain()
    
    def _initialize_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize decomposition patterns."""
        return {
            'sequential': re.compile(r'\b(then|after|next|and then)\b', re.IGNORECASE),
            'conditional': re.compile(r'\b(if|when|unless|provided)\b', re.IGNORECASE),
            'parallel': re.compile(r'\b(and|also|plus|as well as)\b', re.IGNORECASE),
            'comparison': re.compile(r'\b(compare|versus|vs|difference between)\b', re.IGNORECASE),
        }
    
    def _initialize_langchain(self):
        """Initialize LangChain ReAct chain."""
        try:
            from langchain.chains import LLMChain
            from langchain.prompts import PromptTemplate
            # Would initialize ReAct chain here
            return None
        except:
            return None
    
    async def decompose(self, query: str) -> List[Dict[str, Any]]:
        """
        Decompose compound query into sub-tasks.
        
        Args:
            query: Complex user query
            
        Returns:
            List of sub-tasks with dependencies
        """
        # Check if query needs decomposition
        if not self._needs_decomposition(query):
            return [{'task': query, 'type': 'simple', 'dependencies': []}]
        
        # Detect decomposition type
        decomp_type = self._detect_decomposition_type(query)
        
        # Decompose based on type
        if decomp_type == 'sequential':
            return self._decompose_sequential(query)
        elif decomp_type == 'conditional':
            return self._decompose_conditional(query)
        elif decomp_type == 'parallel':
            return self._decompose_parallel(query)
        elif decomp_type == 'comparison':
            return self._decompose_comparison(query)
        else:
            return self._decompose_generic(query)
    
    def _needs_decomposition(self, query: str) -> bool:
        """Check if query needs decomposition."""
        # Check for multiple sentences
        if query.count('.') > 1 or query.count('?') > 1:
            return True
        
        # Check for coordination
        if any(pattern.search(query) for pattern in self.decomposition_patterns.values()):
            return True
        
        # Check for multiple verbs (simple heuristic)
        action_words = ['create', 'write', 'explain', 'show', 'calculate', 'find', 'search']
        action_count = sum(1 for word in action_words if word in query.lower())
        return action_count > 1
    
    def _detect_decomposition_type(self, query: str) -> str:
        """Detect type of decomposition needed."""
        for decomp_type, pattern in self.decomposition_patterns.items():
            if pattern.search(query):
                return decomp_type
        return 'generic'
    
    def _decompose_sequential(self, query: str) -> List[Dict[str, Any]]:
        """Decompose sequential tasks."""
        # Split on sequential markers
        parts = re.split(r'\b(then|after|next|and then)\b', query, flags=re.IGNORECASE)
        
        tasks = []
        current_task = ""
        
        for i, part in enumerate(parts):
            part = part.strip()
            if part.lower() in ['then', 'after', 'next', 'and then']:
                if current_task:
                    tasks.append(current_task)
                current_task = ""
            else:
                current_task += " " + part if current_task else part
        
        if current_task:
            tasks.append(current_task)
        
        # Create task objects with dependencies
        result = []
        for i, task in enumerate(tasks):
            result.append({
                'task': task.strip(),
                'type': 'sequential',
                'order': i,
                'dependencies': [i-1] if i > 0 else []
            })
        
        return result
    
    def _decompose_conditional(self, query: str) -> List[Dict[str, Any]]:
        """Decompose conditional tasks."""
        # Split on conditional markers
        parts = re.split(r'\b(if|when|unless|provided)\b', query, flags=re.IGNORECASE)
        
        if len(parts) >= 3:
            condition = parts[0].strip()
            action = parts[2].strip()
            
            return [
                {
                    'task': condition,
                    'type': 'condition',
                    'order': 0,
                    'dependencies': []
                },
                {
                    'task': action,
                    'type': 'conditional_action',
                    'order': 1,
                    'dependencies': [0],
                    'condition': condition
                }
            ]
        
        return [{'task': query, 'type': 'simple', 'dependencies': []}]
    
    def _decompose_parallel(self, query: str) -> List[Dict[str, Any]]:
        """Decompose parallel tasks."""
        # Split on parallel markers
        parts = re.split(r'\b(and|also|plus|as well as)\b', query, flags=re.IGNORECASE)
        
        tasks = []
        for part in parts:
            part = part.strip()
            if part.lower() not in ['and', 'also', 'plus', 'as well as'] and part:
                tasks.append(part)
        
        return [
            {
                'task': task,
                'type': 'parallel',
                'order': i,
                'dependencies': []  # No dependencies for parallel tasks
            }
            for i, task in enumerate(tasks)
        ]
    
    def _decompose_comparison(self, query: str) -> List[Dict[str, Any]]:
        """Decompose comparison queries."""
        # Extract items to compare
        match = re.search(
            r'compare\s+(.+?)\s+(?:and|vs|versus)\s+(.+?)(?:\?|$)',
            query,
            re.IGNORECASE
        )
        
        if match:
            item1 = match.group(1).strip()
            item2 = match.group(2).strip()
            
            return [
                {
                    'task': f"Explain {item1}",
                    'type': 'comparison_part',
                    'order': 0,
                    'dependencies': [],
                    'comparison_item': item1
                },
                {
                    'task': f"Explain {item2}",
                    'type': 'comparison_part',
                    'order': 1,
                    'dependencies': [],
                    'comparison_item': item2
                },
                {
                    'task': f"Compare {item1} and {item2}",
                    'type': 'comparison_synthesis',
                    'order': 2,
                    'dependencies': [0, 1]
                }
            ]
        
        return [{'task': query, 'type': 'simple', 'dependencies': []}]
    
    def _decompose_generic(self, query: str) -> List[Dict[str, Any]]:
        """Generic decomposition by sentences."""
        sentences = re.split(r'[.!?]+', query)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 1:
            return [{'task': query, 'type': 'simple', 'dependencies': []}]
        
        return [
            {
                'task': sentence,
                'type': 'sequential',
                'order': i,
                'dependencies': [i-1] if i > 0 else []
            }
            for i, sentence in enumerate(sentences)
        ]
    
    def create_execution_plan(self, sub_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create execution plan from sub-tasks."""
        return {
            'total_tasks': len(sub_tasks),
            'tasks': sub_tasks,
            'execution_order': self._determine_execution_order(sub_tasks),
            'estimated_steps': len(sub_tasks)
        }
    
    def _determine_execution_order(self, tasks: List[Dict[str, Any]]) -> List[int]:
        """Determine optimal execution order."""
        # Simple topological sort based on dependencies
        order = []
        completed = set()
        
        while len(order) < len(tasks):
            for i, task in enumerate(tasks):
                if i in completed:
                    continue
                
                deps = task.get('dependencies', [])
                if all(d in completed for d in deps):
                    order.append(i)
                    completed.add(i)
        
        return order
