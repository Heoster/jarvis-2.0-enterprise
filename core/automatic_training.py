"""
Automatic Training System for JARVIS
Learns from positive user feedback and continuously improves responses.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import pickle

from core.logger import get_logger
from core.intent_classifier_enhanced import EnhancedIntentClassifier
from core.smart_knowledge_integration import get_knowledge_integrator
from storage.contextual_memory import get_contextual_memory
from monitoring.metrics import get_metrics_collector

logger = get_logger(__name__)


class AutomaticTrainingSystem:
    """
    Automatic training system that learns from positive user interactions
    """
    
    def __init__(self, training_threshold: int = 5, auto_save_interval: int = 3600):
        """
        Initialize automatic training system
        
        Args:
            training_threshold: Number of positive feedbacks before training
            auto_save_interval: Auto-save interval in seconds
        """
        self.training_threshold = training_threshold
        self.auto_save_interval = auto_save_interval
        
        # Training data storage
        self.positive_interactions = []
        self.training_patterns = {}
        self.learned_responses = {}
        
        # Components
        self.intent_classifier = EnhancedIntentClassifier()
        self.knowledge_integrator = get_knowledge_integrator()
        self.metrics = get_metrics_collector()
        
        # Training state
        self.last_training_time = time.time()
        self.training_count = 0
        self.positive_feedback_count = 0
        
        # File paths
        self.training_data_file = Path("data/training_data.json")
        self.learned_patterns_file = Path("data/learned_patterns.pkl")
        
        # Ensure data directory exists
        self.training_data_file.parent.mkdir(exist_ok=True)
        
        # Load existing training data
        self._load_training_data()
        
        logger.info("Automatic Training System initialized")
    
    async def process_feedback(self, query: str, response: str, feedback: str, 
                              context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Process user feedback and trigger training if needed
        
        Args:
            query: Original user query
            response: JARVIS response
            feedback: User feedback
            context: Additional context
            
        Returns:
            True if training was triggered
        """
        try:
            # Analyze feedback sentiment
            is_positive = self._is_positive_feedback(feedback)
            
            if is_positive:
                # Store positive interaction
                interaction = {
                    'query': query,
                    'response': response,
                    'feedback': feedback,
                    'context': context or {},
                    'timestamp': datetime.now().isoformat(),
                    'query_length': len(query),
                    'response_length': len(response)
                }
                
                self.positive_interactions.append(interaction)
                self.positive_feedback_count += 1
                
                # Update knowledge base
                await self.knowledge_integrator.update_knowledge_from_interaction(
                    query, response, feedback
                )
                
                logger.info(f"Positive feedback recorded: {feedback[:50]}...")
                
                # Check if training threshold reached
                if self.positive_feedback_count >= self.training_threshold:
                    await self._trigger_automatic_training()
                    return True
            
            # Auto-save periodically
            if time.time() - self.last_training_time > self.auto_save_interval:
                await self._save_training_data()
            
            return False
            
        except Exception as e:
            logger.error(f"Feedback processing failed: {e}")
            return False
    
    def _is_positive_feedback(self, feedback: str) -> bool:
        """Determine if feedback is positive"""
        feedback_lower = feedback.lower()
        
        # Positive indicators
        positive_words = [
            'good', 'great', 'excellent', 'perfect', 'amazing', 'awesome',
            'helpful', 'useful', 'correct', 'right', 'yes', 'exactly',
            'thank you', 'thanks', 'appreciate', 'love it', 'brilliant',
            'fantastic', 'wonderful', 'outstanding', 'superb', 'nice',
            'cool', 'sweet', 'nice job', 'well done', 'spot on'
        ]
        
        # Negative indicators (to avoid false positives)
        negative_words = [
            'no', 'not', 'wrong', 'bad', 'terrible', 'awful', 'horrible',
            'useless', 'unhelpful', 'incorrect', 'false', 'stupid'
        ]
        
        # Check for negative words first
        if any(neg_word in feedback_lower for neg_word in negative_words):
            return False
        
        # Check for positive words
        return any(pos_word in feedback_lower for pos_word in positive_words)
    
    async def _trigger_automatic_training(self):
        """Trigger automatic training from accumulated positive feedback"""
        try:
            logger.info(f"🧠 Starting automatic training with {len(self.positive_interactions)} positive interactions")
            
            # Extract training patterns
            patterns = await self._extract_training_patterns()
            
            # Update intent classifier
            await self._update_intent_classifier(patterns)
            
            # Update response templates
            await self._update_response_templates(patterns)
            
            # Save training data
            await self._save_training_data()
            
            # Reset counters
            self.positive_feedback_count = 0
            self.training_count += 1
            self.last_training_time = time.time()
            
            # Record metrics
            self.metrics.record_feature_usage('automatic_training', {
                'training_count': self.training_count,
                'patterns_learned': len(patterns),
                'interactions_processed': len(self.positive_interactions)
            })
            
            logger.info(f"✅ Automatic training completed - learned {len(patterns)} new patterns")
            
        except Exception as e:
            logger.error(f"Automatic training failed: {e}")
    
    async def _extract_training_patterns(self) -> List[Dict[str, Any]]:
        """Extract patterns from positive interactions"""
        patterns = []
        
        # Group interactions by query similarity
        query_groups = self._group_similar_queries()
        
        for group_key, interactions in query_groups.items():
            if len(interactions) >= 2:  # Need at least 2 similar interactions
                pattern = {
                    'pattern_type': self._classify_pattern_type(interactions[0]['query']),
                    'query_pattern': group_key,
                    'successful_responses': [i['response'] for i in interactions],
                    'example_queries': [i['query'] for i in interactions],
                    'confidence': len(interactions) / len(self.positive_interactions),
                    'learned_at': datetime.now().isoformat()
                }
                patterns.append(pattern)
        
        # Extract keyword patterns
        keyword_patterns = self._extract_keyword_patterns()
        patterns.extend(keyword_patterns)
        
        return patterns
    
    def _group_similar_queries(self) -> Dict[str, List[Dict]]:
        """Group similar queries together"""
        groups = {}
        
        for interaction in self.positive_interactions:
            query = interaction['query'].lower().strip()
            
            # Simple similarity grouping based on keywords
            key_words = self._extract_key_words(query)
            group_key = '_'.join(sorted(key_words))
            
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(interaction)
        
        return groups
    
    def _extract_key_words(self, query: str) -> List[str]:
        """Extract key words from query for grouping"""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'what', 'how', 'when', 'where', 'why'
        }
        
        words = query.lower().split()
        key_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        return key_words[:3]  # Take top 3 key words
    
    def _classify_pattern_type(self, query: str) -> str:
        """Classify the type of query pattern"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['time', 'date', 'when']):
            return 'time_date'
        elif any(word in query_lower for word in ['search', 'find', 'look']):
            return 'search'
        elif any(word in query_lower for word in ['hello', 'hi', 'hey']):
            return 'greeting'
        elif any(word in query_lower for word in ['bitcoin', 'currency', 'financial']):
            return 'financial'
        elif any(word in query_lower for word in ['train', 'railway']):
            return 'railway'
        elif any(word in query_lower for word in ['joke', 'quote', 'entertainment']):
            return 'entertainment'
        elif '?' in query:
            return 'question'
        else:
            return 'general'
    
    def _extract_keyword_patterns(self) -> List[Dict[str, Any]]:
        """Extract keyword-based patterns"""
        keyword_counts = {}
        
        # Count keyword frequencies in positive interactions
        for interaction in self.positive_interactions:
            words = interaction['query'].lower().split()
            for word in words:
                if len(word) > 3:  # Skip short words
                    if word not in keyword_counts:
                        keyword_counts[word] = []
                    keyword_counts[word].append(interaction)
        
        # Create patterns for frequently occurring keywords
        patterns = []
        for keyword, interactions in keyword_counts.items():
            if len(interactions) >= 3:  # Keyword appears in 3+ positive interactions
                pattern = {
                    'pattern_type': 'keyword',
                    'keyword': keyword,
                    'frequency': len(interactions),
                    'successful_responses': [i['response'] for i in interactions],
                    'confidence': len(interactions) / len(self.positive_interactions),
                    'learned_at': datetime.now().isoformat()
                }
                patterns.append(pattern)
        
        return patterns
    
    async def _update_intent_classifier(self, patterns: List[Dict[str, Any]]):
        """Update intent classifier with learned patterns"""
        try:
            # Create training data from patterns
            training_texts = []
            training_labels = []
            
            for pattern in patterns:
                if 'example_queries' in pattern:
                    for query in pattern['example_queries']:
                        training_texts.append(query)
                        training_labels.append(pattern['pattern_type'])
            
            if training_texts:
                # Add to existing training data
                existing_data = self.intent_classifier._train_default()
                
                # Combine with learned data
                all_texts = [item[0] for item in existing_data] + training_texts
                all_labels = [item[1] for item in existing_data] + training_labels
                
                # Retrain classifier
                self.intent_classifier.train(all_texts, all_labels)
                
                logger.info(f"Updated intent classifier with {len(training_texts)} learned examples")
            
        except Exception as e:
            logger.error(f"Intent classifier update failed: {e}")
    
    async def _update_response_templates(self, patterns: List[Dict[str, Any]]):
        """Update response templates with learned patterns"""
        try:
            for pattern in patterns:
                # Store learned response patterns
                pattern_key = f"{pattern['pattern_type']}_{pattern.get('keyword', 'general')}"
                
                if pattern_key not in self.learned_responses:
                    self.learned_responses[pattern_key] = []
                
                # Add successful responses as templates
                for response in pattern['successful_responses']:
                    if response not in self.learned_responses[pattern_key]:
                        self.learned_responses[pattern_key].append(response)
            
            logger.info(f"Updated response templates with {len(patterns)} patterns")
            
        except Exception as e:
            logger.error(f"Response template update failed: {e}")
    
    async def get_learned_response(self, query: str, pattern_type: str) -> Optional[str]:
        """Get learned response for a query pattern"""
        try:
            # Extract keywords from query
            keywords = self._extract_key_words(query)
            
            # Try to find matching learned response
            for keyword in keywords:
                pattern_key = f"{pattern_type}_{keyword}"
                if pattern_key in self.learned_responses:
                    responses = self.learned_responses[pattern_key]
                    if responses:
                        import random
                        return random.choice(responses)
            
            # Try general pattern
            general_key = f"{pattern_type}_general"
            if general_key in self.learned_responses:
                responses = self.learned_responses[general_key]
                if responses:
                    import random
                    return random.choice(responses)
            
            return None
            
        except Exception as e:
            logger.error(f"Learned response retrieval failed: {e}")
            return None
    
    async def _save_training_data(self):
        """Save training data to files"""
        try:
            # Save positive interactions as JSON
            training_data = {
                'positive_interactions': self.positive_interactions,
                'training_count': self.training_count,
                'last_training_time': self.last_training_time,
                'positive_feedback_count': self.positive_feedback_count,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.training_data_file, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, indent=2, ensure_ascii=False)
            
            # Save learned patterns as pickle
            patterns_data = {
                'training_patterns': self.training_patterns,
                'learned_responses': self.learned_responses
            }
            
            with open(self.learned_patterns_file, 'wb') as f:
                pickle.dump(patterns_data, f)
            
            logger.info("Training data saved successfully")
            
        except Exception as e:
            logger.error(f"Training data save failed: {e}")
    
    def _load_training_data(self):
        """Load existing training data"""
        try:
            # Load JSON training data
            if self.training_data_file.exists():
                with open(self.training_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.positive_interactions = data.get('positive_interactions', [])
                self.training_count = data.get('training_count', 0)
                self.last_training_time = data.get('last_training_time', time.time())
                self.positive_feedback_count = data.get('positive_feedback_count', 0)
                
                logger.info(f"Loaded {len(self.positive_interactions)} positive interactions")
            
            # Load pickle patterns data
            if self.learned_patterns_file.exists():
                with open(self.learned_patterns_file, 'rb') as f:
                    data = pickle.load(f)
                
                self.training_patterns = data.get('training_patterns', {})
                self.learned_responses = data.get('learned_responses', {})
                
                logger.info(f"Loaded {len(self.learned_responses)} learned response patterns")
            
        except Exception as e:
            logger.error(f"Training data load failed: {e}")
    
    def get_training_statistics(self) -> Dict[str, Any]:
        """Get training system statistics"""
        return {
            'training_count': self.training_count,
            'positive_interactions': len(self.positive_interactions),
            'positive_feedback_count': self.positive_feedback_count,
            'learned_patterns': len(self.training_patterns),
            'learned_responses': len(self.learned_responses),
            'last_training_time': datetime.fromtimestamp(self.last_training_time).isoformat(),
            'training_threshold': self.training_threshold,
            'auto_save_interval': self.auto_save_interval
        }
    
    async def export_training_data(self, format: str = 'json') -> str:
        """Export training data for analysis"""
        try:
            export_data = {
                'metadata': {
                    'exported_at': datetime.now().isoformat(),
                    'total_interactions': len(self.positive_interactions),
                    'training_count': self.training_count
                },
                'positive_interactions': self.positive_interactions,
                'learned_patterns': self.training_patterns,
                'learned_responses': self.learned_responses,
                'statistics': self.get_training_statistics()
            }
            
            if format == 'json':
                export_file = Path(f"data/training_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                return str(export_file)
            
        except Exception as e:
            logger.error(f"Training data export failed: {e}")
            return ""


# Global instance
_training_system = None

def get_training_system() -> AutomaticTrainingSystem:
    """Get or create training system instance"""
    global _training_system
    if _training_system is None:
        _training_system = AutomaticTrainingSystem()
    return _training_system