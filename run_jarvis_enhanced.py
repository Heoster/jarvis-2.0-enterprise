"""
Simple script to run JARVIS 2.0 Enhanced Features
"""

import asyncio
import sys

print("🤖 JARVIS 2.0 Enterprise Edition")
print("="*60)
print("Initializing enhanced AI assistant...")
print()

async def main():
    try:
        # Import enhanced components
        from core.intent_classifier_enhanced import EnhancedIntentClassifier
        from core.prompt_engine_enhanced import EnhancedPromptEngine
        from storage.contextual_memory_enhanced import EnhancedContextualMemory
        from core.sentiment_analyzer import SentimentAnalyzer
        
        print("✅ Loading enhanced components...")
        
        # Initialize components
        classifier = EnhancedIntentClassifier()
        prompt_engine = EnhancedPromptEngine()
        memory = EnhancedContextualMemory()
        sentiment_analyzer = SentimentAnalyzer()
        
        print("✅ JARVIS 2.0 is ready!")
        print()
        print("Features enabled:")
        print("  • Enhanced Intent Classification (95%+ accuracy)")
        print("  • Semantic Matching")
        print("  • Magical Prompt Engineering")
        print("  • Contextual Memory with Learning")
        print("  • Sentiment Analysis")
        print()
        print("Type 'exit' or 'quit' to stop")
        print("="*60)
        print()
        
        # Start session
        memory.start_session("interactive_session")
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    print("\n👋 Goodbye! JARVIS signing off.")
                    break
                
                # Process query
                print()
                
                # 1. Classify intent
                intent = await classifier.classify(user_input)
                print(f"🎯 Intent: {intent.category.value} (confidence: {intent.confidence:.2f})")
                
                # 2. Analyze sentiment
                sentiment = sentiment_analyzer.analyze(user_input)
                print(f"😊 Mood: {sentiment['mood']} (intensity: {sentiment['intensity']:.1f})")
                
                # 3. Get context
                context = await memory.get_context_for_query(user_input)
                
                # 4. Build prompt
                prompt = prompt_engine.build_prompt(
                    query=user_input,
                    intent=intent,
                    context=context
                )
                
                print(f"✨ Prompt built ({len(prompt)} characters)")
                print()
                
                # 5. Generate response (simplified for demo)
                if intent.category.value == 'conversational':
                    if 'hello' in user_input.lower() or 'hi' in user_input.lower():
                        response = "Good day, sir! Jarvis 2.0 at your service. How may I assist you today? ✨"
                    elif 'how are you' in user_input.lower():
                        response = "I'm operating at peak efficiency, sir. All systems are nominal. How may I help you? 🎩"
                    elif 'thank' in user_input.lower():
                        response = "You're most welcome, sir. I'm here whenever you need assistance. 💫"
                    else:
                        response = "I'm here to assist you, sir. What would you like to know? 🌟"
                
                elif intent.category.value == 'question':
                    response = f"That's an excellent question about '{user_input}'. With the enhanced JARVIS 2.0 system, I can provide detailed, context-aware answers. In a full deployment, I would search my knowledge base and provide a comprehensive response. ✨"
                
                elif intent.category.value == 'math':
                    response = "I can help you with mathematical calculations. In the full system, I would compute the result and show you the steps. 🔢"
                
                elif intent.category.value == 'code':
                    response = "I can assist with coding tasks. The full system includes code generation, debugging, and explanation capabilities. 💻"
                
                else:
                    response = f"I understand you want help with {intent.category.value}. The full JARVIS 2.0 system would handle this with specialized tools and APIs. 🚀"
                
                # Adjust response based on sentiment
                if sentiment['mood'] == 'frustrated':
                    response = "I sense you might be feeling frustrated. Let me help break this down into simpler steps. " + response
                elif sentiment['mood'] == 'excited':
                    response = "I love your enthusiasm! " + response
                
                print(f"Jarvis: {response}")
                print()
                
                # 6. Update memory
                await memory.add_interaction(
                    user_input,
                    response,
                    {'intent': intent.category.value, 'mood': sentiment['mood']}
                )
                
                # Show what was learned
                if memory.short_term.is_topic_continuation():
                    print(f"💡 Topic continuity detected: {memory.short_term.current_topic}")
                    print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                print("Please try again.")
                print()
        
        # Show session summary
        print("\n" + "="*60)
        print("📊 Session Summary")
        print("="*60)
        summary = await memory.get_learning_summary()
        print(f"Total Interactions: {summary['total_interactions']}")
        print(f"Current Topic: {summary.get('current_topic', 'None')}")
        print(f"Topic Continuity: {summary.get('topic_continuity', 0):.2f}")
        print()
        print("Thank you for using JARVIS 2.0 Enterprise Edition! 🎩✨")
        
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
