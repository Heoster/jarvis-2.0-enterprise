# JARVIS Enhanced - Quick Reference Card

## 🚀 Installation (30 seconds)

```bash
pip install -r requirements-enhanced.txt
python -m spacy download en_core_web_sm
```

## 🎮 Quick Start (3 lines)

```python
from core.jarvis_unified import UnifiedJarvis
jarvis = UnifiedJarvis(student_id="heoster")
response = await jarvis.process_query("Explain Python functions")
```

## 📦 Core Components

| Component | File | Purpose |
|-----------|------|---------|
| Intent Classifier | `intent_classifier_enhanced.py` | NER + slot filling |
| Semantic Matcher | `semantic_matcher.py` | Fuzzy matching |
| Prompt Engine | `prompt_engine_enhanced.py` | Magical templates |
| Memory | `contextual_memory_enhanced.py` | Student profiles |
| Query Decomposer | `query_decomposer.py` | Multi-stage reasoning |
| Sentiment Analyzer | `sentiment_analyzer.py` | Mood detection |
| Knowledge Graph | `knowledge_graph.py` | Concept tracking |
| Unified JARVIS | `jarvis_unified.py` | All-in-one |

## 🎯 Common Tasks

### Process Query
```python
response = await jarvis.process_query("Your question here")
```

### Check Progress
```python
progress = jarvis.get_student_progress()
print(f"Mastered: {progress['knowledge']['mastered_concepts']}")
```

### Get Recommendations
```python
recommendations = jarvis.get_learning_recommendations()
for rec in recommendations:
    print(rec)
```

### End Session
```python
summary = await jarvis.end_session()
```

## 🧪 Testing

```bash
# All tests
pytest tests/test_jarvis_enhanced.py -v

# Specific component
pytest tests/test_jarvis_enhanced.py::TestEnhancedIntentClassifier -v

# Interactive demo
python examples/jarvis_enhanced_demo.py --mode interactive
```

## 🎨 Personality Modes

- `magical_mentor` - Warm, encouraging, magical ✨
- `jarvis_technical` - Sophisticated, precise 🎯
- `codeex_magical` - Playful, adventurous 🔮

## 😊 Sentiment States

- `frustrated` → Extra supportive 💪
- `confident` → Challenging 🚀
- `excited` → Enthusiastic 🎉
- `curious` → Exploratory 🔍
- `bored` → Advanced 🔥

## 📊 Key Features

✅ spaCy NER  
✅ Sentence Transformers  
✅ LangChain Memory  
✅ Knowledge Graphs  
✅ Query Decomposition  
✅ Sentiment Analysis  
✅ Magical Personality  
✅ Student Profiles  

## 🔧 Troubleshooting

**spaCy not found:**
```bash
python -m spacy download en_core_web_sm
```

**Slow first run:**
- Sentence Transformers downloads model (~100MB)
- Subsequent runs are fast

**Memory not saving:**
```bash
mkdir -p data/students
```

## 📈 Performance

- Intent: <100ms
- Semantic: <200ms
- Full pipeline: <500ms

## 🎓 Student Profile

```json
{
  "learning_style": "balanced",
  "skill_level": "intermediate",
  "emotional_state": "confident",
  "interests": ["python", "minecraft"],
  "goals": ["Learn modding"]
}
```

## 💡 Pro Tips

1. **Use sentiment:** Jarvis adapts to mood
2. **Track progress:** Knowledge graph shows path
3. **Save sessions:** Profiles persist learning
4. **Compound queries:** Auto-decomposes complex questions
5. **Interactive mode:** Best for testing

## 🚀 Production Checklist

- [ ] Dependencies installed
- [ ] spaCy model downloaded
- [ ] Tests passing
- [ ] Student profiles directory created
- [ ] Logs directory configured
- [ ] Demo runs successfully

## 📚 Documentation

- `JARVIS_UPGRADES_COMPLETE.md` - Full features
- `INTEGRATION_GUIDE.md` - Integration steps
- `JARVIS_IMPLEMENTATION_SUMMARY.md` - Overview

## 🎉 One-Liner Demo

```bash
python examples/jarvis_enhanced_demo.py --mode interactive
```

**That's it! You're ready to use JARVIS Enhanced! ✨🚀**
