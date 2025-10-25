"""Tests for action planning and orchestration."""

import pytest
import asyncio
from core.models import Intent, IntentCategory, Action, ActionType, ActionStatus
from core.action_planner import ActionPlanner, DependencyResolver
from core.action_executor import ActionExecutor, DefaultActionExecutor, ExecutionResult


class TestActionPlanner:
    """Test action planner functionality."""
    
    @pytest.mark.asyncio
    async def test_plan_question_intent(self):
        """Test planning for question intent."""
        planner = ActionPlanner()
        
        intent = Intent(
            category=IntentCategory.QUESTION,
            confidence=0.95,
            parameters={'query': 'What is the weather?'}
        )
        
        plan = await planner.plan(intent)
        
        assert len(plan.actions) > 0
        assert plan.estimated_time > 0
        assert isinstance(plan.dependencies, dict)
        
        # Should have retrieval and response generation actions
        action_types = [action.type for action in plan.actions]
        assert ActionType.GENERATE_RESPONSE in action_types
    
    @pytest.mark.asyncio
    async def test_plan_math_intent(self):
        """Test planning for math intent."""
        planner = ActionPlanner()
        
        intent = Intent(
            category=IntentCategory.MATH,
            confidence=0.98,
            parameters={'expression': '2 + 2', 'operation': 'evaluate'}
        )
        
        plan = await planner.plan(intent)
        
        assert len(plan.actions) >= 2
        
        # Should have math computation and response generation
        action_types = [action.type for action in plan.actions]
        assert ActionType.COMPUTE_MATH in action_types
        assert ActionType.GENERATE_RESPONSE in action_types
    
    @pytest.mark.asyncio
    async def test_plan_command_intent(self):
        """Test planning for command intent."""
        planner = ActionPlanner()
        
        intent = Intent(
            category=IntentCategory.COMMAND,
            confidence=0.92,
            parameters={
                'command_type': 'device',
                'device_action': 'open_app',
                'device_params': {'app': 'notepad'}
            }
        )
        
        plan = await planner.plan(intent)
        
        assert len(plan.actions) >= 2
        
        # Should have device control and response generation
        action_types = [action.type for action in plan.actions]
        assert ActionType.CONTROL_DEVICE in action_types
        assert ActionType.GENERATE_RESPONSE in action_types
    
    @pytest.mark.asyncio
    async def test_optimize_plan(self):
        """Test plan optimization."""
        planner = ActionPlanner()
        
        intent = Intent(
            category=IntentCategory.QUESTION,
            confidence=0.95,
            parameters={'query': 'Tell me about Python'}
        )
        
        plan = await planner.plan(intent)
        original_time = plan.estimated_time
        
        optimized_plan = await planner.optimize_plan(plan)
        
        # Optimized plan should have same or better estimated time
        assert optimized_plan.estimated_time <= original_time
    
    def test_dependency_graph_building(self):
        """Test dependency graph construction."""
        planner = ActionPlanner()
        
        actions = [
            Action(
                id='action1',
                type=ActionType.RETRIEVE_MEMORY,
                parameters={},
                estimated_time=0.2,
                priority=1
            ),
            Action(
                id='action2',
                type=ActionType.GENERATE_RESPONSE,
                parameters={},
                estimated_time=0.3,
                priority=2
            )
        ]
        
        dependencies = planner._build_dependency_graph(actions)
        
        assert isinstance(dependencies, dict)
        assert 'action1' in dependencies
        assert 'action2' in dependencies
        
        # Response should depend on retrieval
        assert 'action1' in dependencies['action2']


class TestDependencyResolver:
    """Test dependency resolver functionality."""
    
    def test_resolve_execution_order(self):
        """Test execution order resolution."""
        resolver = DependencyResolver()
        
        actions = [
            Action(
                id='action1',
                type=ActionType.RETRIEVE_MEMORY,
                parameters={},
                estimated_time=0.2,
                priority=1
            ),
            Action(
                id='action2',
                type=ActionType.RETRIEVE_KNOWLEDGE,
                parameters={},
                estimated_time=0.4,
                priority=1
            ),
            Action(
                id='action3',
                type=ActionType.GENERATE_RESPONSE,
                parameters={},
                estimated_time=0.3,
                priority=2
            )
        ]
        
        dependencies = {
            'action1': [],
            'action2': [],
            'action3': ['action1', 'action2']
        }
        
        stages = resolver.resolve_execution_order(actions, dependencies)
        
        assert len(stages) == 2
        assert len(stages[0]) == 2  # action1 and action2 can run in parallel
        assert len(stages[1]) == 1  # action3 runs after
        
        # Verify action3 is in second stage
        assert stages[1][0].id == 'action3'
    
    def test_circular_dependency_detection(self):
        """Test circular dependency detection."""
        resolver = DependencyResolver()
        
        actions = [
            Action(
                id='action1',
                type=ActionType.RETRIEVE_MEMORY,
                parameters={},
                estimated_time=0.2,
                priority=1
            ),
            Action(
                id='action2',
                type=ActionType.RETRIEVE_KNOWLEDGE,
                parameters={},
                estimated_time=0.4,
                priority=1
            )
        ]
        
        # Create circular dependency
        dependencies = {
            'action1': ['action2'],
            'action2': ['action1']
        }
        
        with pytest.raises(ValueError, match="Circular dependency"):
            resolver.resolve_execution_order(actions, dependencies)
    
    def test_identify_parallel_actions(self):
        """Test identification of parallel actions."""
        resolver = DependencyResolver()
        
        actions = [
            Action(
                id='action1',
                type=ActionType.RETRIEVE_MEMORY,
                parameters={},
                estimated_time=0.2,
                priority=1
            ),
            Action(
                id='action2',
                type=ActionType.RETRIEVE_KNOWLEDGE,
                parameters={},
                estimated_time=0.4,
                priority=1
            ),
            Action(
                id='action3',
                type=ActionType.CALL_API,
                parameters={},
                estimated_time=0.5,
                priority=1
            )
        ]
        
        dependencies = {
            'action1': [],
            'action2': [],
            'action3': []
        }
        
        parallel_pairs = resolver.identify_parallel_actions(actions, dependencies)
        
        # All three actions can run in parallel
        assert len(parallel_pairs) == 3
        assert ('action1', 'action2') in parallel_pairs
        assert ('action1', 'action3') in parallel_pairs
        assert ('action2', 'action3') in parallel_pairs
    
    def test_validate_dependencies(self):
        """Test dependency validation."""
        resolver = DependencyResolver()
        
        actions = [
            Action(
                id='action1',
                type=ActionType.RETRIEVE_MEMORY,
                parameters={},
                estimated_time=0.2,
                priority=1
            )
        ]
        
        # Valid dependencies
        dependencies = {'action1': []}
        is_valid, error = resolver.validate_dependencies(actions, dependencies)
        assert is_valid
        assert error is None
        
        # Invalid: unknown action ID
        dependencies = {'action1': ['unknown_action']}
        is_valid, error = resolver.validate_dependencies(actions, dependencies)
        assert not is_valid
        assert error is not None


class TestActionExecutor:
    """Test action executor functionality."""
    
    @pytest.mark.asyncio
    async def test_execute_single_action(self):
        """Test executing a single action."""
        executor = DefaultActionExecutor()
        
        action = Action(
            id='test_action',
            type=ActionType.COMPUTE_MATH,
            parameters={'expression': '2 + 2'},
            estimated_time=0.1,
            priority=1
        )
        
        result = await executor.execute(action)
        
        assert isinstance(result, ExecutionResult)
        assert result.action_id == 'test_action'
        assert result.success
        assert action.status == ActionStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_execute_with_timeout(self):
        """Test action execution with timeout."""
        executor = DefaultActionExecutor()
        
        # Create a custom handler that takes too long
        async def slow_handler(action):
            await asyncio.sleep(2.0)
            return {'result': 'done'}
        
        executor.register_handler(ActionType.COMPUTE_MATH, slow_handler)
        
        action = Action(
            id='slow_action',
            type=ActionType.COMPUTE_MATH,
            parameters={},
            estimated_time=0.1,
            priority=1
        )
        
        result = await executor.execute(action, timeout=0.5)
        
        assert not result.success
        assert 'timed out' in result.error.lower()
        assert action.status == ActionStatus.FAILED
    
    @pytest.mark.asyncio
    async def test_execute_parallel(self):
        """Test parallel action execution."""
        executor = DefaultActionExecutor()
        
        actions = [
            Action(
                id=f'action{i}',
                type=ActionType.RETRIEVE_MEMORY,
                parameters={},
                estimated_time=0.1,
                priority=1
            )
            for i in range(3)
        ]
        
        results = await executor.execute_parallel(actions)
        
        assert len(results) == 3
        assert all(r.success for r in results)
    
    @pytest.mark.asyncio
    async def test_execute_sequential(self):
        """Test sequential action execution."""
        executor = DefaultActionExecutor()
        
        actions = [
            Action(
                id=f'action{i}',
                type=ActionType.RETRIEVE_MEMORY,
                parameters={},
                estimated_time=0.1,
                priority=i
            )
            for i in range(3)
        ]
        
        results = await executor.execute_sequential(actions)
        
        assert len(results) == 3
        assert all(r.success for r in results)
    
    @pytest.mark.asyncio
    async def test_execute_plan(self):
        """Test executing a complete action plan."""
        from core.action_planner import ActionPlanner
        
        executor = DefaultActionExecutor()
        planner = ActionPlanner()
        
        intent = Intent(
            category=IntentCategory.MATH,
            confidence=0.98,
            parameters={'expression': '5 * 3'}
        )
        
        plan = await planner.plan(intent)
        results = await executor.execute_plan(plan)
        
        assert len(results) > 0
        assert all(isinstance(r, ExecutionResult) for r in results.values())
    
    def test_execution_statistics(self):
        """Test execution statistics tracking."""
        executor = DefaultActionExecutor()
        
        # Initially empty
        stats = executor.get_statistics()
        assert stats['total_executions'] == 0
        
        # Add some mock results
        executor.execution_history.append(
            ExecutionResult('action1', True, execution_time=0.5)
        )
        executor.execution_history.append(
            ExecutionResult('action2', False, error='Failed', execution_time=0.3)
        )
        
        stats = executor.get_statistics()
        assert stats['total_executions'] == 2
        assert stats['successful'] == 1
        assert stats['failed'] == 1
        assert stats['success_rate'] == 50.0
