"""
Simple JARVIS 2.0 Demo - No heavy models required
"""

import asyncio

print("🤖 JARVIS 2.0 Enterprise Edition - Quick Demo")
print("="*60)
print()

async def main():
    print("✅ Initializing JARVIS 2.0...")
    print()
    
    # Simple demo without heavy models
    print("🎯 JARVIS 2.0 Features:")
    print("  • Enhanced Intent Classification")
    print("  • Contextual Memory")
    print("  • Sentiment Analysis")
    print("  • Magical Personality")
    print()
    print("Type your message (or 'exit' to quit)")
    print("="*60)
    print()
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye! JARVIS 2.0 signing off. ✨")
                break
            
            # Simple intent detection
            user_lower = user_input.lower()
            
            if any(word in user_lower for word in ['hello', 'hi', 'hey']):
                response = "Good day, sir! Jarvis 2.0 at your service. How may I assist you today? ✨"
                intent = "greeting"
            
            elif any(word in user_lower for word in ['how are you', 'how do you do']):
                response = "I'm operating at peak efficiency, sir. All systems are nominal. The enhanced JARVIS 2.0 is ready to assist! 🎩"
                intent = "status_check"
            
            elif any(word in user_lower for word in ['thank', 'thanks']):
                response = "You're most welcome, sir. I'm here whenever you need assistance. 💫"
                intent = "gratitude"
            
            elif any(word in user_lower for word in ['what can you do', 'help', 'features']):
                response = """I'm JARVIS 2.0 Enterprise Edition with these capabilities:

🎯 Enhanced Intent Classification (95%+ accuracy)
🔍 Semantic Matching for fuzzy queries
✨ Magical Prompt Engineering
🧠 Contextual Memory that learns from interactions
😊 Sentiment Analysis for emotionally intelligent responses
🧩 Multi-stage Query Decomposition
📚 Knowledge Graph for learning paths
🧪 Comprehensive Testing (33 tests passing)

I can help with questions, coding, math, and much more! 🚀"""
                intent = "capabilities"
            
            elif '?' in user_input:
                response = f"That's an excellent question, sir! With JARVIS 2.0's enhanced capabilities, I can provide detailed, context-aware answers. The full system includes web search, knowledge retrieval, and intelligent reasoning. ✨"
                intent = "question"
            
            elif any(word in user_lower for word in ['code', 'program', 'python', 'java']):
                response = "I can assist with coding tasks, sir. JARVIS 2.0 includes code generation, debugging, and explanation capabilities with magical personality. 💻✨"
                intent = "code"
            
            elif any(word in user_lower for word in ['calculate', 'math', 'solve']):
                response = "I'm ready to help with mathematical calculations, sir. The full system includes step-by-step solutions and explanations. 🔢"
                intent = "math"
            
            else:
                response = f"I understand, sir. JARVIS 2.0 is processing your request with enhanced intelligence. In the full deployment, I would provide a comprehensive, context-aware response. 🌟"
                intent = "general"
            
            # Add to history
            conversation_history.append({
                'user': user_input,
                'jarvis': response,
                'intent': intent
            })
            
            print(f"\nJarvis: {response}\n")
            print(f"[Intent: {intent} | Turn: {len(conversation_history)}]")
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print()
    
    # Show summary
    if conversation_history:
        print("\n" + "="*60)
        print("📊 Session Summary")
        print("="*60)
        print(f"Total Interactions: {len(conversation_history)}")
        print(f"Intents Detected: {', '.join(set(turn['intent'] for turn in conversation_history))}")
        print()
    
    print("Thank you for using JARVIS 2.0 Enterprise Edition! 🎩✨")
    print("\nFor full features, run: python run_jarvis_enhanced.py")
    print("(Requires: pip install -r requirements.txt)")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
