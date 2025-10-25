"""
Codeex Assistant Demo
Demonstrates all the magical features!
"""

import asyncio
from core.codeex_assistant import create_codeex_assistant


async def demo_greeting():
    """Demo personalized greeting"""
    print("=" * 60)
    print("🌟 CODEEX GREETING DEMO 🌟")
    print("=" * 60)
    
    assistant = create_codeex_assistant()
    greeting = await assistant.get_greeting()
    print(f"\n{greeting}\n")


async def demo_grammar_correction():
    """Demo grammar correction"""
    print("=" * 60)
    print("📝 GRAMMAR CORRECTION DEMO 📝")
    print("=" * 60)
    
    assistant = create_codeex_assistant()
    
    test_sentences = [
        "hlo how r u",
        "i want to lern python",
        "can u help me with my homwork",
        "This is a perfect sentence."
    ]
    
    for sentence in test_sentences:
        print(f"\n📥 Input: {sentence}")
        response = await assistant.process_query(f"/correct {sentence}")
        print(f"📤 Output:\n{response.text}\n")


async def demo_quiz():
    """Demo quiz system"""
    print("=" * 60)
    print("🎯 QUIZ DEMO 🎯")
    print("=" * 60)
    
    assistant = create_codeex_assistant()
    
    # Start a quiz
    print("\n🎮 Starting Python quiz...")
    response = await assistant.process_query("/quiz python 3")
    print(f"\n{response.text}\n")
    
    # Get quiz stats
    stats = await assistant.get_stats()
    print(f"\n📊 Quiz Stats: {stats['quizzes']}\n")


async def demo_help():
    """Demo knowledge base help"""
    print("=" * 60)
    print("💡 KNOWLEDGE BASE DEMO 💡")
    print("=" * 60)
    
    assistant = create_codeex_assistant()
    
    help_queries = [
        "minecraft forge setup",
        "python basics",
        "debugging tips"
    ]
    
    for query in help_queries:
        print(f"\n❓ Query: {query}")
        response = await assistant.process_query(f"/help {query}")
        print(f"💬 Response:\n{response.text}\n")


async def demo_feedback():
    """Demo feedback system"""
    print("=" * 60)
    print("⭐ FEEDBACK DEMO ⭐")
    print("=" * 60)
    
    assistant = create_codeex_assistant()
    
    # Record some feedback
    await assistant.record_feedback(
        "What is 2+2?",
        "The answer is 4",
        "positive",
        "Great explanation!"
    )
    
    await assistant.record_feedback(
        "How do I code?",
        "Just code",
        "negative",
        "Too vague, needs more detail"
    )
    
    # Get stats
    stats = await assistant.get_stats()
    print(f"\n📊 Feedback Stats:")
    print(f"   Total: {stats['feedback']['total_feedback']}")
    print(f"   Satisfaction: {stats['feedback']['satisfaction_rate']}%")
    print(f"   Positive: {stats['feedback'].get('positive', 0)} 👍")
    print(f"   Negative: {stats['feedback'].get('negative', 0)} 👎")
    
    # Generate report
    report = await assistant.generate_improvement_report()
    print(f"\n{report}")


async def demo_regular_query():
    """Demo regular query with personality"""
    print("=" * 60)
    print("💬 REGULAR QUERY DEMO 💬")
    print("=" * 60)
    
    assistant = create_codeex_assistant()
    
    queries = [
        "What is 15 + 27?",
        "Tell me about Python",
        "How do I learn coding?"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        response = await assistant.process_query(query)
        print(f"💬 Response: {response.text}\n")


async def main():
    """Run all demos"""
    print("\n")
    print("✨" * 30)
    print("🎉 WELCOME TO CODEEX AI DEMO! 🎉")
    print("✨" * 30)
    print("\n")
    
    demos = [
        ("Greeting", demo_greeting),
        ("Grammar Correction", demo_grammar_correction),
        ("Quiz System", demo_quiz),
        ("Knowledge Base", demo_help),
        ("Feedback System", demo_feedback),
        ("Regular Queries", demo_regular_query)
    ]
    
    for name, demo_func in demos:
        try:
            await demo_func()
            await asyncio.sleep(1)  # Pause between demos
        except Exception as e:
            print(f"\n❌ Error in {name} demo: {e}\n")
    
    print("\n")
    print("✨" * 30)
    print("🎊 DEMO COMPLETE! 🎊")
    print("✨" * 30)
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
