"""
Demo script for action planning and orchestration.

This demonstrates how to use the ActionPlanner, DependencyResolver,
and ActionExecutor to plan and execute complex tasks.
"""

import asyncio
from core.models import Intent, IntentCategory
from core.action_planner import ActionPlanner, DependencyResolver
from core.action_executor import DefaultActionExecutor


async def demo_simple_question():
    """Demo: Simple question intent."""
    print("\n=== Demo: Simple Question ===")
    
    planner = ActionPlanner()
    executor = DefaultActionExecutor()
    
    # Create a question intent
    intent = Intent(
        category=IntentCategory.QUESTION,
        confidence=0.95,
        parameters={'query': 'What is the weather today?'}
    )
    
    # Plan actions
    print(f"Planning actions for: {intent.parameters['query']}")
    plan = await planner.plan(intent)
    
    print(f"\nGenerated plan with {len(plan.actions)} actions:")
    for i, action in enumerate(plan.actions, 1):
        print(f"  {i}. {action.type.value} (priority: {action.priority}, est: {action.estimated_time:.2f}s)")
    
    print(f"\nEstimated total time: {plan.estimated_time:.2f}s")
    
    # Execute plan
    print("\nExecuting plan...")
    results = await executor.execute_plan(plan)
    
    print(f"\nExecution complete:")
    for action_id, result in results.items():
        status = "✓" if result.success else "✗"
        print(f"  {status} {action_id[:8]}... ({result.execution_time:.2f}s)")
    
    # Show statistics
    stats = executor.get_statistics()
    print(f"\nStatistics:")
    print(f"  Success rate: {stats['success_rate']:.1f}%")
    print(f"  Average time: {stats['average_execution_time']:.2f}s")


async def demo_math_calculation():
    """Demo: Math calculation intent."""
    print("\n=== Demo: Math Calculation ===")
    
    planner = ActionPlanner()
    executor = DefaultActionExecutor()
    
    # Create a math intent
    intent = Intent(
        category=IntentCategory.MATH,
        confidence=0.98,
        parameters={
            'expression': 'derivative of x^2 + 3x',
            'operation': 'differentiate'
        }
    )
    
    # Plan and execute
    print(f"Planning actions for: {intent.parameters['expression']}")
    plan = await planner.plan(intent)
    
    print(f"\nGenerated plan with {len(plan.actions)} actions:")
    for action in plan.actions:
        print(f"  - {action.type.value}")
    
    print("\nExecuting plan...")
    results = await executor.execute_plan(plan)
    
    successful = sum(1 for r in results.values() if r.success)
    print(f"\nCompleted: {successful}/{len(results)} actions successful")


async def demo_complex_command():
    """Demo: Complex command with multiple steps."""
    print("\n=== Demo: Complex Command ===")
    
    planner = ActionPlanner()
    executor = DefaultActionExecutor()
    resolver = DependencyResolver()
    
    # Create a command intent
    intent = Intent(
        category=IntentCategory.COMMAND,
        confidence=0.92,
        parameters={
            'command_type': 'browser',
            'browser_action': 'navigate',
            'browser_params': {'url': 'https://github.com'}
        }
    )
    
    # Plan actions
    print(f"Planning command: Open GitHub in browser")
    plan = await planner.plan(intent)
    
    # Analyze dependencies
    print(f"\nDependency analysis:")
    stages = resolver.resolve_execution_order(plan.actions, plan.dependencies)
    print(f"  Execution stages: {len(stages)}")
    
    for i, stage in enumerate(stages, 1):
        print(f"  Stage {i}: {len(stage)} action(s) in parallel")
        for action in stage:
            print(f"    - {action.type.value}")
    
    # Calculate speedup
    speedup = resolver.estimate_parallel_speedup(plan.actions, plan.dependencies)
    print(f"\n  Estimated speedup: {speedup:.2f}x")
    
    # Execute
    print("\nExecuting plan...")
    results = await executor.execute_plan(plan)
    
    print(f"\nExecution results:")
    for result in results.values():
        status = "SUCCESS" if result.success else "FAILED"
        print(f"  [{status}] {result.execution_time:.2f}s")


async def demo_parallel_execution():
    """Demo: Parallel execution of independent actions."""
    print("\n=== Demo: Parallel Execution ===")
    
    planner = ActionPlanner()
    executor = DefaultActionExecutor()
    resolver = DependencyResolver()
    
    # Create a complex question that requires multiple retrievals
    intent = Intent(
        category=IntentCategory.QUESTION,
        confidence=0.95,
        parameters={
            'query': 'Tell me about Python programming',
            'needs_memory': True,
            'needs_knowledge': True,
            'requires_api': True,
            'api_name': 'wikipedia'
        }
    )
    
    # Plan actions
    print("Planning complex query with multiple data sources...")
    plan = await planner.plan(intent)
    
    # Identify parallel actions
    parallel_pairs = resolver.identify_parallel_actions(plan.actions, plan.dependencies)
    print(f"\nFound {len(parallel_pairs)} pairs of actions that can run in parallel")
    
    # Optimize plan
    print("\nOptimizing plan for parallel execution...")
    original_time = plan.estimated_time
    optimized_plan = await planner.optimize_plan(plan)
    
    print(f"  Original estimated time: {original_time:.2f}s")
    print(f"  Optimized estimated time: {optimized_plan.estimated_time:.2f}s")
    print(f"  Improvement: {(1 - optimized_plan.estimated_time/original_time)*100:.1f}%")
    
    # Execute optimized plan
    print("\nExecuting optimized plan...")
    results = await executor.execute_plan(optimized_plan)
    
    successful = sum(1 for r in results.values() if r.success)
    total_time = sum(r.execution_time for r in results.values())
    
    print(f"\nResults:")
    print(f"  Actions completed: {successful}/{len(results)}")
    print(f"  Total execution time: {total_time:.2f}s")


async def demo_error_handling():
    """Demo: Error handling and fallback actions."""
    print("\n=== Demo: Error Handling ===")
    
    planner = ActionPlanner()
    executor = DefaultActionExecutor()
    
    # Create an intent that might fail
    intent = Intent(
        category=IntentCategory.FETCH,
        confidence=0.90,
        parameters={
            'fetch_type': 'api',
            'api_name': 'weather',
            'api_params': {'city': 'London'}
        }
    )
    
    # Plan with fallbacks
    print("Planning API fetch with fallback...")
    plan = await planner.plan(intent)
    
    print(f"\nPlan includes {len(plan.fallbacks)} fallback actions:")
    for action_id, fallback in plan.fallbacks.items():
        print(f"  If {action_id[:8]}... fails → {fallback.type.value}")
    
    # Execute
    print("\nExecuting plan with fallback support...")
    results = await executor.execute_plan(plan)
    
    print(f"\nExecution summary:")
    for action_id, result in results.items():
        if result.success:
            print(f"  ✓ {action_id[:8]}... completed")
        else:
            print(f"  ✗ {action_id[:8]}... failed: {result.error}")


async def main():
    """Run all demos."""
    print("=" * 60)
    print("Action Planning and Orchestration Demo")
    print("=" * 60)
    
    try:
        await demo_simple_question()
        await demo_math_calculation()
        await demo_complex_command()
        await demo_parallel_execution()
        await demo_error_handling()
        
        print("\n" + "=" * 60)
        print("All demos completed successfully!")
        print("=" * 60)
    
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
