"""
Demo script showing Jarvis's learning and memory capabilities
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.assistant import Assistant
from core.logger import get_logger

logger = get_logger(__name__)


async def demo_short_term_memory():
    """Demonstrate short-term memory (last 3 turns)"""
    print("\n" + "="*60)
    print("DEMO 1: Short-Term Memory (Context Awareness)")
    print("="*60 + "\n")
    
    assistant = Assistant()
    assistant.start_session("demo_session_1")
    
    # First query
    print("User: What's the weather in Mumbai?")
    response1 = await assistant.process_query("What's the weather in Mumbai?")
    print(f"Jarvis: {response1.text}\n")
    
    # Follow-up without repeating context
    print("User: What about tomorrow?")
    response2 = await assistant.process_query("What about tomorrow?")
    print(f"Jarvis: {response2.text}\n")
    
    # Another follow-up
    print("User: And the day after?")
    response3 = await assistant.process_query("And the day after?")
    print(f"Jarvis: {response3.text}\n")
    
    assistant.clear_session()


async def demo_preference_learning():
    """Demonstrate automatic preference learning"""
    print("\n" + "="*60)
    print("DEMO 2: Automatic Preference Learning")
    print("="*60 + "\n")
    
    assistant = Assistant()
    assistant.start_session("demo_session_2")
    
    # User asks for examples multiple times
    queries = [
        ("What's Python?", "Can you show me an example?"),
        ("Explain functions in Python", "Give me an example"),
        ("What are classes?", "Show an example please"),
    ]
    
    for main_query, example_request in queries:
        print(f"User: {main_query}")
        response1 = await assistant.process_query(main_query)
        print(f"Jarvis: {response1.text[:100]}...\n")
        
        print(f"User: {example_request}")
        response2 = await assistant.process_query(example_request)
        print(f"Jarvis: {response2.text[:100]}...\n")
    
    # Check what was learned
    print("\n--- Learning Summary ---")
    summary = await assistant.get_learning_summary()
    print(f"Total preferences learned: {summary['total_preferences']}")
    print(f"Preference categories: {summary['categories']}")
    
    if 'explanation_style' in summary['preferences']:
        style = summary['preferences']['explanation_style']
        print(f"\nExplanation style preferences:")
        for pref, count in style.items():
            print(f"  - {pref}: {count}")
    
    # Now ask a new question - Jarvis should include examples automatically
    print("\n\nUser: What's machine learning?")
    response = await assistant.process_query("What's machine learning?")
    print(f"Jarvis: {response.text}")
    print("\n✓ Notice: Jarvis now includes examples automatically!")
    
    assistant.clear_session()


async def demo_manual_preferences():
    """Demonstrate manual preference setting"""
    print("\n" + "="*60)
    print("DEMO 3: Manual Preference Setting")
    print("="*60 + "\n")
    
    assistant = Assistant()
    assistant.start_session("demo_session_3")
    
    # Set preferences manually
    print("Setting preferences:")
    print("  - Always use examples: True")
    print("  - Explanation style: Detailed")
    print("  - Use step-by-step: True\n")
    
    await assistant.set_preference(
        category="explanation_style",
        preference="always_use_examples",
        value=True
    )
    
    await assistant.set_preference(
        category="explanation_style",
        preference="detailed",
        value=5  # High count = strong preference
    )
    
    await assistant.set_preference(
        category="explanation_style",
        preference="step_by_step",
        value=5
    )
    
    # Ask a question
    print("User: How do I create a REST API?")
    response = await assistant.process_query("How do I create a REST API?")
    print(f"Jarvis: {response.text}")
    print("\n✓ Response follows user preferences!")
    
    assistant.clear_session()


async def demo_feedback_learning():
    """Demonstrate learning from feedback"""
    print("\n" + "="*60)
    print("DEMO 4: Learning from Feedback")
    print("="*60 + "\n")
    
    assistant = Assistant()
    assistant.start_session("demo_session_4")
    
    # Initial query
    print("User: Explain quantum computing")
    response1 = await assistant.process_query("Explain quantum computing")
    print(f"Jarvis: {response1.text[:150]}...\n")
    
    # Provide feedback
    print("User: Too complicated, can you simplify?")
    await assistant.provide_feedback("Too complicated, can you simplify?")
    print("✓ Feedback recorded\n")
    
    # Ask again
    print("User: Explain it again")
    response2 = await assistant.process_query("Explain quantum computing again")
    print(f"Jarvis: {response2.text[:150]}...")
    print("\n✓ Jarvis adjusted the explanation!")
    
    # Positive feedback
    print("\nUser: Perfect! That's much better")
    await assistant.provide_feedback("Perfect! That's much better")
    print("✓ Positive feedback reinforces the adjustment\n")
    
    assistant.clear_session()


async def demo_session_continuity():
    """Demonstrate session continuity and context"""
    print("\n" + "="*60)
    print("DEMO 5: Session Continuity")
    print("="*60 + "\n")
    
    assistant = Assistant()
    
    # Session 1
    print("--- Session 1 ---")
    assistant.start_session("user_123_morning")
    
    print("User: I'm learning Python")
    await assistant.process_query("I'm learning Python")
    
    print("User: Can you help me with functions?")
    await assistant.process_query("Can you help me with functions?")
    
    summary1 = await assistant.get_learning_summary()
    print(f"Session duration: {summary1['session_duration']:.1f}s")
    print(f"Turns in session: {summary1['turns_in_session']}\n")
    
    assistant.clear_session()
    
    # Session 2 - preferences persist
    print("--- Session 2 (Later) ---")
    assistant.start_session("user_123_evening")
    
    print("User: Now I want to learn about classes")
    response = await assistant.process_query("Now I want to learn about classes")
    print(f"Jarvis: {response.text[:100]}...")
    print("\n✓ Jarvis remembers preferences from previous session!")
    
    assistant.clear_session()


async def demo_interactive():
    """Interactive demo - chat with Jarvis"""
    print("\n" + "="*60)
    print("DEMO 6: Interactive Chat (Type 'quit' to exit)")
    print("="*60 + "\n")
    
    assistant = Assistant()
    assistant.start_session("interactive_demo")
    
    print("Try these commands:")
    print("  - Ask questions normally")
    print("  - Type 'summary' to see what Jarvis learned")
    print("  - Type 'feedback: <message>' to provide feedback")
    print("  - Type 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                break
            
            if user_input.lower() == 'summary':
                summary = await assistant.get_learning_summary()
                print(f"\n--- Learning Summary ---")
                print(f"Session duration: {summary['session_duration']:.1f}s")
                print(f"Turns: {summary['turns_in_session']}")
                print(f"Preferences: {summary['total_preferences']}")
                if summary['preferences']:
                    print("\nLearned preferences:")
                    for category, prefs in summary['preferences'].items():
                        print(f"  {category}:")
                        for pref, value in prefs.items():
                            print(f"    - {pref}: {value}")
                print()
                continue
            
            if user_input.lower().startswith('feedback:'):
                feedback = user_input[9:].strip()
                await assistant.provide_feedback(feedback)
                print("✓ Feedback recorded\n")
                continue
            
            # Process query
            response = await assistant.process_query(user_input)
            print(f"Jarvis: {response.text}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}\n")
    
    print("\nGoodbye!")
    assistant.clear_session()


async def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("JARVIS LEARNING & MEMORY SYSTEM DEMO")
    print("="*60)
    
    demos = [
        ("1", "Short-Term Memory", demo_short_term_memory),
        ("2", "Preference Learning", demo_preference_learning),
        ("3", "Manual Preferences", demo_manual_preferences),
        ("4", "Feedback Learning", demo_feedback_learning),
        ("5", "Session Continuity", demo_session_continuity),
        ("6", "Interactive Chat", demo_interactive),
    ]
    
    print("\nAvailable demos:")
    for num, name, _ in demos:
        print(f"  {num}. {name}")
    print("  0. Run all demos")
    
    choice = input("\nSelect demo (0-6): ").strip()
    
    if choice == "0":
        # Run all non-interactive demos
        for num, name, demo_func in demos[:-1]:
            await demo_func()
            await asyncio.sleep(1)
    else:
        # Run selected demo
        for num, name, demo_func in demos:
            if num == choice:
                await demo_func()
                break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\nError: {e}")
