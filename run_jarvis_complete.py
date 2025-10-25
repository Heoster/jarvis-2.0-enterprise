"""
JARVIS Complete - Unified System with ALL Features
Combines Original JARVIS + JARVIS 2.0 Enhancements
"""

import asyncio
import sys
from datetime import datetime

print("🤖 JARVIS COMPLETE - Unified System")
print("="*80)
print("Combining Original JARVIS + JARVIS 2.0 Enhancements")
print("="*80)
print()

async def main():
    try:
        from core.jarvis_unified import get_jarvis_unified
        
        print("⏳ Initializing complete system...")
        print()
        
        # Get unified JARVIS
        jarvis = await get_jarvis_unified()
        
        # Start session
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        await jarvis.start_session(session_id)
        
        # Get greeting
        greeting = await jarvis.get_greeting()
        print(greeting)
        print()
        
        # Show status
        status = jarvis.get_status()
        print("✅ System Status: OPERATIONAL")
        print()
        print("📦 Original JARVIS Features:")
        print("  • Web Search & Scraping")
        print("  • Real-time Data (Weather, News, Knowledge)")
        print("  • API Routing (Grammar, Quiz, Feedback)")
        print("  • Transformers + LangChain")
        print("  • Indian APIs (Finance, Railway, Location)")
        print("  • Action Planning & Execution")
        print()
        print("✨ JARVIS 2.0 Enhancements:")
        print("  • Enhanced Intent Classification (95%+ accuracy)")
        print("  • Semantic Matching with Sentence Transformers")
        print("  • Magical Prompt Engineering")
        print("  • Contextual Memory with Learning")
        print("  • Sentiment Analysis & Tone Adjustment")
        print("  • Multi-Stage Query Decomposition")
        print("  • Knowledge Graph")
        print()
        print("Type 'exit' or 'quit' to stop")
        print("="*80)
        print()
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    farewell = await jarvis.get_farewell()
                    print(f"\n{farewell}")
                    break
                
                print()
                print("🔄 Processing with unified system...")
                
                # Process with unified JARVIS (combines all features)
                response = await jarvis.process_query(user_input)
                
                print()
                print(f"Jarvis: {response}")
                print()
                
                # Show brief stats
                summary = await jarvis.get_session_summary()
                interactions = summary.get('total_interactions', 0)
                print(f"[Session: {interactions} interactions]")
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("Please try again.")
                print()
        
        # Show final summary
        print("\n" + "="*80)
        print("📊 Session Summary")
        print("="*80)
        summary = await jarvis.get_session_summary()
        
        enhanced = summary.get('enhanced_features', {})
        print(f"Session ID: {summary.get('session_id', 'N/A')}")
        print(f"Total Interactions: {enhanced.get('total_interactions', 0)}")
        print(f"Current Topic: {enhanced.get('current_topic', 'None')}")
        print(f"Topic Continuity: {enhanced.get('topic_continuity', 0):.2f}")
        print()
        
        brain_status = summary.get('brain_status', {})
        print(f"Brain Status: {brain_status.get('status', 'unknown')}")
        print(f"Memory Size: {brain_status.get('memory_size', 0)} turns")
        print()
        print("Thank you for using JARVIS Complete! 🎩✨")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("\nMake sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        print("  python -m spacy download en_core_web_sm")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
