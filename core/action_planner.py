"""Action planning and orchestration for the On-Device Assistant."""

import asyncio
import uuid
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime
import networkx as nx

from core.models import (
    Intent, IntentCategory, Action, ActionPlan, ActionType, ActionStatus
)
from core.logger import get_logger

logger = get_logger(__name__)


class ActionPlanner:
    """
    Plans and optimizes action sequences based on user intent.
    
    Responsibilities:
    - Decompose complex requests into atomic actions
    - Build dependency graphs
    - Optimize execution order
    - Generate fallback plans
    """
    
    def __init__(self):
        """Initialize the action planner."""
        self.action_templates = self._initialize_action_templates()
        self.resource_estimates = self._initialize_resource_estimates()
    
    def _initialize_action_templates(self) -> Dict[IntentCategory, List[ActionType]]:
        """
        Initialize action templates for each intent category.
        
        Returns:
            Mapping of intent categories to typical action sequences
        """
        return {
            IntentCategory.QUESTION: [
                ActionType.RETRIEVE_MEMORY,
                ActionType.RETRIEVE_KNOWLEDGE,
                ActionType.GENERATE_RESPONSE,
            ],
            IntentCategory.COMMAND: [
                ActionType.CONTROL_DEVICE,
                ActionType.GENERATE_RESPONSE,
            ],
            IntentCategory.MATH: [
                ActionType.COMPUTE_MATH,
                ActionType.GENERATE_RESPONSE,
            ],
            IntentCategory.CODE: [
                ActionType.EXECUTE_CODE,
                ActionType.GENERATE_RESPONSE,
            ],
            IntentCategory.FETCH: [
                ActionType.CALL_API,
                ActionType.GENERATE_RESPONSE,
            ],
            IntentCategory.CONVERSATIONAL: [
                ActionType.RETRIEVE_MEMORY,
                ActionType.GENERATE_RESPONSE,
            ],
        }
    
    def _initialize_resource_estimates(self) -> Dict[ActionType, float]:
        """
        Initialize estimated execution times for each action type.
        
        Returns:
            Mapping of action types to estimated execution time in seconds
        """
        return {
            ActionType.RETRIEVE_MEMORY: 0.2,
            ActionType.RETRIEVE_KNOWLEDGE: 0.4,
            ActionType.CALL_API: 0.5,
            ActionType.SCRAPE_WEB: 1.0,
            ActionType.COMPUTE_MATH: 0.15,
            ActionType.EXECUTE_CODE: 0.3,
            ActionType.CONTROL_DEVICE: 0.4,
            ActionType.CONTROL_BROWSER: 0.5,
            ActionType.GENERATE_RESPONSE: 0.3,
            ActionType.SPEAK: 0.5,
        }
    
    async def plan(self, intent: Intent, context: Optional[Dict] = None) -> ActionPlan:
        """
        Create an action plan based on the user intent.
        
        Args:
            intent: Classified user intent
            context: Optional context information
            
        Returns:
            Complete action plan with dependencies
        """
        logger.info(f"Planning actions for intent: {intent.category.value}")
        
        # Decompose intent into actions
        actions = await self._decompose_intent(intent, context or {})
        
        # Build dependency graph
        dependencies = self._build_dependency_graph(actions)
        
        # Prioritize and order actions
        actions = self._prioritize_actions(actions, dependencies)
        
        # Estimate total execution time
        estimated_time = self._estimate_execution_time(actions, dependencies)
        
        # Generate fallback actions
        fallbacks = self._generate_fallbacks(actions)
        
        plan = ActionPlan(
            actions=actions,
            dependencies=dependencies,
            estimated_time=estimated_time,
            fallbacks=fallbacks
        )
        
        logger.info(f"Created plan with {len(actions)} actions, estimated time: {estimated_time:.2f}s")
        
        return plan
    
    async def _decompose_intent(
        self, 
        intent: Intent, 
        context: Dict
    ) -> List[Action]:
        """
        Decompose intent into atomic actions.
        
        Args:
            intent: User intent
            context: Context information
            
        Returns:
            List of atomic actions
        """
        actions = []
        
        # Get base action template for this intent category
        action_types = self.action_templates.get(
            intent.category, 
            [ActionType.GENERATE_RESPONSE]
        )
        
        # Handle complex intents with multiple sub-tasks
        if intent.category == IntentCategory.QUESTION:
            actions.extend(self._plan_question_actions(intent, context))
        
        elif intent.category == IntentCategory.COMMAND:
            actions.extend(self._plan_command_actions(intent, context))
        
        elif intent.category == IntentCategory.MATH:
            actions.extend(self._plan_math_actions(intent, context))
        
        elif intent.category == IntentCategory.CODE:
            actions.extend(self._plan_code_actions(intent, context))
        
        elif intent.category == IntentCategory.FETCH:
            actions.extend(self._plan_fetch_actions(intent, context))
        
        elif intent.category == IntentCategory.CONVERSATIONAL:
            actions.extend(self._plan_conversational_actions(intent, context))
        
        else:
            # Default: just generate a response
            actions.append(self._create_action(
                ActionType.GENERATE_RESPONSE,
                {'intent': intent.to_dict()},
                priority=1
            ))
        
        return actions
    
    def _plan_question_actions(self, intent: Intent, context: Dict) -> List[Action]:
        """Plan actions for question intents."""
        actions = []
        
        # Check if we need to retrieve from memory
        if context.get('needs_memory', True):
            actions.append(self._create_action(
                ActionType.RETRIEVE_MEMORY,
                {'query': intent.parameters.get('query', ''), 'top_k': 5},
                priority=1
            ))
        
        # Check if we need to retrieve from knowledge base
        if context.get('needs_knowledge', True):
            actions.append(self._create_action(
                ActionType.RETRIEVE_KNOWLEDGE,
                {'query': intent.parameters.get('query', ''), 'top_k': 10},
                priority=1
            ))
        
        # Check if we need to call external APIs
        if intent.parameters.get('requires_api'):
            api_name = intent.parameters.get('api_name', 'generic')
            actions.append(self._create_action(
                ActionType.CALL_API,
                {
                    'api': api_name,
                    'params': intent.parameters.get('api_params', {})
                },
                priority=2
            ))
        
        # Generate response based on retrieved information
        actions.append(self._create_action(
            ActionType.GENERATE_RESPONSE,
            {'intent': intent.to_dict(), 'context': context},
            priority=3
        ))
        
        return actions
    
    def _plan_command_actions(self, intent: Intent, context: Dict) -> List[Action]:
        """Plan actions for command intents."""
        actions = []
        
        command_type = intent.parameters.get('command_type', 'device')
        
        if command_type == 'browser':
            actions.append(self._create_action(
                ActionType.CONTROL_BROWSER,
                {
                    'action': intent.parameters.get('browser_action', 'navigate'),
                    'params': intent.parameters.get('browser_params', {})
                },
                priority=1
            ))
        else:
            actions.append(self._create_action(
                ActionType.CONTROL_DEVICE,
                {
                    'action': intent.parameters.get('device_action', 'execute'),
                    'params': intent.parameters.get('device_params', {})
                },
                priority=1
            ))
        
        # Generate confirmation response
        actions.append(self._create_action(
            ActionType.GENERATE_RESPONSE,
            {'intent': intent.to_dict(), 'context': context},
            priority=2
        ))
        
        return actions
    
    def _plan_math_actions(self, intent: Intent, context: Dict) -> List[Action]:
        """Plan actions for math intents."""
        actions = []
        
        actions.append(self._create_action(
            ActionType.COMPUTE_MATH,
            {
                'expression': intent.parameters.get('expression', ''),
                'operation': intent.parameters.get('operation', 'evaluate')
            },
            priority=1
        ))
        
        actions.append(self._create_action(
            ActionType.GENERATE_RESPONSE,
            {'intent': intent.to_dict(), 'context': context},
            priority=2
        ))
        
        return actions
    
    def _plan_code_actions(self, intent: Intent, context: Dict) -> List[Action]:
        """Plan actions for code intents."""
        actions = []
        
        actions.append(self._create_action(
            ActionType.EXECUTE_CODE,
            {
                'code': intent.parameters.get('code', ''),
                'language': intent.parameters.get('language', 'python'),
                'mode': intent.parameters.get('mode', 'execute')  # execute, analyze, debug
            },
            priority=1
        ))
        
        actions.append(self._create_action(
            ActionType.GENERATE_RESPONSE,
            {'intent': intent.to_dict(), 'context': context},
            priority=2
        ))
        
        return actions
    
    def _plan_fetch_actions(self, intent: Intent, context: Dict) -> List[Action]:
        """Plan actions for fetch intents."""
        actions = []
        
        fetch_type = intent.parameters.get('fetch_type', 'api')
        api_name = intent.parameters.get('api_name', 'generic')
        
        # Detect weather queries
        query_text = intent.parameters.get('query', '').lower()
        if 'weather' in query_text or api_name == 'weather':
            # Extract city from query if present
            city = intent.parameters.get('city')
            if not city and 'in ' in query_text:
                # Try to extract city from "weather in [city]"
                parts = query_text.split('in ')
                if len(parts) > 1:
                    city = parts[1].strip().split()[0].title()
            
            actions.append(self._create_action(
                ActionType.CALL_API,
                {
                    'api': 'weather',
                    'params': {'city': city}  # None defaults to Muzaffarnagar
                },
                priority=1
            ))
        
        # Detect news queries
        elif 'news' in query_text or api_name == 'news':
            # Extract category or search query
            category = intent.parameters.get('category')
            search_query = intent.parameters.get('search_query')
            
            # Try to detect category from query
            if not category:
                for cat in ['business', 'entertainment', 'sports', 'technology', 'health', 'science']:
                    if cat in query_text:
                        category = cat
                        break
            
            actions.append(self._create_action(
                ActionType.CALL_API,
                {
                    'api': 'news',
                    'params': {
                        'category': category,
                        'query': search_query
                    }
                },
                priority=1
            ))
        
        # Web scraping
        elif fetch_type == 'web':
            actions.append(self._create_action(
                ActionType.SCRAPE_WEB,
                {
                    'url': intent.parameters.get('url', ''),
                    'selectors': intent.parameters.get('selectors', [])
                },
                priority=1
            ))
        
        # Generic API call
        else:
            actions.append(self._create_action(
                ActionType.CALL_API,
                {
                    'api': api_name,
                    'params': intent.parameters.get('api_params', {})
                },
                priority=1
            ))
        
        actions.append(self._create_action(
            ActionType.GENERATE_RESPONSE,
            {'intent': intent.to_dict(), 'context': context},
            priority=2
        ))
        
        return actions
    
    def _plan_conversational_actions(self, intent: Intent, context: Dict) -> List[Action]:
        """Plan actions for conversational intents."""
        actions = []
        
        # Retrieve recent conversation history
        actions.append(self._create_action(
            ActionType.RETRIEVE_MEMORY,
            {'query': intent.parameters.get('query', ''), 'top_k': 3},
            priority=1
        ))
        
        actions.append(self._create_action(
            ActionType.GENERATE_RESPONSE,
            {'intent': intent.to_dict(), 'context': context},
            priority=2
        ))
        
        return actions
    
    def _create_action(
        self, 
        action_type: ActionType, 
        parameters: Dict, 
        priority: int = 1
    ) -> Action:
        """
        Create an action with estimated resources.
        
        Args:
            action_type: Type of action
            parameters: Action parameters
            priority: Execution priority (lower = higher priority)
            
        Returns:
            Action object
        """
        action_id = str(uuid.uuid4())
        estimated_time = self.resource_estimates.get(action_type, 0.5)
        
        return Action(
            id=action_id,
            type=action_type,
            parameters=parameters,
            estimated_time=estimated_time,
            priority=priority,
            status=ActionStatus.PENDING
        )
    
    def _build_dependency_graph(self, actions: List[Action]) -> Dict[str, List[str]]:
        """
        Build dependency graph for actions.
        
        Args:
            actions: List of actions
            
        Returns:
            Dictionary mapping action IDs to their dependency IDs
        """
        dependencies = {}
        
        # Group actions by priority
        priority_groups = {}
        for action in actions:
            if action.priority not in priority_groups:
                priority_groups[action.priority] = []
            priority_groups[action.priority].append(action)
        
        # Build dependencies based on priority and action types
        sorted_priorities = sorted(priority_groups.keys())
        
        for i, priority in enumerate(sorted_priorities):
            current_actions = priority_groups[priority]
            
            for action in current_actions:
                action_deps = []
                
                # Actions depend on all actions from previous priority levels
                if i > 0:
                    prev_priority = sorted_priorities[i - 1]
                    prev_actions = priority_groups[prev_priority]
                    action_deps.extend([a.id for a in prev_actions])
                
                # Special dependencies based on action types
                if action.type == ActionType.GENERATE_RESPONSE:
                    # Response generation depends on all retrieval and computation actions
                    for other_action in actions:
                        if other_action.id != action.id and other_action.type in [
                            ActionType.RETRIEVE_MEMORY,
                            ActionType.RETRIEVE_KNOWLEDGE,
                            ActionType.CALL_API,
                            ActionType.SCRAPE_WEB,
                            ActionType.COMPUTE_MATH,
                            ActionType.EXECUTE_CODE,
                            ActionType.CONTROL_DEVICE,
                            ActionType.CONTROL_BROWSER,
                        ]:
                            if other_action.id not in action_deps:
                                action_deps.append(other_action.id)
                
                dependencies[action.id] = action_deps
        
        return dependencies
    
    def _prioritize_actions(
        self, 
        actions: List[Action], 
        dependencies: Dict[str, List[str]]
    ) -> List[Action]:
        """
        Prioritize and order actions based on dependencies.
        
        Args:
            actions: List of actions
            dependencies: Dependency graph
            
        Returns:
            Ordered list of actions
        """
        # Actions are already prioritized by their priority field
        # Sort by priority (lower number = higher priority)
        return sorted(actions, key=lambda a: (a.priority, a.id))
    
    def _estimate_execution_time(
        self, 
        actions: List[Action], 
        dependencies: Dict[str, List[str]]
    ) -> float:
        """
        Estimate total execution time considering parallelization.
        
        Args:
            actions: List of actions
            dependencies: Dependency graph
            
        Returns:
            Estimated execution time in seconds
        """
        # Build networkx graph for critical path analysis
        G = nx.DiGraph()
        
        # Add nodes with execution time as weight
        for action in actions:
            G.add_node(action.id, time=action.estimated_time)
        
        # Add edges for dependencies
        for action_id, deps in dependencies.items():
            for dep_id in deps:
                G.add_edge(dep_id, action_id)
        
        # Calculate critical path (longest path considering parallel execution)
        try:
            # Find all paths and calculate the longest one
            if len(G.nodes) == 0:
                return 0.0
            
            # Simple estimation: sum of all unique priority levels
            priority_times = {}
            for action in actions:
                if action.priority not in priority_times:
                    priority_times[action.priority] = 0.0
                # Take max time for actions at same priority (they run in parallel)
                priority_times[action.priority] = max(
                    priority_times[action.priority],
                    action.estimated_time
                )
            
            return sum(priority_times.values())
        
        except Exception as e:
            logger.warning(f"Error estimating execution time: {e}")
            # Fallback: sum all action times
            return sum(action.estimated_time for action in actions)
    
    def _generate_fallbacks(self, actions: List[Action]) -> Dict[str, Action]:
        """
        Generate fallback actions for critical actions.
        
        Args:
            actions: List of actions
            
        Returns:
            Dictionary mapping action IDs to fallback actions
        """
        fallbacks = {}
        
        for action in actions:
            # Generate fallbacks for external dependencies
            if action.type == ActionType.CALL_API:
                # Fallback: use cached data or skip
                fallback = self._create_action(
                    ActionType.RETRIEVE_KNOWLEDGE,
                    {'query': action.parameters.get('params', {}).get('query', ''), 'top_k': 5},
                    priority=action.priority
                )
                fallbacks[action.id] = fallback
            
            elif action.type == ActionType.SCRAPE_WEB:
                # Fallback: use cached version or skip
                fallback = self._create_action(
                    ActionType.RETRIEVE_KNOWLEDGE,
                    {'query': action.parameters.get('url', ''), 'top_k': 5},
                    priority=action.priority
                )
                fallbacks[action.id] = fallback
            
            elif action.type in [ActionType.CONTROL_DEVICE, ActionType.CONTROL_BROWSER]:
                # Fallback: inform user of failure
                fallback = self._create_action(
                    ActionType.GENERATE_RESPONSE,
                    {
                        'text': f"I couldn't complete the {action.type.value} action. Please try again.",
                        'error': True
                    },
                    priority=action.priority
                )
                fallbacks[action.id] = fallback
        
        return fallbacks
    
    async def optimize_plan(self, plan: ActionPlan) -> ActionPlan:
        """
        Optimize an existing action plan.
        
        Args:
            plan: Action plan to optimize
            
        Returns:
            Optimized action plan
        """
        logger.info("Optimizing action plan")
        
        # Identify independent actions that can run in parallel
        independent_groups = self._identify_independent_actions(
            plan.actions, 
            plan.dependencies
        )
        
        # Adjust priorities to enable parallelization
        for group in independent_groups:
            # Actions in the same group can have the same priority
            min_priority = min(action.priority for action in group)
            for action in group:
                action.priority = min_priority
        
        # Recalculate estimated time with optimized parallelization
        plan.estimated_time = self._estimate_execution_time(
            plan.actions, 
            plan.dependencies
        )
        
        logger.info(f"Optimized plan, new estimated time: {plan.estimated_time:.2f}s")
        
        return plan
    
    def _identify_independent_actions(
        self, 
        actions: List[Action], 
        dependencies: Dict[str, List[str]]
    ) -> List[List[Action]]:
        """
        Identify groups of independent actions that can run in parallel.
        
        Args:
            actions: List of actions
            dependencies: Dependency graph
            
        Returns:
            List of action groups that can run in parallel
        """
        # Build networkx graph
        G = nx.DiGraph()
        
        for action in actions:
            G.add_node(action.id)
        
        for action_id, deps in dependencies.items():
            for dep_id in deps:
                G.add_edge(dep_id, action_id)
        
        # Find actions at the same depth level (can potentially run in parallel)
        independent_groups = []
        
        # Group by priority level
        priority_groups = {}
        for action in actions:
            if action.priority not in priority_groups:
                priority_groups[action.priority] = []
            priority_groups[action.priority].append(action)
        
        # Each priority group can potentially run in parallel
        for priority, group in priority_groups.items():
            if len(group) > 1:
                # Check if actions in this group are truly independent
                independent = []
                for action in group:
                    # Check if this action depends on any other in the group
                    deps = dependencies.get(action.id, [])
                    group_ids = [a.id for a in group]
                    if not any(dep_id in group_ids for dep_id in deps):
                        independent.append(action)
                
                if len(independent) > 1:
                    independent_groups.append(independent)
        
        return independent_groups


class DependencyResolver:
    """
    Resolves action dependencies and determines optimal execution order.
    
    Responsibilities:
    - Determine execution order based on dependencies
    - Identify independent actions for parallel execution
    - Detect circular dependencies
    - Generate execution stages
    """
    
    def __init__(self):
        """Initialize the dependency resolver."""
        pass
    
    def resolve_execution_order(
        self, 
        actions: List[Action], 
        dependencies: Dict[str, List[str]]
    ) -> List[List[Action]]:
        """
        Resolve execution order and group actions into stages.
        
        Actions in the same stage can be executed in parallel.
        
        Args:
            actions: List of actions
            dependencies: Dependency graph (action_id -> [dependency_ids])
            
        Returns:
            List of stages, where each stage is a list of actions that can run in parallel
        """
        logger.info("Resolving execution order")
        
        # Build dependency graph
        G = self._build_graph(actions, dependencies)
        
        # Check for circular dependencies
        if not nx.is_directed_acyclic_graph(G):
            logger.error("Circular dependency detected in action plan")
            raise ValueError("Circular dependency detected in action plan")
        
        # Perform topological sort to get execution order
        try:
            topo_order = list(nx.topological_sort(G))
        except nx.NetworkXError as e:
            logger.error(f"Error in topological sort: {e}")
            raise ValueError(f"Invalid dependency graph: {e}")
        
        # Group actions into stages based on dependencies
        stages = self._group_into_stages(actions, dependencies, topo_order)
        
        logger.info(f"Resolved execution order into {len(stages)} stages")
        
        return stages
    
    def _build_graph(
        self, 
        actions: List[Action], 
        dependencies: Dict[str, List[str]]
    ) -> nx.DiGraph:
        """
        Build a directed graph from actions and dependencies.
        
        Args:
            actions: List of actions
            dependencies: Dependency graph
            
        Returns:
            NetworkX directed graph
        """
        G = nx.DiGraph()
        
        # Add nodes
        for action in actions:
            G.add_node(action.id, action=action)
        
        # Add edges
        for action_id, deps in dependencies.items():
            for dep_id in deps:
                if dep_id in G.nodes:
                    G.add_edge(dep_id, action_id)
        
        return G
    
    def _group_into_stages(
        self, 
        actions: List[Action], 
        dependencies: Dict[str, List[str]],
        topo_order: List[str]
    ) -> List[List[Action]]:
        """
        Group actions into execution stages.
        
        Args:
            actions: List of actions
            dependencies: Dependency graph
            topo_order: Topologically sorted action IDs
            
        Returns:
            List of stages
        """
        # Create action lookup
        action_map = {action.id: action for action in actions}
        
        # Track which stage each action belongs to
        action_stages = {}
        
        # Assign each action to the earliest possible stage
        for action_id in topo_order:
            # Find the maximum stage of all dependencies
            deps = dependencies.get(action_id, [])
            if not deps:
                # No dependencies, can go in stage 0
                action_stages[action_id] = 0
            else:
                # Must go after all dependencies
                max_dep_stage = max(
                    action_stages.get(dep_id, 0) for dep_id in deps
                )
                action_stages[action_id] = max_dep_stage + 1
        
        # Group actions by stage
        stages_dict = {}
        for action_id, stage in action_stages.items():
            if stage not in stages_dict:
                stages_dict[stage] = []
            stages_dict[stage].append(action_map[action_id])
        
        # Convert to list of stages
        max_stage = max(stages_dict.keys()) if stages_dict else 0
        stages = []
        for i in range(max_stage + 1):
            stages.append(stages_dict.get(i, []))
        
        return stages
    
    def identify_parallel_actions(
        self, 
        actions: List[Action], 
        dependencies: Dict[str, List[str]]
    ) -> Set[Tuple[str, str]]:
        """
        Identify pairs of actions that can be executed in parallel.
        
        Args:
            actions: List of actions
            dependencies: Dependency graph
            
        Returns:
            Set of action ID pairs that can run in parallel
        """
        parallel_pairs = set()
        
        # Build graph
        G = self._build_graph(actions, dependencies)
        
        # Two actions can run in parallel if neither depends on the other
        action_ids = [action.id for action in actions]
        
        for i, action_id1 in enumerate(action_ids):
            for action_id2 in action_ids[i+1:]:
                # Check if there's a path from action1 to action2 or vice versa
                has_path_1_to_2 = nx.has_path(G, action_id1, action_id2)
                has_path_2_to_1 = nx.has_path(G, action_id2, action_id1)
                
                if not has_path_1_to_2 and not has_path_2_to_1:
                    # No dependency between them, can run in parallel
                    parallel_pairs.add((action_id1, action_id2))
        
        logger.info(f"Identified {len(parallel_pairs)} pairs of parallel actions")
        
        return parallel_pairs
    
    def estimate_parallel_speedup(
        self, 
        actions: List[Action], 
        dependencies: Dict[str, List[str]]
    ) -> float:
        """
        Estimate speedup from parallel execution.
        
        Args:
            actions: List of actions
            dependencies: Dependency graph
            
        Returns:
            Speedup factor (sequential_time / parallel_time)
        """
        # Sequential time: sum of all action times
        sequential_time = sum(action.estimated_time for action in actions)
        
        # Parallel time: sum of stage times (max time per stage)
        stages = self.resolve_execution_order(actions, dependencies)
        parallel_time = sum(
            max(action.estimated_time for action in stage) if stage else 0.0
            for stage in stages
        )
        
        if parallel_time == 0:
            return 1.0
        
        speedup = sequential_time / parallel_time
        
        logger.info(f"Estimated speedup: {speedup:.2f}x (sequential: {sequential_time:.2f}s, parallel: {parallel_time:.2f}s)")
        
        return speedup
    
    def validate_dependencies(
        self, 
        actions: List[Action], 
        dependencies: Dict[str, List[str]]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that dependencies are well-formed.
        
        Args:
            actions: List of actions
            dependencies: Dependency graph
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        action_ids = {action.id for action in actions}
        
        # Check that all dependency IDs exist
        for action_id, deps in dependencies.items():
            if action_id not in action_ids:
                return False, f"Unknown action ID in dependencies: {action_id}"
            
            for dep_id in deps:
                if dep_id not in action_ids:
                    return False, f"Unknown dependency ID: {dep_id} for action {action_id}"
        
        # Check for circular dependencies
        G = self._build_graph(actions, dependencies)
        if not nx.is_directed_acyclic_graph(G):
            try:
                cycle = nx.find_cycle(G)
                cycle_str = " -> ".join([str(edge[0]) for edge in cycle])
                return False, f"Circular dependency detected: {cycle_str}"
            except nx.NetworkXNoCycle:
                pass
        
        return True, None
