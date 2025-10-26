# JARVIS Enhanced Features - Integration Guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install enhanced dependencies
pip install -r requirements-enhanced.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Download Sentence Transformer model (happens automatically on first use)
```

### 2. Verify Installation

```bash
# Run enhanced tests
python -m pytest tests/test_jarvis_enhanced.py -v

# Or run the demo
python examples/jarvis_enhanced_demo.py
```

### 3. Basic Usage

```python
from core.jarvis_unified import UnifiedJarvis

# Initialize enhanced JARVIS
jarvis = UnifiedJarvis(
    student_id="heoster",
    personality="magical_mentor"
)

# Process query with all enhancements
response = await jarvis.process_query(
    "Explain Python functions and then show me an example"
)

print(response)
```

## 📚 Component Integration

### Enhanced Intent Classification

```python
from core.intent_classifier_enhanced import EnhancedIntentClassifier

classifier = EnhancedIntentClassifier()

# Classify with NER and slot filling
intent = await classifier.classify("Create a Minecraft mod using Forge")

print(f"Intent: {intent.category}")
print(f"Confidence: {intent.confidence}")
print(f"Slots: {intent.context['slots']}")
print(f"Entities: {intent.context['entities']}")
```

### Semantic Matching

```python
from core.semantic_matcher import SemanticMatcher

matcher = SemanticMatcher()

# Compute similarity
similarity = await matcher.compute_similarity(
    "How do I install Python?",
    "What's the process for setting up Python?"
)

# Fuzzy intent matching
intents = {
    'install': ["install software", "setup program"],
    'code': ["write function", "create class"]
}

match = await matcher.fuzzy_match(query, intents)
```

### Enhanced Memory

```python
from storage.contextual_memory_enhanced import EnhancedContextualMemory

memory = EnhancedContextualMemory(student_id="heoster")

# Add exchange with sentiment
memory.add_exchange(
    user_input="I'm confused about loops",
    assistant_response="Let me help...",
    intent="question",
    sentiment="frustrated"
)

# Get adaptive context
context = memory.get_adaptive_context()
print(f"Emotional state: {context['emotional_state']}")
print(f"Preferences: {context['student_preferences']}")

# Save profile
memory.save_student_profile()
```

### Query Decomposition

```python
from core.query_decomposer import QueryDecomposer

decomposer = QueryDecomposer()

# Decompose complex query
tasks = await decomposer.decompose(
    "Explain functions and then show an example and compare with classes"
)

# Create execution plan
plan = decomposer.create_execution_plan(tasks)

# Execute in order
for task_id in plan['execution_order']:
    task = tasks[task_id]
    print(f"Executing: {task['task']}")
```

### Sentiment Analysis

```python
from core.sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# Analyze sentiment
result = analyzer.analyze("I'm so confused and stuck!")

print(f"Mood: {result['mood']}")
print(f"Intensity: {result['intensity']}")

# Get tone recommendations
recommendations = analyzer.get_tone_recommendation(result)
print(f"Approach: {recommendations['approach']}")
print(f"Suggestions: {recommendations['suggestions']}")
```

### Knowledge Graph

```python
from core.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph(student_id="heoster")

# Track mastered concepts
mastered = {"variables", "data_types", "operators"}

# Get learning path
path = kg.get_learning_path("classes", mastered)
print(kg.visualize_path(path))

# Get next recommendations
next_concepts = kg.get_next_concepts(mastered)
for concept, score in next_concepts[:3]:
    print(f"{concept}: readiness {score:.2f}")

# Record progress
kg.record_attempt("conditionals", success=True)
kg.save_graph()
```

## 🔧 Migrating Existing Code

### Step 1: Update jarvis_brain.py

```python
# Add to imports
from core.intent_classifier_enhanced import EnhancedIntentClassifier
from core.semantic_matcher import SemanticMatcher
from storage.contextual_memory_enhanced import EnhancedContextualMemory
from core.query_decomposer import QueryDecomposer
from core.sentiment_analyzer import SentimentAnalyzer
from core.knowledge_graph import KnowledgeGraph

# In __init__
self.enhanced_classifier = EnhancedIntentClassifier()
self.semantic_matcher = SemanticMatcher()
self.enhanced_memory = EnhancedContextualMemory(student_id="heoster")
self.query_decomposer = QueryDecomposer()
self.sentiment_analyzer = SentimentAnalyzer()
self.knowledge_graph = KnowledgeGraph(student_id="heoster")
```

### Step 2: Enhance Query Processing

```python
async def generate_response(self, query: str, context: Optional[Dict] = None):
    # 1. Analyze sentiment
    sentiment = self.sentiment_analyzer.analyze(query)
    
    # 2. Check if query needs decomposition
    if self.query_decomposer._needs_decomposition(query):
        tasks = await self.query_decomposer.decompose(query)
        # Process each task sequentially
        responses = []
        for task in tasks:
            response = await self._process_single_task(task['task'], sentiment)
            responses.append(response)
        return "\n\n".join(responses)
    
    # 3. Enhanced intent classification
    intent = await self.enhanced_classifier.classify(query)
    
    # 4. Add to enhanced memory
    self.enhanced_memory.add_exchange(
        user_input=query,
        assistant_response="",  # Will update after generation
        intent=intent.category.value,
        sentiment=sentiment['mood']
    )
    
    # 5. Get adaptive context
    adaptive_context = self.enhanced_memory.get_adaptive_context()
    
    # 6. Generate response with tone adjustment
    tone_rec = self.sentiment_analyzer.get_tone_recommendation(sentiment)
    
    # ... rest of generation logic
```

### Step 3: Update Response Generation

```python
from core.prompt_engine_enhanced import EnhancedPromptEngine

# In __init__
self.prompt_engine = EnhancedPromptEngine(personality="magical_mentor")

# In response generation
prompt = self.prompt_engine.build_prompt(
    intent=intent,
    query=query,
    context_docs=retrieved_docs,
    conversation_history=self.enhanced_memory.get_short_term_context(),
    student_name="Heoster",
    emotional_state=sentiment['mood']
)
```

## 🎯 Feature-Specific Integration

### Adding Custom Concepts to Knowledge Graph

```python
# Add Minecraft modding concepts
kg.add_concept("forge_basics", category="minecraft", difficulty=2)
kg.add_concept("custom_blocks", category="minecraft", difficulty=3)
kg.add_prerequisite("custom_blocks", "forge_basics")
kg.add_prerequisite("forge_basics", "java_basics")
```

### Creating Custom Sentiment Patterns

```python
# Extend sentiment analyzer
analyzer.sentiment_patterns['excited_about_minecraft'] = {
    'keywords': ['minecraft', 'mod', 'awesome', 'cool'],
    'patterns': [r'minecraft.*awesome', r'love.*modding'],
    'tone_adjustment': 'enthusiastic_technical'
}
```

### Custom Prompt Templates

```python
from jinja2 import Template

engine.templates['minecraft_help'] = Template("""
🎮 Minecraft Modding Help

Your Question: {{ query }}

{% if mod_type %}
Mod Type: {{ mod_type }}
{% endif %}

Let me guide you through creating this mod! ⚡
""")
```

## 🧪 Testing Your Integration

### Unit Tests

```python
# test_my_integration.py
import pytest
from core.jarvis_unified import UnifiedJarvis

@pytest.mark.asyncio
async def test_enhanced_query_processing():
    jarvis = UnifiedJarvis(student_id="test")
    
    response = await jarvis.process_query(
        "I'm confused about Python functions"
    )
    
    assert response is not None
    assert len(response) > 0
    
    # Check sentiment was detected
    memory = jarvis.enhanced_memory
    last_exchange = memory.get_short_term_context()[-1]
    assert last_exchange['sentiment'] == 'frustrated'
```

### Integration Tests

```bash
# Run all enhanced tests
python -m pytest tests/test_jarvis_enhanced.py -v

# Run specific test
python -m pytest tests/test_jarvis_enhanced.py::TestEnhancedIntentClassifier -v

# Run with coverage
python -m pytest tests/test_jarvis_enhanced.py --cov=core --cov-report=html
```

## 📊 Monitoring and Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('core')
logger.setLevel(logging.DEBUG)
```

### Check Component Status

```python
# Check if all components loaded
jarvis = UnifiedJarvis()

status = {
    'intent_classifier': jarvis.enhanced_classifier.pipeline is not None,
    'semantic_matcher': jarvis.semantic_matcher.model is not None,
    'sentiment_analyzer': jarvis.sentiment_analyzer.transformer_model is not None,
    'memory': len(jarvis.enhanced_memory.student_profile) > 0,
    'knowledge_graph': jarvis.knowledge_graph.graph.number_of_nodes() > 0
}

print("Component Status:")
for component, loaded in status.items():
    print(f"  {component}: {'✅' if loaded else '❌'}")
```

### Profile Performance

```python
import time

start = time.time()
response = await jarvis.process_query("Explain Python")
duration = time.time() - start

print(f"Query processed in {duration:.2f}s")
```

## 🔄 Gradual Migration Strategy

### Phase 1: Parallel Running (Week 1)
- Keep existing JARVIS running
- Add enhanced components alongside
- Compare outputs
- Collect metrics

### Phase 2: Selective Enhancement (Week 2-3)
- Use enhanced intent classification for technical queries
- Apply sentiment analysis to all queries
- Start building student profiles

### Phase 3: Full Integration (Week 4)
- Replace old components with enhanced versions
- Migrate all queries to new pipeline
- Enable all advanced features

### Phase 4: Optimization (Week 5+)
- Fine-tune models with collected data
- Optimize performance bottlenecks
- Expand knowledge graph

## 🎓 Best Practices

### 1. Student Profile Management
```python
# Always save profiles at session end
def on_session_end():
    memory.save_student_profile()
    knowledge_graph.save_graph()
```

### 2. Error Handling
```python
try:
    intent = await classifier.classify(query)
except Exception as e:
    logger.error(f"Classification failed: {e}")
    # Fallback to basic classification
    intent = await basic_classifier.classify(query)
```

### 3. Performance Optimization
```python
# Cache embeddings for common queries
@lru_cache(maxsize=1000)
def get_cached_embedding(text: str):
    return semantic_matcher.get_embedding(text)
```

### 4. Graceful Degradation
```python
# If advanced features fail, fall back to basic
if not enhanced_classifier.spacy_nlp:
    logger.warning("spaCy not available, using basic NER")
    # Use regex-based entity extraction
```

## 📈 Measuring Success

### Key Metrics

1. **Intent Classification Accuracy**
   - Track correct vs incorrect classifications
   - Monitor confidence scores

2. **Student Engagement**
   - Session duration
   - Number of follow-up questions
   - Emotional state progression

3. **Learning Progress**
   - Concepts mastered over time
   - Success rate on challenges
   - Knowledge graph growth

4. **Response Quality**
   - Student satisfaction ratings
   - Clarification request frequency
   - Task completion rate

### Analytics Dashboard

```python
def generate_analytics():
    return {
        'total_sessions': memory.student_profile['session_count'],
        'total_interactions': memory.student_profile['total_interactions'],
        'concepts_mastered': len(kg.get_progress_summary(mastered)['mastered_concepts']),
        'average_sentiment': calculate_avg_sentiment(),
        'most_common_intents': get_intent_distribution(),
        'learning_velocity': calculate_learning_velocity()
    }
```

## 🆘 Troubleshooting

### Common Issues

**Issue: spaCy model not found**
```bash
python -m spacy download en_core_web_sm
```

**Issue: Sentence Transformers slow on first run**
- Model downloads on first use (1-2 minutes)
- Subsequent runs are fast

**Issue: Memory profiles not saving**
```python
# Ensure directory exists
Path("data/students").mkdir(parents=True, exist_ok=True)
```

**Issue: Knowledge graph empty**
```python
# Reinitialize base concepts
kg._initialize_base_concepts()
kg.save_graph()
```

## 🎉 Success Checklist

- [ ] All dependencies installed
- [ ] spaCy model downloaded
- [ ] Tests passing
- [ ] Student profiles saving
- [ ] Knowledge graph persisting
- [ ] Sentiment detection working
- [ ] Query decomposition functional
- [ ] Semantic matching accurate
- [ ] Memory tracking conversations
- [ ] Magical personality active

## 📞 Support

For issues or questions:
1. Check logs in `logs/jarvis.log`
2. Run diagnostic: `python examples/jarvis_enhanced_demo.py --diagnose`
3. Review test output: `pytest tests/test_jarvis_enhanced.py -v`

**JARVIS Enhanced is ready to provide world-class AI assistance! ✨🚀**
