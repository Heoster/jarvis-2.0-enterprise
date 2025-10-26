"""
Metrics collection system for Jarvis AI.
Tracks performance, usage, and system health metrics.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics

from core.logger import get_logger
from core.constants import FeatureFlags

logger = get_logger(__name__)


class MetricsCollector:
    """
    Collects and aggregates metrics for Jarvis AI system.
    Provides insights into performance, usage patterns, and system health.
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize metrics collector.
        
        Args:
            max_history: Maximum number of historical entries to keep
        """
        self.max_history = max_history
        self.enabled = FeatureFlags.ENABLE_METRICS
        
        # Performance metrics
        self.query_times = deque(maxlen=max_history)
        self.response_times = deque(maxlen=max_history)
        self.intent_confidences = deque(maxlen=max_history)
        
        # Usage metrics
        self.query_counts = defaultdict(int)
        self.intent_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.feature_usage = defaultdict(int)
        
        # System metrics
        self.cache_stats = {}
        self.memory_usage = deque(maxlen=100)
        
        # Session metrics
        self.session_data = {}
        self.active_sessions = set()
        
        # Start time for uptime calculation
        self.start_time = time.time()
        
        logger.info("Metrics collector initialized" + (" (disabled)" if not self.enabled else ""))
    
    def record_query_time(self, query_time: float, query: str = ""):
        """
        Record query processing time.
        
        Args:
            query_time: Time taken to process query in seconds
            query: Optional query text for analysis
        """
        if not self.enabled:
            return
        
        self.query_times.append({
            'time': query_time,
            'timestamp': time.time(),
            'query_length': len(query) if query else 0
        })
    
    def record_response_time(self, response_time: float, response_length: int = 0):
        """
        Record response generation time.
        
        Args:
            response_time: Time taken to generate response
            response_length: Length of generated response
        """
        if not self.enabled:
            return
        
        self.response_times.append({
            'time': response_time,
            'timestamp': time.time(),
            'response_length': response_length
        })
    
    def record_intent_confidence(self, intent: str, confidence: float):
        """
        Record intent classification confidence.
        
        Args:
            intent: Classified intent
            confidence: Confidence score (0-1)
        """
        if not self.enabled:
            return
        
        self.intent_confidences.append({
            'intent': intent,
            'confidence': confidence,
            'timestamp': time.time()
        })
        
        self.intent_counts[intent] += 1
    
    def record_query(self, query: str, intent: str = "unknown"):
        """
        Record query for usage analysis.
        
        Args:
            query: User query
            intent: Classified intent
        """
        if not self.enabled:
            return
        
        # Categorize query by length
        query_length = len(query)
        if query_length < 10:
            category = "short"
        elif query_length < 50:
            category = "medium"
        else:
            category = "long"
        
        self.query_counts[category] += 1
        self.query_counts['total'] += 1
    
    def record_error(self, error_type: str, component: str = "unknown"):
        """
        Record error occurrence.
        
        Args:
            error_type: Type of error
            component: Component where error occurred
        """
        if not self.enabled:
            return
        
        error_key = f"{component}:{error_type}"
        self.error_counts[error_key] += 1
        self.error_counts['total'] += 1
    
    def record_feature_usage(self, feature: str, usage_data: Optional[Dict] = None):
        """
        Record feature usage.
        
        Args:
            feature: Feature name
            usage_data: Optional usage metadata
        """
        if not self.enabled:
            return
        
        self.feature_usage[feature] += 1
        
        # Store detailed usage data if provided
        if usage_data:
            feature_key = f"{feature}_details"
            if feature_key not in self.feature_usage:
                self.feature_usage[feature_key] = []
            self.feature_usage[feature_key].append({
                'timestamp': time.time(),
                'data': usage_data
            })
    
    def start_session(self, session_id: str, metadata: Optional[Dict] = None):
        """
        Start tracking a session.
        
        Args:
            session_id: Unique session identifier
            metadata: Optional session metadata
        """
        if not self.enabled:
            return
        
        self.active_sessions.add(session_id)
        self.session_data[session_id] = {
            'start_time': time.time(),
            'queries': 0,
            'intents': defaultdict(int),
            'metadata': metadata or {}
        }
    
    def end_session(self, session_id: str):
        """
        End session tracking.
        
        Args:
            session_id: Session identifier
        """
        if not self.enabled:
            return
        
        if session_id in self.active_sessions:
            self.active_sessions.remove(session_id)
            
            if session_id in self.session_data:
                session = self.session_data[session_id]
                session['end_time'] = time.time()
                session['duration'] = session['end_time'] - session['start_time']
    
    def record_session_activity(self, session_id: str, intent: str):
        """
        Record activity in a session.
        
        Args:
            session_id: Session identifier
            intent: Intent for this activity
        """
        if not self.enabled:
            return
        
        if session_id in self.session_data:
            session = self.session_data[session_id]
            session['queries'] += 1
            session['intents'][intent] += 1
    
    def update_cache_stats(self, cache_stats: Dict[str, Any]):
        """
        Update cache statistics.
        
        Args:
            cache_stats: Cache statistics dictionary
        """
        if not self.enabled:
            return
        
        self.cache_stats = {
            **cache_stats,
            'timestamp': time.time()
        }
    
    def record_memory_usage(self, memory_mb: float):
        """
        Record memory usage.
        
        Args:
            memory_mb: Memory usage in MB
        """
        if not self.enabled:
            return
        
        self.memory_usage.append({
            'memory_mb': memory_mb,
            'timestamp': time.time()
        })
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance metrics summary.
        
        Returns:
            Performance summary dictionary
        """
        if not self.enabled or not self.query_times:
            return {'enabled': False}
        
        # Calculate query time statistics
        query_times = [entry['time'] for entry in self.query_times]
        
        performance = {
            'query_times': {
                'count': len(query_times),
                'avg': statistics.mean(query_times),
                'median': statistics.median(query_times),
                'min': min(query_times),
                'max': max(query_times),
                'p95': self._percentile(query_times, 95),
                'p99': self._percentile(query_times, 99)
            }
        }
        
        # Response time statistics
        if self.response_times:
            response_times = [entry['time'] for entry in self.response_times]
            performance['response_times'] = {
                'count': len(response_times),
                'avg': statistics.mean(response_times),
                'median': statistics.median(response_times),
                'min': min(response_times),
                'max': max(response_times)
            }
        
        # Intent confidence statistics
        if self.intent_confidences:
            confidences = [entry['confidence'] for entry in self.intent_confidences]
            performance['intent_confidence'] = {
                'count': len(confidences),
                'avg': statistics.mean(confidences),
                'median': statistics.median(confidences),
                'min': min(confidences),
                'max': max(confidences)
            }
        
        return performance
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """
        Get usage metrics summary.
        
        Returns:
            Usage summary dictionary
        """
        if not self.enabled:
            return {'enabled': False}
        
        return {
            'queries': dict(self.query_counts),
            'intents': dict(self.intent_counts),
            'features': dict(self.feature_usage),
            'errors': dict(self.error_counts),
            'active_sessions': len(self.active_sessions),
            'total_sessions': len(self.session_data)
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get system health metrics.
        
        Returns:
            System health dictionary
        """
        if not self.enabled:
            return {'enabled': False}
        
        uptime = time.time() - self.start_time
        
        health = {
            'uptime_seconds': uptime,
            'uptime_formatted': self._format_duration(uptime),
            'cache_stats': self.cache_stats,
            'error_rate': self._calculate_error_rate(),
            'avg_confidence': self._calculate_avg_confidence()
        }
        
        # Memory usage if available
        if self.memory_usage:
            recent_memory = [entry['memory_mb'] for entry in list(self.memory_usage)[-10:]]
            health['memory'] = {
                'current_mb': recent_memory[-1] if recent_memory else 0,
                'avg_mb': statistics.mean(recent_memory),
                'trend': self._calculate_trend(recent_memory)
            }
        
        return health
    
    def get_session_analytics(self) -> Dict[str, Any]:
        """
        Get session analytics.
        
        Returns:
            Session analytics dictionary
        """
        if not self.enabled:
            return {'enabled': False}
        
        completed_sessions = [
            session for session in self.session_data.values()
            if 'duration' in session
        ]
        
        if not completed_sessions:
            return {'no_completed_sessions': True}
        
        durations = [session['duration'] for session in completed_sessions]
        query_counts = [session['queries'] for session in completed_sessions]
        
        return {
            'total_sessions': len(self.session_data),
            'completed_sessions': len(completed_sessions),
            'active_sessions': len(self.active_sessions),
            'avg_duration': statistics.mean(durations),
            'avg_queries_per_session': statistics.mean(query_counts),
            'longest_session': max(durations),
            'most_active_session': max(query_counts)
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _calculate_error_rate(self) -> float:
        """Calculate overall error rate"""
        total_errors = self.error_counts.get('total', 0)
        total_queries = self.query_counts.get('total', 0)
        
        if total_queries == 0:
            return 0.0
        
        return total_errors / total_queries
    
    def _calculate_avg_confidence(self) -> float:
        """Calculate average intent confidence"""
        if not self.intent_confidences:
            return 0.0
        
        confidences = [entry['confidence'] for entry in self.intent_confidences]
        return statistics.mean(confidences)
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return 'stable'
        
        # Simple trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        if second_avg > first_avg * 1.1:
            return 'increasing'
        elif second_avg < first_avg * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        duration = timedelta(seconds=int(seconds))
        return str(duration)
    
    def export_metrics(self) -> Dict[str, Any]:
        """
        Export all metrics for analysis.
        
        Returns:
            Complete metrics dictionary
        """
        if not self.enabled:
            return {'enabled': False}
        
        return {
            'performance': self.get_performance_summary(),
            'usage': self.get_usage_summary(),
            'system_health': self.get_system_health(),
            'session_analytics': self.get_session_analytics(),
            'export_timestamp': datetime.now().isoformat()
        }
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)"""
        if not self.enabled:
            return
        
        self.query_times.clear()
        self.response_times.clear()
        self.intent_confidences.clear()
        self.query_counts.clear()
        self.intent_counts.clear()
        self.error_counts.clear()
        self.feature_usage.clear()
        self.session_data.clear()
        self.active_sessions.clear()
        self.memory_usage.clear()
        
        self.start_time = time.time()
        
        logger.info("Metrics reset")


# Global metrics collector
_metrics_collector = None

def get_metrics_collector() -> MetricsCollector:
    """Get or create global metrics collector"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector