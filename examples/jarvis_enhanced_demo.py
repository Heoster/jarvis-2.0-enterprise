"""Demo script showcasing all enhanced JARVIS features."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.jarvis_unified import UnifiedJarvis
from core.logger import get_logger

logger = get_logger(__name__)


async def demo_basic_queries():
    """Demo basic query processing."""
    print("\n" + "="*80)
    print("🎯 DEMO 1: Basic Query Processing")
    print("="*80 + "\n")
    
    jarvis = UnifiedJarvis(student_id="demo_user", personality="magical_mentor")
    
    queries = [
        "Hello Jarvis!",
        "What is Python?",
        "I'm confused about loops",
        "This is awesome! Show me more!",
    ]
    
    for query in queries:
        print(f"\n👤 Student: {query}")
        response = await jarvis.process_query(query)
        print(f"🤖 Jarvis: {response}\n")
        print("-" * 80)
    
    await jarvis.end_session()


async def demo_compound_queries():
    """Demo compound query decomposition."""
    print("\n" + "="*80)
    print("🎯 DEMO 2: Compound Query Decomposition")
    print("="*80 + "\n")
    
    jarvis = UnifiedJarvis(student_id="demo_user")
    
    compound_query = "Explain Python functions and then show me an example and compare with classes"
    
    print(f"👤 Student: {compound_query}\n")
    response = await jarvis.process_query(compound_query)
    print(f"🤖 Jarvis:\n{response}\n")
    
    await jarvis.end_session()


async def demo_sentiment_adaptation():
    """Demo sentiment-based response adaptation."""
    print("\n" + "="*80)
    print("🎯 DEMO 3: Sentiment-Based Adaptation")
    print("="*80 + "\n")
    
    jarvis = UnifiedJarvis(student_id="demo_user")
    
    emotional_queries = [
        ("I'm so confused and stuck on this problem", "frustrated"),
        ("Got it! This makes perfect sense now!", "confident"),
        ("This is amazing! I love learning this!", "excited"),
        ("This is too easy and boring", "bored"),
    ]
    
    for query, expected_mood in emotional_queries:
        print(f"\n👤 Student: {query}")
        print(f"   Expected mood: {expected_mood}")
        
        response = await jarvis.process_query(query)
        print(f"🤖 Jarvis: {response}\n")
        print("-" * 80)
    
    await jarvis.end_session()


async def demo_knowledge_tracking():
    """Demo knowledge graph and progress tracking."""
    print("\n" + "="*80)
    print("🎯 DEMO 4: Knowledge Graph & Progress Tracking")
    print("="*80 + "\n")
    
    jarvis = UnifiedJarvis(student_id="demo_user")
    
    # Simulate learning progression
    learning_queries = [
        "Explain variables in Python",
        "What are data types?",
        "How do conditionals work?",
        "Show me how to use loops",
        "Explain functions",
    ]
    
    for query in learning_queries:
        print(f"\n👤 Student: {query}")
        response = await jarvis.process_query(query)
        print(f"🤖 Jarvis: {response[:200]}...\n")
    
    # Show progress
    print("\n" + "="*80)
    print("📊 LEARNING PROGRESS")
    print("="*80 + "\n")
    
    progress = jarvis.get_student_progress()
    print(f"Total Interactions: {progress.get('memory', {}).get('total_interactions', 0)}")
    print(f"Emotional State: {progress.get('memory', {}).get('emotional_state', 'neutral')}")
    
    if 'knowledge' in progress:
        kg_progress = progress['knowledge']
        print(f"\nConcepts Mastered: {kg_progress.get('mastered_concepts', 0)}/{kg_progress.get('total_concepts', 0)}")
        print(f"Progress: {kg_progress.get('progress_percentage', 0):.1f}%")
    
    # Show recommendations
    print("\n" + "="*80)
    print("💡 LEARNING RECOMMENDATIONS")
    print("="*80 + "\n")
    
    recommendations = jarvis.get_learning_recommendations()
    for rec in recommendations:
        print(rec)
    
    await jarvis.end_session()


async def demo_memory_and_context():
    """Demo contextual memory and conversation continuity."""
    print("\n" + "="*80)
    print("🎯 DEMO 5: Contextual Memory & Conversation Continuity")
    print("="*80 + "\n")
    
    jarvis = UnifiedJarvis(student_id="demo_user")
    
    conversation = [
        "What is recursion?",
        "Can you show me an example?",
        "What if I want to use it with lists?",
        "Thanks! That was helpful!",
    ]
    
    for query in conversation:
        print(f"\n👤 Student: {query}")
        response = await jarvis.process_query(query)
        print(f"🤖 Jarvis: {response}\n")
        
        # Show short-term memory
        if jarvis.enhanced_memory:
            context = jarvis.enhanced_memory.get_short_term_context()
            print(f"   [Memory: {len(context)} recent exchanges]")
        
        print("-" * 80)
    
    await jarvis.end_session()


async def demo_technical_queries():
    """Demo technical query handling."""
    print("\n" + "="*80)
    print("🎯 DEMO 6: Technical Query Handling")
    print("="*80 + "\n")
    
    jarvis = UnifiedJarvis(student_id="demo_user")
    
    technical_queries = [
        "Create a Minecraft mod using Forge",
        "Run npm install express",
        "Write a Python function to sort a list",
        "How do I use git commit?",
    ]
    
    for query in technical_queries:
        print(f"\n👤 Student: {query}")
        response = await jarvis.process_query(query)
        print(f"🤖 Jarvis: {response}\n")
        print("-" * 80)
    
    await jarvis.end_session()


async def demo_system_status():
    """Demo system status and diagnostics."""
    print("\n" + "="*80)
    print("🎯 DEMO 7: System Status & Diagnostics")
    print("="*80 + "\n")
    
    jarvis = UnifiedJarvis(student_id="demo_user")
    
    status = jarvis.get_status()
    
    print("System Status:")
    print(f"  Student ID: {status['student_id']}")
    print(f"  Personality: {status['personality']}")
    print(f"\nComponents:")
    
    for component, loaded in status['components'].items():
        status_icon = "✅" if loaded else "❌"
        print(f"  {status_icon} {component.replace('_', ' ').title()}")
    
    print(f"\nAll Features Enabled: {'✅' if status['features_enabled'] else '❌'}")


async def run_all_demos():
    """Run all demo scenarios."""
    print("\n" + "="*80)
    print("🚀 JARVIS ENHANCED FEATURES - COMPREHENSIVE DEMO")
    print("="*80)
    
    demos = [
        ("Basic Queries", demo_basic_queries),
        ("Compound Queries", demo_compound_queries),
        ("Sentiment Adaptation", demo_sentiment_adaptation),
        ("Knowledge Tracking", demo_knowledge_tracking),
        ("Memory & Context", demo_memory_and_context),
        ("Technical Queries", demo_technical_queries),
        ("System Status", demo_system_status),
    ]
    
    for name, demo_func in demos:
        try:
            await demo_func()
            print(f"\n✅ {name} demo completed\n")
        except Exception as e:
            print(f"\n❌ {name} demo failed: {e}\n")
            logger.error(f"Demo failed: {e}", exc_info=True)
    
    print("\n" + "="*80)
    print("🎉 ALL DEMOS COMPLETED!")
    print("="*80 + "\n")


async def interactive_mode():
    """Interactive mode for testing."""
    print("\n" + "="*80)
    print("🎮 JARVIS ENHANCED - INTERACTIVE MODE")
    print("="*80)
    print("\nType 'quit' or 'exit' to end session")
    print("Type 'status' to see system status")
    print("Type 'progress' to see learning progress")
    print("Type 'help' for more commands\n")
    
    jarvis = UnifiedJarvis(student_id="interactive_user", personality="magical_mentor")
    
    while True:
        try:
            query = input("\n👤 You: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['quit', 'exit', 'bye']:
                print("\n🤖 Jarvis: Goodbye! Saving your progress...\n")
                summary = await jarvis.end_session()
                if summary:
                    print(f"Session Duration: {summary.get('duration', 0):.0f}s")
                    print(f"Total Exchanges: {summary.get('exchanges', 0)}")
                break
            
            if query.lower() == 'status':
                status = jarvis.get_status()
                print("\n🤖 Jarvis: System Status:")
                for component, loaded in status['components'].items():
                    print(f"  {'✅' if loaded else '❌'} {component}")
                continue
            
            if query.lower() == 'progress':
                progress = jarvis.get_student_progress()
                print("\n🤖 Jarvis: Your Progress:")
                print(f"  Interactions: {progress.get('memory', {}).get('total_interactions', 0)}")
                print(f"  Emotional State: {progress.get('memory', {}).get('emotional_state', 'neutral')}")
                continue
            
            if query.lower() == 'help':
                print("\n🤖 Jarvis: Available Commands:")
                print("  quit/exit - End session")
                print("  status - Show system status")
                print("  progress - Show learning progress")
                print("  help - Show this message")
                continue
            
            # Process query
            response = await jarvis.process_query(query)
            print(f"\n🤖 Jarvis: {response}")
            
        except KeyboardInterrupt:
            print("\n\n🤖 Jarvis: Session interrupted. Saving progress...\n")
            await jarvis.end_session()
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.error(f"Interactive mode error: {e}", exc_info=True)


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="JARVIS Enhanced Features Demo")
    parser.add_argument(
        '--mode',
        choices=['all', 'interactive', 'basic', 'compound', 'sentiment', 'knowledge', 'memory', 'technical', 'status'],
        default='all',
        help='Demo mode to run'
    )
    parser.add_argument('--diagnose', action='store_true', help='Run diagnostics')
    
    args = parser.parse_args()
    
    if args.diagnose:
        await demo_system_status()
        return
    
    mode_map = {
        'all': run_all_demos,
        'interactive': interactive_mode,
        'basic': demo_basic_queries,
        'compound': demo_compound_queries,
        'sentiment': demo_sentiment_adaptation,
        'knowledge': demo_knowledge_tracking,
        'memory': demo_memory_and_context,
        'technical': demo_technical_queries,
        'status': demo_system_status,
    }
    
    demo_func = mode_map.get(args.mode, run_all_demos)
    await demo_func()


if __name__ == "__main__":
    asyncio.run(main())
