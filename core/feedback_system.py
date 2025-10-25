"""
Feedback and Evaluation System
Collects user feedback to improve responses and fine-tuning
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from core.logger import get_logger

logger = get_logger(__name__)


class FeedbackSystem:
    """Manages user feedback and evaluation"""
    
    def __init__(self, feedback_dir: str = 'data/feedback'):
        self.feedback_dir = Path(feedback_dir)
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        
        self.feedback_file = self.feedback_dir / 'feedback.jsonl'
        self.feedback_stats = self.feedback_dir / 'stats.json'
        
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """Load feedback statistics"""
        if self.feedback_stats.exists():
            try:
                with open(self.feedback_stats, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'total_feedback': 0,
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'categories': {},
            'improvement_requests': []
        }
    
    def _save_stats(self):
        """Save feedback statistics"""
        try:
            with open(self.feedback_stats, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")
    
    def record_feedback(self, query: str, response: str, 
                       feedback_type: str, comment: Optional[str] = None,
                       category: Optional[str] = None) -> Dict:
        """
        Record user feedback
        
        Args:
            query: Original user query
            response: Assistant response
            feedback_type: 'positive', 'negative', or 'neutral'
            comment: Optional feedback comment
            category: Optional category (grammar, quiz, general, etc.)
        
        Returns:
            Feedback record
        """
        feedback = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response,
            'feedback_type': feedback_type,
            'comment': comment,
            'category': category or 'general'
        }
        
        # Save to file
        try:
            with open(self.feedback_file, 'a') as f:
                f.write(json.dumps(feedback) + '\n')
        except Exception as e:
            logger.error(f"Failed to save feedback: {e}")
        
        # Update stats
        self.stats['total_feedback'] += 1
        self.stats[feedback_type] = self.stats.get(feedback_type, 0) + 1
        
        if category:
            if category not in self.stats['categories']:
                self.stats['categories'][category] = {
                    'positive': 0, 'negative': 0, 'neutral': 0
                }
            self.stats['categories'][category][feedback_type] += 1
        
        if comment and feedback_type == 'negative':
            self.stats['improvement_requests'].append({
                'timestamp': feedback['timestamp'],
                'comment': comment,
                'category': category
            })
        
        self._save_stats()
        
        logger.info(f"Recorded {feedback_type} feedback for category {category}")
        
        return feedback
    
    def get_feedback_stats(self) -> Dict:
        """Get feedback statistics"""
        total = self.stats['total_feedback']
        if total == 0:
            return {
                **self.stats,
                'satisfaction_rate': 0.0
            }
        
        positive = self.stats.get('positive', 0)
        satisfaction_rate = (positive / total) * 100
        
        return {
            **self.stats,
            'satisfaction_rate': round(satisfaction_rate, 1)
        }
    
    def get_improvement_suggestions(self, limit: int = 10) -> List[Dict]:
        """Get recent improvement suggestions"""
        suggestions = self.stats.get('improvement_requests', [])
        return suggestions[-limit:]
    
    def get_category_performance(self, category: str) -> Dict:
        """Get performance metrics for a category"""
        if category not in self.stats['categories']:
            return {
                'category': category,
                'total': 0,
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'satisfaction_rate': 0.0
            }
        
        cat_stats = self.stats['categories'][category]
        total = sum(cat_stats.values())
        positive = cat_stats.get('positive', 0)
        
        return {
            'category': category,
            'total': total,
            **cat_stats,
            'satisfaction_rate': round((positive / total * 100) if total > 0 else 0, 1)
        }
    
    def export_training_data(self, output_file: str, 
                           feedback_filter: Optional[str] = None):
        """
        Export feedback as training data
        
        Args:
            output_file: Output file path
            feedback_filter: Filter by feedback type (positive, negative, etc.)
        """
        training_data = []
        
        try:
            with open(self.feedback_file, 'r') as f:
                for line in f:
                    feedback = json.loads(line)
                    
                    # Apply filter
                    if feedback_filter and feedback['feedback_type'] != feedback_filter:
                        continue
                    
                    # Format for training
                    training_data.append({
                        'input': feedback['query'],
                        'output': feedback['response'],
                        'quality': feedback['feedback_type'],
                        'category': feedback.get('category', 'general')
                    })
            
            # Save training data
            with open(output_file, 'w') as f:
                json.dump(training_data, f, indent=2)
            
            logger.info(f"Exported {len(training_data)} training examples to {output_file}")
            
            return len(training_data)
        
        except Exception as e:
            logger.error(f"Failed to export training data: {e}")
            return 0
    
    def get_low_performing_areas(self, threshold: float = 50.0) -> List[Dict]:
        """
        Identify areas with low satisfaction rates
        
        Args:
            threshold: Satisfaction rate threshold (%)
        
        Returns:
            List of low-performing categories
        """
        low_performing = []
        
        for category, stats in self.stats['categories'].items():
            total = sum(stats.values())
            if total < 5:  # Skip categories with too few samples
                continue
            
            positive = stats.get('positive', 0)
            satisfaction = (positive / total * 100) if total > 0 else 0
            
            if satisfaction < threshold:
                low_performing.append({
                    'category': category,
                    'satisfaction_rate': round(satisfaction, 1),
                    'total_feedback': total,
                    'needs_improvement': True
                })
        
        # Sort by satisfaction rate (lowest first)
        low_performing.sort(key=lambda x: x['satisfaction_rate'])
        
        return low_performing
    
    def generate_improvement_report(self) -> str:
        """Generate a comprehensive improvement report"""
        stats = self.get_feedback_stats()
        low_areas = self.get_low_performing_areas()
        suggestions = self.get_improvement_suggestions(5)
        
        report = "📊 **Codeex Improvement Report** 📊\n\n"
        report += f"**Overall Statistics:**\n"
        report += f"- Total Feedback: {stats['total_feedback']}\n"
        report += f"- Satisfaction Rate: {stats['satisfaction_rate']}%\n"
        report += f"- Positive: {stats.get('positive', 0)} 👍\n"
        report += f"- Negative: {stats.get('negative', 0)} 👎\n"
        report += f"- Neutral: {stats.get('neutral', 0)} 😐\n\n"
        
        if low_areas:
            report += "**Areas Needing Improvement:**\n"
            for area in low_areas:
                report += f"- {area['category']}: {area['satisfaction_rate']}% satisfaction\n"
            report += "\n"
        
        if suggestions:
            report += "**Recent Improvement Suggestions:**\n"
            for i, sug in enumerate(suggestions, 1):
                report += f"{i}. [{sug['category']}] {sug['comment']}\n"
        
        return report


# Singleton instance
_feedback_system_instance = None

def get_feedback_system() -> FeedbackSystem:
    """Get or create feedback system instance"""
    global _feedback_system_instance
    if _feedback_system_instance is None:
        _feedback_system_instance = FeedbackSystem()
    return _feedback_system_instance
