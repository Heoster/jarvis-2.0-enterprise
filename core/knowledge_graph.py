"""Knowledge Graph for concept tracking and learning path visualization."""

import networkx as nx
from typing import Dict, Any, List, Optional, Set, Tuple
import json
from pathlib import Path

from core.logger import get_logger

logger = get_logger(__name__)


class KnowledgeGraph:
    """
    Tracks concepts and their relationships for learning path visualization.
    Uses NetworkX for graph operations.
    """
    
    def __init__(self, student_id: Optional[str] = None):
        self.student_id = student_id or "default"
        self.graph = nx.DiGraph()
        self.concept_metadata = {}
        self._load_graph()
        self._initialize_base_concepts()
    
    def _load_graph(self):
        """Load existing knowledge graph."""
        graph_path = Path(f"data/knowledge_graphs/{self.student_id}_graph.json")
        
        if graph_path.exists():
            try:
                with open(graph_path, 'r') as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data['graph'])
                    self.concept_metadata = data.get('metadata', {})
                logger.info(f"Loaded knowledge graph for {self.student_id}")
            except Exception as e:
                logger.error(f"Failed to load knowledge graph: {e}")
    
    def _initialize_base_concepts(self):
        """Initialize base programming concepts if graph is empty."""
        if self.graph.number_of_nodes() == 0:
            base_concepts = {
                # Python basics
                'variables': {'category': 'basics', 'difficulty': 1},
                'data_types': {'category': 'basics', 'difficulty': 1},
                'operators': {'category': 'basics', 'difficulty': 1},
                'conditionals': {'category': 'control_flow', 'difficulty': 2},
                'loops': {'category': 'control_flow', 'difficulty': 2},
                'functions': {'category': 'functions', 'difficulty': 3},
                'lists': {'category': 'data_structures', 'difficulty': 2},
                'dictionaries': {'category': 'data_structures', 'difficulty': 3},
                'classes': {'category': 'oop', 'difficulty': 4},
                'inheritance': {'category': 'oop', 'difficulty': 5},
                'file_io': {'category': 'advanced', 'difficulty': 4},
                'exceptions': {'category': 'advanced', 'difficulty': 4},
                
                # Minecraft modding
                'minecraft_basics': {'category': 'minecraft', 'difficulty': 1},
                'forge_setup': {'category': 'minecraft', 'difficulty': 2},
                'blocks': {'category': 'minecraft', 'difficulty': 3},
                'items': {'category': 'minecraft', 'difficulty': 3},
                'entities': {'category': 'minecraft', 'difficulty': 4},
                'events': {'category': 'minecraft', 'difficulty': 4},
            }
            
            for concept, attrs in base_concepts.items():
                self.add_concept(concept, **attrs)
            
            # Add prerequisite relationships
            prerequisites = [
                ('data_types', 'variables'),
                ('conditionals', 'operators'),
                ('loops', 'conditionals'),
                ('functions', 'variables'),
                ('lists', 'data_types'),
                ('dictionaries', 'lists'),
                ('classes', 'functions'),
                ('inheritance', 'classes'),
                ('file_io', 'functions'),
                ('exceptions', 'functions'),
                ('forge_setup', 'minecraft_basics'),
                ('blocks', 'forge_setup'),
                ('items', 'forge_setup'),
                ('entities', 'classes'),
                ('events', 'functions'),
            ]
            
            for concept, prereq in prerequisites:
                self.add_prerequisite(concept, prereq)
    
    def add_concept(
        self,
        concept: str,
        category: str = 'general',
        difficulty: int = 1,
        **kwargs
    ):
        """Add a concept to the knowledge graph."""
        self.graph.add_node(
            concept,
            category=category,
            difficulty=difficulty,
            mastered=False,
            attempts=0,
            last_studied=None,
            **kwargs
        )
        
        self.concept_metadata[concept] = {
            'category': category,
            'difficulty': difficulty,
            'added_at': str(Path(__file__).stat().st_mtime)
        }
        
        logger.info(f"Added concept: {concept}")
    
    def add_prerequisite(self, concept: str, prerequisite: str):
        """Add prerequisite relationship."""
        if concept not in self.graph:
            self.add_concept(concept)
        if prerequisite not in self.graph:
            self.add_concept(prerequisite)
        
        self.graph.add_edge(prerequisite, concept, relationship='prerequisite')
        logger.debug(f"Added prerequisite: {prerequisite} -> {concept}")
    
    def add_related(self, concept1: str, concept2: str, relationship: str = 'related'):
        """Add related concept relationship."""
        if concept1 not in self.graph:
            self.add_concept(concept1)
        if concept2 not in self.graph:
            self.add_concept(concept2)
        
        self.graph.add_edge(concept1, concept2, relationship=relationship)
        self.graph.add_edge(concept2, concept1, relationship=relationship)
    
    def mark_mastered(self, concept: str):
        """Mark a concept as mastered."""
        if concept in self.graph:
            self.graph.nodes[concept]['mastered'] = True
            logger.info(f"Concept mastered: {concept}")
    
    def record_attempt(self, concept: str, success: bool = True):
        """Record a learning attempt."""
        if concept in self.graph:
            self.graph.nodes[concept]['attempts'] += 1
            self.graph.nodes[concept]['last_studied'] = str(Path(__file__).stat().st_mtime)
            
            if success and self.graph.nodes[concept]['attempts'] >= 3:
                self.mark_mastered(concept)
    
    def get_learning_path(
        self,
        target_concept: str,
        current_knowledge: Optional[Set[str]] = None
    ) -> List[str]:
        """
        Generate optimal learning path to target concept.
        
        Args:
            target_concept: Concept to learn
            current_knowledge: Set of already mastered concepts
            
        Returns:
            Ordered list of concepts to learn
        """
        if target_concept not in self.graph:
            return []
        
        current_knowledge = current_knowledge or set()
        
        # Get all prerequisites using topological sort
        try:
            # Get subgraph of target and its prerequisites
            predecessors = nx.ancestors(self.graph, target_concept)
            subgraph = self.graph.subgraph(predecessors | {target_concept})
            
            # Topological sort gives learning order
            path = list(nx.topological_sort(subgraph))
            
            # Filter out already known concepts
            path = [c for c in path if c not in current_knowledge]
            
            return path
        except nx.NetworkXError:
            logger.error(f"Could not generate path for {target_concept}")
            return [target_concept]
    
    def get_next_concepts(
        self,
        mastered_concepts: Set[str],
        max_difficulty: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Get recommended next concepts to learn.
        
        Args:
            mastered_concepts: Set of mastered concepts
            max_difficulty: Maximum difficulty level
            
        Returns:
            List of (concept, readiness_score) tuples
        """
        candidates = []
        
        for concept in self.graph.nodes():
            # Skip if already mastered
            if concept in mastered_concepts:
                continue
            
            # Skip if too difficult
            difficulty = self.graph.nodes[concept].get('difficulty', 1)
            if difficulty > max_difficulty:
                continue
            
            # Check prerequisites
            prerequisites = set(self.graph.predecessors(concept))
            unmet_prereqs = prerequisites - mastered_concepts
            
            if not unmet_prereqs:
                # All prerequisites met - calculate readiness score
                score = self._calculate_readiness(concept, mastered_concepts)
                candidates.append((concept, score))
        
        # Sort by readiness score
        return sorted(candidates, key=lambda x: x[1], reverse=True)
    
    def _calculate_readiness(self, concept: str, mastered: Set[str]) -> float:
        """Calculate readiness score for a concept."""
        score = 1.0
        
        # Bonus for having all prerequisites
        prerequisites = set(self.graph.predecessors(concept))
        if prerequisites and prerequisites.issubset(mastered):
            score += 0.5
        
        # Bonus for related concepts
        related = set(self.graph.neighbors(concept))
        related_mastered = related.intersection(mastered)
        if related:
            score += 0.3 * (len(related_mastered) / len(related))
        
        # Penalty for high difficulty
        difficulty = self.graph.nodes[concept].get('difficulty', 1)
        score -= (difficulty - 1) * 0.1
        
        return max(score, 0.0)
    
    def get_concept_info(self, concept: str) -> Dict[str, Any]:
        """Get detailed information about a concept."""
        if concept not in self.graph:
            return {}
        
        node_data = self.graph.nodes[concept]
        prerequisites = list(self.graph.predecessors(concept))
        unlocks = list(self.graph.successors(concept))
        related = [n for n in self.graph.neighbors(concept) 
                  if self.graph[concept][n].get('relationship') == 'related']
        
        return {
            'concept': concept,
            'category': node_data.get('category'),
            'difficulty': node_data.get('difficulty'),
            'mastered': node_data.get('mastered', False),
            'attempts': node_data.get('attempts', 0),
            'prerequisites': prerequisites,
            'unlocks': unlocks,
            'related': related,
            'last_studied': node_data.get('last_studied')
        }
    
    def visualize_path(self, path: List[str]) -> str:
        """Create ASCII visualization of learning path."""
        if not path:
            return "No path to visualize"
        
        viz = "Learning Path:\n\n"
        for i, concept in enumerate(path, 1):
            info = self.get_concept_info(concept)
            difficulty = info.get('difficulty', 1)
            mastered = info.get('mastered', False)
            
            status = "✅" if mastered else "⭕"
            difficulty_stars = "⭐" * difficulty
            
            viz += f"{i}. {status} {concept} {difficulty_stars}\n"
            
            if i < len(path):
                viz += "   ↓\n"
        
        return viz
    
    def get_progress_summary(self, mastered: Set[str]) -> Dict[str, Any]:
        """Get learning progress summary."""
        total_concepts = self.graph.number_of_nodes()
        mastered_count = len(mastered)
        
        # Group by category
        categories = {}
        for concept in self.graph.nodes():
            category = self.graph.nodes[concept].get('category', 'general')
            if category not in categories:
                categories[category] = {'total': 0, 'mastered': 0}
            categories[category]['total'] += 1
            if concept in mastered:
                categories[category]['mastered'] += 1
        
        return {
            'total_concepts': total_concepts,
            'mastered_concepts': mastered_count,
            'progress_percentage': (mastered_count / total_concepts * 100) if total_concepts > 0 else 0,
            'categories': categories,
            'next_recommended': self.get_next_concepts(mastered, max_difficulty=5)[:3]
        }
    
    def save_graph(self):
        """Save knowledge graph to disk."""
        graph_path = Path(f"data/knowledge_graphs/{self.student_id}_graph.json")
        graph_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            data = {
                'graph': nx.node_link_data(self.graph),
                'metadata': self.concept_metadata
            }
            with open(graph_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved knowledge graph for {self.student_id}")
        except Exception as e:
            logger.error(f"Failed to save knowledge graph: {e}")
