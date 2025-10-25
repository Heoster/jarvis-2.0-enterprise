"""
Knowledge Base Expander
Adds classroom-specific facts, modding guides, and troubleshooting steps
"""

from typing import Dict, List, Optional
from datetime import datetime
from core.logger import get_logger

logger = get_logger(__name__)


class KnowledgeExpander:
    """Expands knowledge base with specialized content"""
    
    def __init__(self):
        self.knowledge_base = self._initialize_knowledge()
    
    def _initialize_knowledge(self) -> Dict:
        """Initialize knowledge base with categories"""
        return {
            'minecraft_modding': {
                'getting_started': [
                    {
                        'title': 'Setting up Minecraft Forge',
                        'content': '''
                        **Step-by-Step Forge Setup:**
                        1. Download Minecraft Forge from files.minecraftforge.net
                        2. Run the installer and select "Install client"
                        3. Open Minecraft Launcher and select Forge profile
                        4. Launch game to verify installation
                        5. Mods folder will be created in .minecraft directory
                        ''',
                        'tags': ['forge', 'setup', 'beginner']
                    },
                    {
                        'title': 'Creating Your First Mod',
                        'content': '''
                        **Basic Mod Structure:**
                        1. Set up development environment (IntelliJ IDEA or Eclipse)
                        2. Create mod main class with @Mod annotation
                        3. Add mod metadata in mods.toml
                        4. Register items, blocks, or entities
                        5. Build and test in development environment
                        ''',
                        'tags': ['mod', 'creation', 'beginner']
                    }
                ],
                'common_errors': [
                    {
                        'error': 'ClassNotFoundException',
                        'solution': '''
                        **Fix:**
                        - Check mod dependencies in build.gradle
                        - Verify all required libraries are included
                        - Refresh Gradle project
                        - Rebuild mod
                        ''',
                        'tags': ['error', 'java', 'dependencies']
                    },
                    {
                        'error': 'Mod not loading',
                        'solution': '''
                        **Troubleshooting:**
                        - Check mods.toml for correct mod ID
                        - Verify Minecraft version compatibility
                        - Look for errors in latest.log
                        - Ensure mod file is in mods folder
                        ''',
                        'tags': ['error', 'loading', 'troubleshooting']
                    },
                    {
                        'error': 'Texture not showing',
                        'solution': '''
                        **Fix:**
                        - Check texture file path matches resource location
                        - Verify texture is in correct folder (assets/modid/textures/)
                        - Ensure texture file is PNG format
                        - Check for typos in texture name
                        ''',
                        'tags': ['error', 'textures', 'resources']
                    }
                ],
                'advanced_topics': [
                    {
                        'title': 'Custom Entities',
                        'content': '''
                        **Creating Custom Entities:**
                        1. Extend Entity or LivingEntity class
                        2. Register entity type
                        3. Create entity renderer
                        4. Add entity model and textures
                        5. Implement AI goals and behaviors
                        ''',
                        'tags': ['entities', 'advanced', 'ai']
                    },
                    {
                        'title': 'Data Generation',
                        'content': '''
                        **Automated Data Generation:**
                        1. Create data generator class
                        2. Implement providers (recipes, loot tables, etc.)
                        3. Run data generation task
                        4. Generated files appear in src/generated
                        5. Commit generated files to version control
                        ''',
                        'tags': ['datagen', 'advanced', 'automation']
                    }
                ]
            },
            'programming': {
                'python': [
                    {
                        'title': 'Python Basics',
                        'content': '''
                        **Essential Python Concepts:**
                        - Variables and data types
                        - Control flow (if/else, loops)
                        - Functions and modules
                        - Lists, dictionaries, sets
                        - File I/O operations
                        ''',
                        'tags': ['python', 'basics', 'beginner']
                    },
                    {
                        'title': 'Object-Oriented Programming',
                        'content': '''
                        **OOP in Python:**
                        - Classes and objects
                        - Inheritance and polymorphism
                        - Encapsulation
                        - Magic methods (__init__, __str__, etc.)
                        - Properties and decorators
                        ''',
                        'tags': ['python', 'oop', 'intermediate']
                    }
                ],
                'java': [
                    {
                        'title': 'Java Fundamentals',
                        'content': '''
                        **Core Java Concepts:**
                        - Classes and objects
                        - Inheritance and interfaces
                        - Exception handling
                        - Collections framework
                        - Streams and lambdas
                        ''',
                        'tags': ['java', 'basics', 'beginner']
                    }
                ]
            },
            'study_tips': [
                {
                    'title': 'Effective Learning Strategies',
                    'content': '''
                    **Study Smart:**
                    1. Break study sessions into 25-minute chunks (Pomodoro)
                    2. Take regular breaks
                    3. Practice active recall
                    4. Teach concepts to others
                    5. Use spaced repetition
                    ''',
                    'tags': ['study', 'productivity', 'learning']
                },
                {
                    'title': 'Debugging Mindset',
                    'content': '''
                    **How to Debug Like a Pro:**
                    1. Read error messages carefully
                    2. Isolate the problem
                    3. Check recent changes
                    4. Use print statements or debugger
                    5. Search for similar issues online
                    6. Take breaks when stuck
                    ''',
                    'tags': ['debugging', 'problem-solving', 'coding']
                }
            ],
            'homework_help': {
                'math': [
                    {
                        'title': 'Algebra Tips',
                        'content': '''
                        **Solving Equations:**
                        - Isolate the variable
                        - Perform same operation on both sides
                        - Check your answer
                        - Practice with different problems
                        ''',
                        'tags': ['math', 'algebra', 'homework']
                    }
                ],
                'science': [
                    {
                        'title': 'Scientific Method',
                        'content': '''
                        **Steps:**
                        1. Ask a question
                        2. Research background
                        3. Form hypothesis
                        4. Test with experiment
                        5. Analyze data
                        6. Draw conclusions
                        ''',
                        'tags': ['science', 'method', 'homework']
                    }
                ]
            }
        }
    
    def search_knowledge(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """
        Search knowledge base
        
        Args:
            query: Search query
            category: Optional category filter
        
        Returns:
            List of matching knowledge items
        """
        query_lower = query.lower()
        results = []
        
        # Determine which categories to search
        if category:
            categories = {category: self.knowledge_base.get(category, {})}
        else:
            categories = self.knowledge_base
        
        # Search through categories
        for cat_name, cat_data in categories.items():
            if isinstance(cat_data, dict):
                for subcat_name, items in cat_data.items():
                    for item in items:
                        # Search in title, content, and tags
                        if self._matches_query(item, query_lower):
                            results.append({
                                'category': cat_name,
                                'subcategory': subcat_name,
                                **item,
                                'relevance': self._calculate_relevance(item, query_lower)
                            })
            elif isinstance(cat_data, list):
                for item in cat_data:
                    if self._matches_query(item, query_lower):
                        results.append({
                            'category': cat_name,
                            **item,
                            'relevance': self._calculate_relevance(item, query_lower)
                        })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        
        return results
    
    def _matches_query(self, item: Dict, query: str) -> bool:
        """Check if item matches query"""
        searchable = ' '.join([
            item.get('title', ''),
            item.get('content', ''),
            item.get('error', ''),
            item.get('solution', ''),
            ' '.join(item.get('tags', []))
        ]).lower()
        
        # Check if all query words are in searchable text
        query_words = query.split()
        return all(word in searchable for word in query_words)
    
    def _calculate_relevance(self, item: Dict, query: str) -> float:
        """Calculate relevance score"""
        score = 0.0
        query_words = query.split()
        
        # Title match (highest weight)
        title = item.get('title', '').lower()
        for word in query_words:
            if word in title:
                score += 3.0
        
        # Tag match (medium weight)
        tags = [t.lower() for t in item.get('tags', [])]
        for word in query_words:
            if word in tags:
                score += 2.0
        
        # Content match (lower weight)
        content = item.get('content', '').lower()
        for word in query_words:
            if word in content:
                score += 1.0
        
        return score
    
    def get_category_list(self) -> List[str]:
        """Get list of all categories"""
        return list(self.knowledge_base.keys())
    
    def add_knowledge(self, category: str, subcategory: Optional[str], 
                     item: Dict):
        """Add new knowledge item"""
        if category not in self.knowledge_base:
            self.knowledge_base[category] = {}
        
        if subcategory:
            if subcategory not in self.knowledge_base[category]:
                self.knowledge_base[category][subcategory] = []
            self.knowledge_base[category][subcategory].append(item)
        else:
            if not isinstance(self.knowledge_base[category], list):
                self.knowledge_base[category] = []
            self.knowledge_base[category].append(item)
        
        logger.info(f"Added knowledge to {category}/{subcategory}")
    
    def get_troubleshooting_guide(self, error_type: str) -> Optional[Dict]:
        """Get troubleshooting guide for specific error"""
        # Search in common errors
        for category in self.knowledge_base.values():
            if isinstance(category, dict) and 'common_errors' in category:
                for error in category['common_errors']:
                    if error_type.lower() in error.get('error', '').lower():
                        return error
        return None
    
    def get_learning_path(self, topic: str) -> List[Dict]:
        """Get structured learning path for a topic"""
        results = self.search_knowledge(topic)
        
        # Sort by difficulty: beginner -> intermediate -> advanced
        difficulty_order = {'beginner': 0, 'intermediate': 1, 'advanced': 2}
        
        def get_difficulty(item):
            tags = item.get('tags', [])
            for tag in tags:
                if tag in difficulty_order:
                    return difficulty_order[tag]
            return 1  # Default to intermediate
        
        results.sort(key=get_difficulty)
        return results


# Singleton instance
_knowledge_expander_instance = None

def get_knowledge_expander() -> KnowledgeExpander:
    """Get or create knowledge expander instance"""
    global _knowledge_expander_instance
    if _knowledge_expander_instance is None:
        _knowledge_expander_instance = KnowledgeExpander()
    return _knowledge_expander_instance
