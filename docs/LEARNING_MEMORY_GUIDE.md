# Jarvis Learning & Memory System Guide

## Overview

Jarvis now features an advanced contextual memory system that enables continuous learning from user interactions. The system combines:

- **Short-term Memory**: Last 3 conversation turns for immediate context
- **Long-term Memory**: Persistent user preferences and patterns
- **Session Awareness**: Tracks conversation sessions and context
- **Automatic Learning**: Detects patterns and adapts responses

## Architecture

### Components

1. **ConversationBuffer**: Manages recent conversation turns (short-term memory)
2. **UserPreferences**: Learns and stores long-term user preferences
3. **ContextualMemory**: Integrates both memory types with the assistant

### Memory Flow

```
User Input → Contextual Memory → Intent Classification → Response Generation
     ↓                                                            ↓
Learning Patterns ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
```

## Features

### 1. Short-Term Context (Last 3 Turns)

Jarvis remembers the last 3 conversation turns, enabling:
- Follow-up questions without repeating context
- Pronoun resolution ("it", "that", "this")
- Contextual understanding

**Example:**
```
User: "What's the weather in Mumbai?"
Jarvis: "The weather in Mumbai is 28°C and sunny."
User: "What about tomorrow?"  # Jarvis knows "it" refers to Mumbai
Jarvis: "Tomorrow in Mumbai will be 30°C with partly cloudy skies."
```

### 2. User Preferences Learning

Jarvis automatically learns your preferences:

#### Explanation Style
- **Use Examples**: Learns if you frequently ask for examples
- **Detailed**: Prefers comprehensive explanations
- **Concise**: Prefers brief, to-the-point answers
- **Step-by-Step**: Likes guided tutorials

#### Automatic Detection

The system detects patterns from your queries:

| User Pattern | Learned Preference |
|-------------|-------------------|
| "show me an example" | Always include examples |
| "explain in detail" | Provide detailed responses |
| "brief answer please" | Keep responses concise |
| "step by step guide" | Use step-by-step format |

### 3. Session Awareness

Each conversation session is tracked:
- Session duration
- Number of turns
- Session metadata
- Context continuity

## Usage

### Basic Usage

```python
from core.assistant import Assistant

# Initialize assistant
assistant = Assistant()

# Start a session
assistant.start_session("user_123_session_1")

# Process queries - Jarvis learns automatically
response1 = await assistant.process_query("Explain how Bitcoin works")
response2 = await assistant.process_query("Can you give me an example?")
# Jarvis learns: User prefers examples

response3 = await assistant.process_query("What's machine learning?")
# Jarvis automatically includes examples now!
```

### Manual Preference Setting

```python
# Set a preference manually
await assistant.set_preference(
    category="explanation_style",
    preference="always_use_examples",
    value=True
)

# Set language preference
await assistant.set_preference(
    category="language",
    preference="preferred_language",
    value="hindi"
)
```

### Providing Feedback

```python
# Positive feedback reinforces current behavior
await assistant.provide_feedback("That was perfect, thanks!")

# Negative feedback triggers adjustment
await assistant.provide_feedback("Too complicated, can you simplify?")

# Specific feedback teaches preferences
await assistant.provide_feedback("Please always show examples")
```

### Getting Learning Summary

```python
# See what Jarvis has learned about you
summary = await assistant.get_learning_summary()

print(summary)
# Output:
# {
#     'total_preferences': 5,
#     'categories': ['explanation_style', 'language'],
#     'preferences': {
#         'explanation_style': {
#             'use_examples': 5,
#             'detailed': 3,
#             'always_use_examples': True
#         }
#     },
#     'session_duration': 1234.5,
#     'turns_in_session': 8
# }
```

### Session Management

```python
# Start a new session
assistant.start_session("session_456", metadata={
    'user_id': 'user_123',
    'platform': 'web'
})

# Clear session (keeps long-term preferences)
assistant.clear_session()
```

## Preference Categories

### Explanation Style
- `use_examples`: Include examples in explanations
- `detailed`: Provide comprehensive information
- `concise`: Keep responses brief
- `step_by_step`: Use step-by-step format
- `simplify`: Use simpler language
- `always_use_examples`: Always include examples (explicit)

### Language
- `preferred_language`: User's preferred language
- `technical_level`: Technical complexity level

### Response Format
- `use_bullet_points`: Prefer bullet points
- `use_code_blocks`: Include code examples
- `use_analogies`: Use analogies for explanation

## API Integration

### REST API Example

```python
from fastapi import FastAPI
from core.assistant import Assistant

app = FastAPI()
assistant = Assistant()

@app.post("/chat")
async def chat(message: str, session_id: str):
    # Start or continue session
    assistant.start_session(session_id)
    
    # Process with learning
    response = await assistant.process_query(message)
    
    return {
        "response": response.text,
        "confidence": response.confidence
    }

@app.post("/feedback")
async def feedback(feedback: str, session_id: str):
    await assistant.provide_feedback(feedback)
    return {"status": "learned"}

@app.get("/preferences/{session_id}")
async def get_preferences(session_id: str):
    summary = await assistant.get_learning_summary()
    return summary
```

## Advanced Features

### Custom Learning Patterns

You can extend the learning system:

```python
from storage.contextual_memory import ContextualMemory

# Access contextual memory
memory = assistant.contextual_memory

# Add custom pattern detection
async def detect_custom_pattern(user_input: str):
    if "in hindi" in user_input.lower():
        await memory.user_preferences.learn_preference(
            category="language",
            preference="preferred_language",
            value="hindi",
            confidence=1.0
        )
```

### Memory Persistence

All preferences are automatically persisted to SQLite:
- Location: `data/memory.db`
- Encrypted sensitive data
- Automatic cleanup of old data

### Context Injection

The system automatically injects context into prompts:

```
Recent conversation:
User: What's Bitcoin?
Assistant: Bitcoin is a cryptocurrency...
User: How does it work?

User preferences:
- User prefers examples
- User prefers detailed explanations

[Current Query]: Can you explain mining?
```

## Best Practices

### 1. Session Management
- Start a new session for each user conversation
- Use meaningful session IDs (e.g., `user_id_timestamp`)
- Clear sessions when appropriate

### 2. Feedback Loop
- Encourage users to provide feedback
- Use feedback to refine preferences
- Monitor learning summary regularly

### 3. Privacy
- Sensitive preferences are encrypted
- Implement data retention policies
- Allow users to clear their data

### 4. Testing
- Test with different user patterns
- Verify preference learning
- Check context continuity

## Examples

### Example 1: Learning from Repeated Patterns

```python
# User asks for examples multiple times
await assistant.process_query("What's Python?")
await assistant.process_query("Can you show an example?")

await assistant.process_query("Explain functions")
await assistant.process_query("Give me an example")

await assistant.process_query("What are classes?")
# Jarvis now automatically includes examples!
```

### Example 2: Contextual Follow-ups

```python
# First query
response1 = await assistant.process_query(
    "What's the Bitcoin price?"
)
# Response: "Bitcoin is currently $45,000"

# Follow-up without context
response2 = await assistant.process_query(
    "What about yesterday?"
)
# Jarvis knows we're still talking about Bitcoin price
```

### Example 3: Preference Override

```python
# Set a strong preference
await assistant.set_preference(
    category="explanation_style",
    preference="always_use_examples",
    value=True
)

# All future responses will include examples
response = await assistant.process_query("What's AI?")
# Response includes examples automatically
```

## Troubleshooting

### Memory Not Persisting
- Check database path: `data/memory.db`
- Verify write permissions
- Check logs for errors

### Preferences Not Applied
- Verify preference threshold (needs 3+ occurrences)
- Check preference category and name
- Use manual setting for immediate effect

### Context Not Working
- Ensure session is started
- Check buffer size (default: 3 turns)
- Verify conversation storage

## Configuration

### Memory Settings

```python
# In core/config.py or environment variables
MEMORY_MAX_TURNS = 3  # Short-term buffer size
MEMORY_RETENTION_DAYS = 30  # Long-term data retention
MEMORY_CONFIDENCE_THRESHOLD = 0.8  # Learning confidence
```

### Custom Buffer Size

```python
from storage.contextual_memory import ContextualMemory

# Create with custom buffer size
memory = ContextualMemory(
    memory_store=memory_store,
    max_turns=5  # Keep last 5 turns
)
```

## Future Enhancements

- Semantic memory search
- Multi-user preference profiles
- Preference export/import
- Advanced pattern recognition
- Emotion detection and adaptation
- Cross-session learning

## Support

For issues or questions:
1. Check logs: `logs/jarvis.log`
2. Review memory database: `data/memory.db`
3. Test with simple patterns first
4. Verify LangChain installation

## Summary

Jarvis's learning and memory system makes interactions more natural and personalized over time. The system:
- ✅ Remembers recent context (3 turns)
- ✅ Learns user preferences automatically
- ✅ Adapts responses based on patterns
- ✅ Persists learning across sessions
- ✅ Provides session awareness
- ✅ Supports manual preference setting
- ✅ Enables feedback-based learning

Start using it today and watch Jarvis become more personalized to your needs!
