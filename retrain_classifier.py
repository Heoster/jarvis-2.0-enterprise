"""
Retrain the intent classifier with better examples
"""

from core.intent_classifier_enhanced import EnhancedIntentClassifier

print("🔧 Retraining JARVIS Intent Classifier...")

classifier = EnhancedIntentClassifier()

# Better training data
training_data = [
    # Greetings
    ("hi", "conversational"),
    ("hello", "conversational"),
    ("hey", "conversational"),
    ("hii", "conversational"),
    ("good morning", "conversational"),
    ("how are you", "conversational"),
    ("how do you do", "conversational"),
    
    # Questions
    ("what is tesla coil", "question"),
    ("tell me about codeex", "question"),
    ("what time is now", "question"),
    ("who is elon musk", "question"),
    ("explain python", "question"),
    ("how does it work", "question"),
    ("why is the sky blue", "question"),
    ("when was it invented", "question"),
    
    # Search/Fetch
    ("search portugal", "fetch"),
    ("find information about", "fetch"),
    ("look up", "fetch"),
    ("google for", "fetch"),
    ("search for", "fetch"),
    
    # Commands
    ("open chrome", "command"),
    ("close window", "command"),
    ("start application", "command"),
    ("run program", "command"),
    
    # Math
    ("calculate 5 plus 3", "math"),
    ("what is 10 times 5", "math"),
    ("solve equation", "math"),
    
    # Code
    ("write python code", "code"),
    ("debug this", "code"),
    ("explain function", "code"),
]

texts = [text for text, _ in training_data]
labels = [label for _, label in training_data]

classifier.train(texts, labels)

print("✅ Classifier retrained with better examples!")
print(f"   Total examples: {len(training_data)}")
print(f"   Categories: {set(labels)}")
print("\nNow run: python run_jarvis_enhanced.py")
