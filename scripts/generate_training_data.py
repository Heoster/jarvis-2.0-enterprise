"""
Generate synthetic training data for intent classification.

This script creates training examples for all intent categories using
templates and variations to bootstrap the training dataset.
"""

import json
import random
from pathlib import Path
from typing import List, Dict
from datetime import datetime


class TrainingDataGenerator:
    """Generate synthetic training data for intent classification."""
    
    def __init__(self):
        """Initialize the generator with templates."""
        self.templates = self._load_templates()
        self.generated_data = []
    
    def _load_templates(self) -> Dict[str, List[str]]:
        """Load query templates for each intent category."""
        return {
            'QUESTION': [
                "What is {topic}?",
                "Tell me about {topic}",
                "Explain {topic}",
                "How does {topic} work?",
                "Why is {topic} important?",
                "Can you explain {topic}?",
                "I want to know about {topic}",
                "What do you know about {topic}?",
            ],
            'COMMAND': [
                "Open {app}",
                "Launch {app}",
                "Start {app}",
                "Close {app}",
                "Quit {app}",
                "Run {app}",
                "Execute {app}",
                "Show me {app}",
            ],
            'MATH': [
                "What is {num1} {op} {num2}?",
                "Calculate {num1} {op} {num2}",
                "Solve {num1} {op} {num2}",
                "{num1} {op} {num2} equals what?",
                "Compute {num1} {op} {num2}",
                "What's {num1} {op} {num2}?",
                "Find the {operation} of {expression}",
                "Differentiate {expression}",
                "Integrate {expression}",
            ],
            'CODE': [
                "Write a {language} function to {task}",
                "Create a {language} script for {task}",
                "Show me {language} code to {task}",
                "How do I {task} in {language}?",
                "Generate {language} code for {task}",
                "Help me write {language} to {task}",
            ],
            'FETCH': [
                "What's the weather in {location}?",
                "Get me the weather for {location}",
                "How's the weather in {location}?",
                "Tell me the weather in {location}",
                "What's the news about {topic}?",
                "Get me news on {topic}",
                "Search for {query}",
                "Look up {query}",
            ],
            'CONVERSATIONAL': [
                "Hello",
                "Hi there",
                "Good morning",
                "How are you?",
                "What's up?",
                "Thanks",
                "Thank you",
                "Goodbye",
                "See you later",
                "That's great",
                "Awesome",
                "I see",
            ]
        }
    
    def generate_question_examples(self, count: int = 100) -> List[Dict]:
        """Generate QUESTION intent examples."""
        examples = []
        
        topics = [
            "Python", "machine learning", "quantum computing",
            "climate change", "artificial intelligence", "blockchain",
            "renewable energy", "space exploration", "genetics",
            "neural networks", "cloud computing", "cybersecurity"
        ]
        
        templates = self.templates['QUESTION']
        
        for _ in range(count):
            template = random.choice(templates)
            topic = random.choice(topics)
            query = template.format(topic=topic)
            
            examples.append({
                'query': query,
                'intent': 'QUESTION',
                'confidence': 1.0,
                'metadata': {'generated': True, 'topic': topic}
            })
        
        return examples
    
    def generate_command_examples(self, count: int = 100) -> List[Dict]:
        """Generate COMMAND intent examples."""
        examples = []
        
        apps = [
            "Chrome", "Firefox", "Notepad", "Calculator",
            "Word", "Excel", "PowerPoint", "Outlook",
            "Spotify", "Discord", "Slack", "Teams",
            "VS Code", "PyCharm", "Terminal", "File Explorer"
        ]
        
        templates = self.templates['COMMAND']
        
        for _ in range(count):
            template = random.choice(templates)
            app = random.choice(apps)
            query = template.format(app=app)
            
            examples.append({
                'query': query,
                'intent': 'COMMAND',
                'confidence': 1.0,
                'metadata': {'generated': True, 'app': app}
            })
        
        return examples
    
    def generate_math_examples(self, count: int = 100) -> List[Dict]:
        """Generate MATH intent examples."""
        examples = []
        
        operations = ['+', '-', '*', '/', '^']
        op_names = {
            '+': 'sum', '-': 'difference', '*': 'product',
            '/': 'quotient', '^': 'power'
        }
        
        # Basic arithmetic
        for _ in range(count // 2):
            template = random.choice(self.templates['MATH'][:6])
            num1 = random.randint(1, 100)
            num2 = random.randint(1, 100)
            op = random.choice(operations)
            
            query = template.format(num1=num1, num2=num2, op=op)
            
            examples.append({
                'query': query,
                'intent': 'MATH',
                'confidence': 1.0,
                'metadata': {
                    'generated': True,
                    'operation': op_names.get(op, op)
                }
            })
        
        # Calculus
        expressions = [
            "x^2 + 3x", "sin(x)", "e^x", "ln(x)",
            "x^3 - 2x^2 + x", "cos(x) + sin(x)"
        ]
        
        for _ in range(count // 2):
            template = random.choice(self.templates['MATH'][6:])
            expression = random.choice(expressions)
            operation = random.choice(['derivative', 'integral', 'limit'])
            
            query = template.format(
                expression=expression,
                operation=operation
            )
            
            examples.append({
                'query': query,
                'intent': 'MATH',
                'confidence': 1.0,
                'metadata': {
                    'generated': True,
                    'operation': operation,
                    'expression': expression
                }
            })
        
        return examples
    
    def generate_code_examples(self, count: int = 100) -> List[Dict]:
        """Generate CODE intent examples."""
        examples = []
        
        languages = ['Python', 'JavaScript', 'Java', 'C++', 'Go', 'Rust']
        tasks = [
            "sort a list", "reverse a string", "find prime numbers",
            "read a file", "make an HTTP request", "parse JSON",
            "connect to a database", "create a class", "handle errors",
            "write to a file", "calculate factorial", "implement binary search"
        ]
        
        templates = self.templates['CODE']
        
        for _ in range(count):
            template = random.choice(templates)
            language = random.choice(languages)
            task = random.choice(tasks)
            
            query = template.format(language=language, task=task)
            
            examples.append({
                'query': query,
                'intent': 'CODE',
                'confidence': 1.0,
                'metadata': {
                    'generated': True,
                    'language': language,
                    'task': task
                }
            })
        
        return examples
    
    def generate_fetch_examples(self, count: int = 100) -> List[Dict]:
        """Generate FETCH intent examples."""
        examples = []
        
        locations = [
            "London", "New York", "Tokyo", "Paris", "Sydney",
            "Berlin", "Toronto", "Mumbai", "Singapore", "Dubai"
        ]
        
        topics = [
            "technology", "politics", "sports", "science",
            "entertainment", "business", "health", "climate"
        ]
        
        templates = self.templates['FETCH']
        
        for _ in range(count):
            template = random.choice(templates)
            
            if '{location}' in template:
                location = random.choice(locations)
                query = template.format(location=location)
                metadata = {'generated': True, 'location': location}
            elif '{topic}' in template:
                topic = random.choice(topics)
                query = template.format(topic=topic)
                metadata = {'generated': True, 'topic': topic}
            else:
                query_text = random.choice([
                    "Python tutorials", "best restaurants nearby",
                    "latest iPhone", "machine learning courses"
                ])
                query = template.format(query=query_text)
                metadata = {'generated': True, 'query': query_text}
            
            examples.append({
                'query': query,
                'intent': 'FETCH',
                'confidence': 1.0,
                'metadata': metadata
            })
        
        return examples
    
    def generate_conversational_examples(self, count: int = 50) -> List[Dict]:
        """Generate CONVERSATIONAL intent examples."""
        examples = []
        
        # Use templates directly (they're already complete phrases)
        templates = self.templates['CONVERSATIONAL']
        
        # Generate variations
        variations = {
            "Hello": ["Hey", "Hi", "Greetings", "Hello there"],
            "How are you?": ["How's it going?", "How are you doing?", "What's up?"],
            "Thanks": ["Thank you", "Thanks a lot", "Much appreciated", "Cheers"],
            "Goodbye": ["Bye", "See you", "Later", "Take care"]
        }
        
        for _ in range(count):
            base = random.choice(templates)
            
            # Add variations
            if base in variations:
                query = random.choice([base] + variations[base])
            else:
                query = base
            
            examples.append({
                'query': query,
                'intent': 'CONVERSATIONAL',
                'confidence': 1.0,
                'metadata': {'generated': True}
            })
        
        return examples
    
    def generate_all(self, examples_per_intent: int = 100) -> List[Dict]:
        """Generate examples for all intent categories."""
        print(f"Generating {examples_per_intent} examples per intent...")
        
        all_examples = []
        
        # Generate for each intent
        all_examples.extend(self.generate_question_examples(examples_per_intent))
        print(f"✓ Generated {examples_per_intent} QUESTION examples")
        
        all_examples.extend(self.generate_command_examples(examples_per_intent))
        print(f"✓ Generated {examples_per_intent} COMMAND examples")
        
        all_examples.extend(self.generate_math_examples(examples_per_intent))
        print(f"✓ Generated {examples_per_intent} MATH examples")
        
        all_examples.extend(self.generate_code_examples(examples_per_intent))
        print(f"✓ Generated {examples_per_intent} CODE examples")
        
        all_examples.extend(self.generate_fetch_examples(examples_per_intent))
        print(f"✓ Generated {examples_per_intent} FETCH examples")
        
        all_examples.extend(self.generate_conversational_examples(examples_per_intent // 2))
        print(f"✓ Generated {examples_per_intent // 2} CONVERSATIONAL examples")
        
        # Shuffle to mix intents
        random.shuffle(all_examples)
        
        self.generated_data = all_examples
        
        print(f"\n✓ Total: {len(all_examples)} examples generated")
        
        return all_examples
    
    def save_to_file(self, filepath: str):
        """Save generated data to JSON file."""
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_examples': len(self.generated_data),
                'generator_version': '1.0.0'
            },
            'examples': self.generated_data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Saved to {filepath}")
    
    def get_statistics(self) -> Dict:
        """Get statistics about generated data."""
        if not self.generated_data:
            return {}
        
        intent_counts = {}
        for example in self.generated_data:
            intent = example['intent']
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        return {
            'total': len(self.generated_data),
            'by_intent': intent_counts
        }


def main():
    """Main function to generate training data."""
    print("=" * 60)
    print("Training Data Generator")
    print("=" * 60)
    print()
    
    generator = TrainingDataGenerator()
    
    # Generate data
    examples_per_intent = 200  # Adjust as needed
    generator.generate_all(examples_per_intent)
    
    # Show statistics
    stats = generator.get_statistics()
    print("\nStatistics:")
    print(f"  Total examples: {stats['total']}")
    print("  By intent:")
    for intent, count in sorted(stats['by_intent'].items()):
        print(f"    {intent}: {count}")
    
    # Save to file
    output_file = 'data/training/synthetic_intents.json'
    generator.save_to_file(output_file)
    
    print("\n" + "=" * 60)
    print("✓ Generation complete!")
    print("=" * 60)
    print(f"\nNext steps:")
    print(f"1. Review the generated data in {output_file}")
    print(f"2. Add manual examples for edge cases")
    print(f"3. Run: python scripts/train_intent_classifier.py")


if __name__ == "__main__":
    main()
