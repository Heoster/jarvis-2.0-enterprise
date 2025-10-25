# Data Strategy for On-Device Assistant

## The Data Challenge

Building a JARVIS-like AI requires substantial training data. This document outlines practical strategies to address this challenge without requiring massive datasets upfront.

---

## Current Data Situation

### What We Have ✅
- Pre-trained NLP models (spaCy)
- Pre-trained embeddings (sentence-transformers)
- Pre-trained LLMs (via Ollama)
- Basic intent classifier (trained on small dataset)

### What We Need ⚠️
- More intent classification examples (target: 1000+ per category)
- Entity extraction training data
- Conversation examples for context learning
- User interaction logs for personalization

---

## Strategy 1: Leverage Pre-trained Models

**Approach**: Use existing models trained on billions of examples

### Implementation
```python
# Already implemented:
- spaCy: Trained on OntoNotes (1M+ words)
- Sentence-BERT: Trained on 1B+ sentence pairs
- Llama models: Trained on trillions of tokens
```

### Benefits
- ✅ No training data needed
- ✅ High quality out-of-the-box
- ✅ Covers general language understanding

### Limitations
- ⚠️ Not customized to our specific use cases
- ⚠️ May not understand domain-specific commands

---

## Strategy 2: Synthetic Data Generation

**Approach**: Programmatically generate training examples

### Example: Intent Classification Data
```python
# Generate synthetic queries for MATH intent
templates = [
    "What is {num1} {op} {num2}?",
    "Calculate {num1} {op} {num2}",
    "Solve {num1} {op} {num2}",
    "{num1} {op} {num2} equals what?",
]

operations = ['+', '-', '*', '/', '^']
numbers = range(1, 100)

# Generates 2000+ examples
for template in templates:
    for op in operations:
        for _ in range(100):
            num1, num2 = random.choice(numbers), random.choice(numbers)
            query = template.format(num1=num1, op=op, num2=num2)
            # Add to training set
```

### Benefits
- ✅ Can generate unlimited examples
- ✅ Covers edge cases systematically
- ✅ No manual labeling needed

### Limitations
- ⚠️ May not capture natural language variation
- ⚠️ Requires good templates

---

## Strategy 3: Data Augmentation

**Approach**: Create variations of existing examples

### Techniques
```python
# Paraphrasing
"What's the weather?" → "Tell me the weather"
"What's the weather?" → "How's the weather today?"

# Synonym replacement
"Open Gmail" → "Launch Gmail"
"Open Gmail" → "Start Gmail"

# Entity substitution
"Open Gmail" → "Open Chrome"
"Open Gmail" → "Open Notepad"

# Noise injection
"What is 5 + 3?" → "What is 5+3?"
"What is 5 + 3?" → "whats 5 + 3"
```

### Implementation
```python
import nlpaug.augmenter.word as naw

# Synonym augmentation
aug = naw.SynonymAug(aug_src='wordnet')
augmented = aug.augment("Open my email")
# → "Launch my electronic mail"

# Back-translation
aug = naw.BackTranslationAug()
augmented = aug.augment("What's the weather?")
# → "How is the weather?"
```

### Benefits
- ✅ Multiplies existing data 5-10x
- ✅ Improves model robustness
- ✅ Captures natural variations

---

## Strategy 4: Active Learning

**Approach**: Learn from user corrections

### Implementation Flow
```
1. User: "What's 5 times 7?"
2. System: Classifies as QUESTION (wrong)
3. User: Corrects to MATH
4. System: Stores correction
5. Retrains model with new example
```

### Code Example
```python
class ActiveLearner:
    def __init__(self):
        self.corrections = []
        self.retrain_threshold = 100
    
    async def record_correction(
        self, 
        query: str, 
        predicted: str, 
        correct: str
    ):
        self.corrections.append({
            'query': query,
            'predicted': predicted,
            'correct': correct,
            'timestamp': datetime.now()
        })
        
        if len(self.corrections) >= self.retrain_threshold:
            await self.retrain_model()
    
    async def retrain_model(self):
        # Add corrections to training set
        # Retrain classifier
        # Deploy new model
        pass
```

### Benefits
- ✅ Learns from real usage
- ✅ Improves over time
- ✅ Personalized to user

---

## Strategy 5: Transfer Learning

**Approach**: Fine-tune pre-trained models on small datasets

### Example: Intent Classification
```python
from transformers import AutoModelForSequenceClassification

# Start with pre-trained BERT
model = AutoModelForSequenceClassification.from_pretrained(
    'bert-base-uncased',
    num_labels=7  # Our intent categories
)

# Fine-tune on just 100 examples per category
# Still achieves 90%+ accuracy
```

### Benefits
- ✅ Requires minimal training data (100-500 examples)
- ✅ Leverages billions of pre-training examples
- ✅ Fast training (minutes, not days)

---

## Strategy 6: Community Contributions

**Approach**: Crowdsource training data

### Implementation
```markdown
# Call for Contributions

Help improve the assistant by contributing examples!

## How to Contribute
1. Fork the repository
2. Add examples to `data/training/intents.json`
3. Submit a pull request

## Example Format
{
  "query": "What's the weather in London?",
  "intent": "FETCH",
  "entities": [
    {"text": "London", "type": "LOCATION"}
  ]
}

## Rewards
- Recognition in contributors list
- Early access to new features
- Community badges
```

### Benefits
- ✅ Scales with community size
- ✅ Diverse examples
- ✅ Free data collection

---

## Strategy 7: User Interaction Logging

**Approach**: Learn from actual usage (with consent)

### Implementation
```python
class InteractionLogger:
    def __init__(self, consent_manager):
        self.consent = consent_manager
    
    async def log_interaction(
        self, 
        query: str, 
        intent: str, 
        success: bool
    ):
        # Only log if user consented
        if not await self.consent.has_permission('data_collection'):
            return
        
        # Anonymize and store
        await self.store_anonymized({
            'query_hash': hash(query),
            'intent': intent,
            'success': success,
            'timestamp': datetime.now()
        })
```

### Privacy Considerations
- ✅ Explicit user consent required
- ✅ Data stays local
- ✅ Anonymization applied
- ✅ User can delete anytime

---

## Practical Implementation Plan

### Phase 1: Bootstrap (Week 1-2)
**Goal**: Get to 500 examples per intent

1. **Synthetic Generation** (300 examples)
   - Create templates for each intent
   - Generate variations programmatically
   
2. **Manual Creation** (100 examples)
   - Write realistic queries
   - Cover common use cases
   
3. **Augmentation** (100 examples)
   - Apply paraphrasing
   - Add noise and variations

**Estimated Effort**: 2-3 days
**Result**: Functional classifier (85-90% accuracy)

### Phase 2: Expansion (Week 3-4)
**Goal**: Reach 1000+ examples per intent

1. **More Templates** (300 examples)
   - Add edge cases
   - Cover different phrasings
   
2. **Community Contributions** (200 examples)
   - Open call for contributions
   - Review and merge PRs
   
3. **Active Learning Setup** (ongoing)
   - Implement correction mechanism
   - Start collecting user feedback

**Estimated Effort**: 1 week
**Result**: Robust classifier (90-95% accuracy)

### Phase 3: Refinement (Week 5-8)
**Goal**: Continuous improvement

1. **User Interaction Logging** (ongoing)
   - Collect real usage data
   - Identify failure patterns
   
2. **Regular Retraining** (weekly)
   - Incorporate new examples
   - Deploy updated models
   
3. **Quality Monitoring** (ongoing)
   - Track accuracy metrics
   - A/B test improvements

**Estimated Effort**: Ongoing
**Result**: Personalized, improving system (95%+ accuracy)

---

## Data Requirements by Component

### Intent Classifier
- **Minimum**: 100 examples per intent (7 intents = 700 total)
- **Recommended**: 500 examples per intent (3,500 total)
- **Optimal**: 1000+ examples per intent (7,000+ total)

### Entity Extraction
- **Minimum**: Use pre-trained spaCy (no data needed)
- **Recommended**: 200 annotated examples for custom entities
- **Optimal**: 1000+ annotated examples

### Conversation Context
- **Minimum**: 50 multi-turn conversations
- **Recommended**: 200 conversations
- **Optimal**: 1000+ conversations

### Personalization
- **Minimum**: 100 user interactions
- **Recommended**: 1000 interactions
- **Optimal**: 10,000+ interactions (per user)

---

## Tools and Resources

### Data Generation Tools
```bash
# Install augmentation library
pip install nlpaug

# Install paraphrasing tool
pip install parrot-paraphraser

# Install back-translation
pip install googletrans==4.0.0-rc1
```

### Annotation Tools
- **Label Studio**: Web-based annotation
- **Prodigy**: Efficient annotation with active learning
- **Doccano**: Open-source text annotation

### Synthetic Data Libraries
- **Faker**: Generate fake but realistic data
- **Mimesis**: Fast data generation
- **SDV**: Synthetic data vault

---

## Success Metrics

### Data Quality
- ✅ Inter-annotator agreement >90%
- ✅ Balanced class distribution
- ✅ Diverse linguistic patterns
- ✅ Covers edge cases

### Model Performance
- ✅ Intent accuracy >95%
- ✅ Entity F1 score >90%
- ✅ User satisfaction >4/5
- ✅ Continuous improvement trend

---

## Conclusion

**The data challenge is manageable** through:

1. **Smart Reuse**: Leverage pre-trained models (billions of examples)
2. **Synthetic Generation**: Create unlimited training data
3. **Augmentation**: Multiply existing examples 5-10x
4. **Active Learning**: Improve from user feedback
5. **Transfer Learning**: Need only 100-500 examples
6. **Community**: Crowdsource contributions

**Bottom Line**: You don't need millions of examples to start. With 500-1000 well-crafted examples per intent and smart techniques, you can build a highly accurate system that improves over time.

---

**Next Steps**:
1. Run `python scripts/generate_training_data.py` (to be created)
2. Review and augment generated data
3. Train initial model
4. Deploy and collect user feedback
5. Iterate and improve

**Estimated Time to Production-Quality Data**: 4-6 weeks
