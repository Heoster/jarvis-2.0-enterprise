# 🛠️ JARVIS 2.0 Developer Guide

**Quick reference for developers working with the enhanced JARVIS system**

---

## 🚀 Quick Start

### Basic Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Download models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Initialize databases
python scripts/init_db.py

# Run tests
pytest tests/test_jarvis_enhanced.py -v
```

### Simple Usage
```python
from core.intent_classifier_enhanced import EnhancedIntentClassifier
from core.prompt_engine_enhanced import EnhancedPromptEngine
from storage.contextual_memory_enhanced import EnhancedContextualMemory

# Initialize
classifier = EnhancedIntentClassifier()
prompt_engine = EnhancedPromptEngine()
memory = EnhancedContextualMemory()

# Process query
intent = await classifier.classify("How do I create a Python list?")
context = await memory.get_context_for_query("Python list")
prompt = prompt_engine.build_prompt("How do I create a Python list?", intent, context=context)
```

---

## 📚 Component Reference

### 1. Enhanced Intent Classifier

**File**: `core/intent_classifier_enhanced.py`

```python
from core.intent_classifier_enhanced import EnhancedIntentClassifier

classifier = EnhancedIntentClassifier()

# Classify with context
intent = await classifier.classify(
    text="git clone repo and npm install",
    context={'recent_intents': ['command', 'code']}
)

# Access results
print(intent.category)  # IntentCategory.COMMAND
print(intent.confidence)  # 0.95
print(intent.parameters['entities'])  # Extracted entities
print(intent.parameters['slots'])  # Filled slots
print(intent.parameters['cli_match'])  # 'git_command'
```

**Key Methods**:
- `classify(text, context)` - Main classification method
- `_extract_entities_spacy(text)` - Extract entities with spaCy
- `_fill_slots(text)` - Fill slots with patterns
- `_match_cli_patterns(text)` - Match CLI commands

---

### 2. Enhanced Prompt Engine

**File**: `core/prompt_engine_enhanced.py`

```python
from core.prompt_engine_enhanced import EnhancedPromptEngine

engine = EnhancedPromptEngine(personality="magical")

# Build prompt
prompt = engine.build_prompt(
    query="How do I create a Forge mod?",
    intent=intent,
    context={
        'context_docs': documents,
        'web_results': search_results,
        'mc_version': '1.19'
    },
    conversation_history=history,
    user_preferences={'prefers_examples': True}
)

# Chain-of-thought prompt
cot_prompt = engine.create_chain_of_thought_prompt(
    query="Implement quicksort",
    steps=["Understand", "Plan", "Code", "Test"]
)

# Add custom template
engine.add_custom_template(
    name="my_template",
    template_string="Custom template: {{ query }}"
)
```

**Available Templates**:
- `question_with_context` - Q&A with context
- `code_with_chain_of_thought` - Step-by-step coding
- `debugging_systematic` - Systematic debugging
- `minecraft_modding` - Minecraft-specific
- `math_with_steps` - Math with steps
- `clarification_request` - Clarification

---

### 3. Enhanced Contextual Memory

**File**: `storage/contextual_memory_enhanced.py`

```python
from storage.contextual_memory_enhanced import EnhancedContextualMemory

memory = EnhancedContextualMemory(max_short_term_turns=3)

# Start session
memory.start_session("session_123", metadata={'user_id': 'student_1'})

# Add interaction
await memory.add_interaction(
    user_input="Explain Python lists",
    assistant_response="Lists are...",
    metadata={'intent': 'python', 'asked_for_example': True}
)

# Get context for query
context = await memory.get_context_for_query("Tell me more about lists")
# Returns: {
#   'short_term_history': [...],
#   'is_topic_continuation': True,
#   'user_preferences': {...},
#   'relevant_memories': [...]
# }

# Learn from feedback
await memory.learn_from_feedback(
    feedback="That was really helpful!",
    context={'used_examples': True}
)

# Get learning summary
summary = await memory.get_learning_summary()
```

**Key Components**:
- `ShortTermMemory` - Last 3 turns
- `LongTermMemory` - Persistent storage
- `UserPreferences` - Learned preferences
- `EnhancedContextualMemory` - Unified interface

---

### 4. Semantic Matcher

**File**: `core/semantic_matcher.py`

```python
from core.semantic_matcher import SemanticMatcher

matcher = SemanticMatcher(model_name='all-MiniLM-L6-v2')

# Compute similarity
similarity = await matcher.compute_similarity(
    "How do I create a list?",
    "What's the way to make a list?"
)
# Returns: 0.85

# Find most similar
candidates = ["greeting", "farewell", "question", "command"]
results = await matcher.find_most_similar(
    query="hello there",
    candidates=candidates,
    threshold=0.5
)
# Returns: [('greeting', 0.92), ...]

# Fuzzy match to intents
intents = {
    'greeting': ['hello', 'hi', 'hey'],
    'farewell': ['bye', 'goodbye']
}
match = await matcher.fuzzy_match("hiya", intents, threshold=0.6)
# Returns: ('greeting', 0.85)

# Semantic search
documents = [
    {'text': 'Python is...', 'id': 1},
    {'text': 'Java is...', 'id': 2}
]
results = await matcher.semantic_search(
    query="Tell me about Python",
    documents=documents,
    top_k=5
)
```

---

### 5. Sentiment Analyzer

**File**: `core/sentiment_analyzer.py`

```python
from core.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# Analyze sentiment
sentiment = analyzer.analyze("I don't understand this at all!")
# Returns: {
#   'mood': 'frustrated',
#   'confidence': 0.9,
#   'tone_adjustment': 'extra_supportive',
#   'intensity': 1.8,
#   'indicators': ['emphatic']
# }

# Get tone recommendation
recommendation = analyzer.get_tone_recommendation(sentiment)
# Returns: {
#   'approach': 'extra_supportive',
#   'suggestions': [
#       'Break down concepts into smaller steps',
#       'Use more analogies and examples',
#       ...
#   ],
#   'emoji_style': 'supportive',
#   'language': 'simple and clear'
# }
```

**Detected Moods**:
- `frustrated` - Student is struggling
- `confident` - Student understands well
- `excited` - Student is enthusiastic
- `curious` - Student wants to explore
- `bored` - Content is too easy

---

### 6. Query Decomposer

**File**: `core/query_decomposer.py`

```python
from core.query_decomposer import QueryDecomposer

decomposer = QueryDecomposer()

# Decompose complex query
tasks = await decomposer.decompose(
    "First search for tutorials, then summarize them, and create a quiz"
)
# Returns: [
#   {'task': 'search for tutorials', 'order': 0, 'dependencies': []},
#   {'task': 'summarize them', 'order': 1, 'dependencies': [0]},
#   {'task': 'create a quiz', 'order': 2, 'dependencies': [1]}
# ]

# Create execution plan
plan = decomposer.create_execution_plan(tasks)
# Returns: {
#   'total_tasks': 3,
#   'tasks': [...],
#   'execution_order': [0, 1, 2],
#   'estimated_steps': 3
# }
```

**Decomposition Types**:
- Sequential: "First X, then Y"
- Parallel: "X and Y and Z"
- Conditional: "If X, then Y"
- Comparison: "Compare X and Y"

---

## 🎯 Common Patterns

### Pattern 1: Complete Query Processing
```python
async def process_query(query: str):
    # 1. Classify intent
    intent = await classifier.classify(query)
    
    # 2. Analyze sentiment
    sentiment = sentiment_analyzer.analyze(query)
    
    # 3. Get context
    context = await memory.get_context_for_query(query)
    
    # 4. Decompose if complex
    if intent.confidence < 0.7:
        tasks = await decomposer.decompose(query)
        # Process each task...
    
    # 5. Build prompt
    prompt = prompt_engine.build_prompt(
        query=query,
        intent=intent,
        context=context,
        user_preferences=context['user_preferences']
    )
    
    # 6. Generate response (with your LLM)
    response = await llm.generate(prompt)
    
    # 7. Add to memory
    await memory.add_interaction(query, response, {'intent': intent.category.value})
    
    return response
```

### Pattern 2: Adaptive Response Based on Sentiment
```python
async def generate_adaptive_response(query: str, response: str):
    # Analyze sentiment
    sentiment = sentiment_analyzer.analyze(query)
    
    # Get tone recommendation
    recommendation = sentiment_analyzer.get_tone_recommendation(sentiment)
    
    # Adjust response based on mood
    if sentiment['mood'] == 'frustrated':
        # Break down into smaller steps
        response = add_step_by_step_breakdown(response)
        response = add_encouragement(response)
    elif sentiment['mood'] == 'confident':
        # Add advanced content
        response = add_advanced_topics(response)
    
    return response
```

### Pattern 3: Learning from Interactions
```python
async def learn_from_interaction(query: str, response: str, feedback: str):
    # Analyze feedback
    if 'helpful' in feedback.lower():
        # Learn what worked
        if 'example' in response.lower():
            await memory.user_preferences.learn_preference(
                'explanation_style', 'use_examples', True, confidence=1.0
            )
    
    # Store in long-term memory
    await memory.long_term.store_memory(
        memory_type='successful_interaction',
        content=f"Q: {query}\nA: {response}",
        metadata={'feedback': feedback}
    )
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/test_jarvis_enhanced.py -v --asyncio-mode=auto
```

### Run Specific Test Class
```bash
pytest tests/test_jarvis_enhanced.py::TestEnhancedIntentClassifier -v
```

### Run Single Test
```bash
pytest tests/test_jarvis_enhanced.py::TestEnhancedIntentClassifier::test_casual_query -v
```

### Test with Coverage
```bash
pytest tests/test_jarvis_enhanced.py --cov=core --cov=storage --cov-report=html
```

---

## 🐛 Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Component Status
```python
# Intent classifier
info = classifier.get_model_info()
print(info)
# {'status': 'loaded', 'spacy_enabled': True, ...}

# Memory
summary = await memory.get_learning_summary()
print(summary)
# {'total_interactions': 10, 'preferences': {...}, ...}
```

### Inspect Intent Details
```python
intent = await classifier.classify("test query")
print(f"Category: {intent.category}")
print(f"Confidence: {intent.confidence}")
print(f"Parameters: {intent.parameters}")
print(f"Context: {intent.context}")
```

---

## ⚡ Performance Tips

### 1. Cache Semantic Embeddings
```python
# Embeddings are automatically cached in SemanticMatcher
matcher = SemanticMatcher()
# First call: ~100ms
await matcher.compute_similarity(text1, text2)
# Subsequent calls with same texts: ~1ms
```

### 2. Limit Memory Size
```python
# Keep short-term memory small
memory = EnhancedContextualMemory(max_short_term_turns=3)

# Periodically clean long-term memory
if len(memory.long_term.memories) > 1000:
    memory.long_term.memories = memory.long_term.memories[-1000:]
```

### 3. Batch Processing
```python
# Process multiple queries in parallel
queries = ["query1", "query2", "query3"]
intents = await asyncio.gather(*[
    classifier.classify(q) for q in queries
])
```

---

## 🔧 Configuration

### Environment Variables
```bash
# .env file
JARVIS_SPACY_MODEL=en_core_web_sm
JARVIS_SEMANTIC_MODEL=all-MiniLM-L6-v2
JARVIS_SHORT_TERM_MEMORY_TURNS=3
JARVIS_MEMORY_STORAGE=data/memory
JARVIS_ENABLE_SENTIMENT_ANALYSIS=true
```

### Programmatic Configuration
```python
# Custom spaCy model
classifier = EnhancedIntentClassifier(spacy_model="en_core_web_lg")

# Custom semantic model
matcher = SemanticMatcher(model_name="paraphrase-MiniLM-L6-v2")

# Custom memory settings
memory = EnhancedContextualMemory(max_short_term_turns=5)
```

---

## 📖 Additional Resources

- **Full Documentation**: `JARVIS_UPGRADES_COMPLETE.md`
- **Test Examples**: `tests/test_jarvis_enhanced.py`
- **API Reference**: See docstrings in each module
- **Codeex Features**: `CODEEX_FEATURES.md`
- **Project Status**: `PROJECT_STATUS.md`

---

## 🆘 Common Issues

### Issue: spaCy model not found
```bash
# Solution
python -m spacy download en_core_web_sm
```

### Issue: Sentence Transformers slow
```python
# Solution: Use smaller model
matcher = SemanticMatcher(model_name='all-MiniLM-L6-v2')  # Fast
# Instead of: 'all-mpnet-base-v2'  # Slower but more accurate
```

### Issue: Memory growing too large
```python
# Solution: Clear old sessions
memory.clear_session()

# Or limit long-term memory
memory.long_term.memories = memory.long_term.memories[-500:]
```

---

## 🎓 Best Practices

1. **Always use async/await** for I/O operations
2. **Cache embeddings** when possible
3. **Limit memory size** to prevent growth
4. **Use context** for better classification
5. **Learn from feedback** to improve over time
6. **Test with diverse inputs** including errors
7. **Monitor sentiment** to adjust tone
8. **Decompose complex queries** for better handling

---

**Happy Coding! 🚀✨**

*For questions or issues, refer to the comprehensive documentation in `JARVIS_UPGRADES_COMPLETE.md`*
