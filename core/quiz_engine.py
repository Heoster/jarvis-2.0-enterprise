"""
Quiz and Assessment Engine
Generates interactive quizzes for students
"""

import random
from typing import Dict, List, Optional
from datetime import datetime
from core.logger import get_logger

logger = get_logger(__name__)


class QuizEngine:
    """Interactive quiz generation and management"""
    
    def __init__(self):
        self.active_quizzes = {}
        self.quiz_history = []
        
        # Sample quiz database (expandable)
        self.quiz_bank = {
            'python': [
                {
                    'question': 'What is the correct way to create a list in Python?',
                    'options': ['list = []', 'list = ()', 'list = {}', 'list = <>'],
                    'correct': 0,
                    'difficulty': 'easy',
                    'explanation': 'Square brackets [] are used to create lists in Python.'
                },
                {
                    'question': 'Which keyword is used to define a function in Python?',
                    'options': ['function', 'def', 'func', 'define'],
                    'correct': 1,
                    'difficulty': 'easy',
                    'explanation': 'The "def" keyword is used to define functions in Python.'
                },
                {
                    'question': 'What does the len() function do?',
                    'options': ['Returns length', 'Returns type', 'Returns value', 'Returns index'],
                    'correct': 0,
                    'difficulty': 'easy',
                    'explanation': 'len() returns the number of items in an object.'
                }
            ],
            'math': [
                {
                    'question': 'What is 15 × 8?',
                    'options': ['120', '125', '115', '130'],
                    'correct': 0,
                    'difficulty': 'easy',
                    'explanation': '15 × 8 = 120'
                },
                {
                    'question': 'What is the square root of 144?',
                    'options': ['10', '11', '12', '13'],
                    'correct': 2,
                    'difficulty': 'medium',
                    'explanation': '√144 = 12 because 12 × 12 = 144'
                }
            ],
            'minecraft': [
                {
                    'question': 'What is the main programming language for Minecraft mods?',
                    'options': ['Python', 'Java', 'C++', 'JavaScript'],
                    'correct': 1,
                    'difficulty': 'easy',
                    'explanation': 'Minecraft Java Edition mods are written in Java.'
                },
                {
                    'question': 'Which tool is commonly used for Minecraft modding?',
                    'options': ['Unity', 'Forge', 'Unreal', 'Godot'],
                    'correct': 1,
                    'difficulty': 'medium',
                    'explanation': 'Minecraft Forge is the most popular modding framework.'
                }
            ]
        }
    
    def generate_quiz(self, topic: str, num_questions: int = 5, 
                     difficulty: Optional[str] = None) -> Dict:
        """
        Generate a quiz on a specific topic
        
        Args:
            topic: Quiz topic (python, math, minecraft, etc.)
            num_questions: Number of questions
            difficulty: Filter by difficulty (easy, medium, hard)
        
        Returns:
            Quiz dictionary
        """
        topic_lower = topic.lower()
        
        # Get questions for topic
        if topic_lower not in self.quiz_bank:
            # Generate generic quiz
            questions = self._generate_generic_quiz(topic, num_questions)
        else:
            questions = self.quiz_bank[topic_lower].copy()
            
            # Filter by difficulty if specified
            if difficulty:
                questions = [q for q in questions if q['difficulty'] == difficulty]
            
            # Shuffle and limit
            random.shuffle(questions)
            questions = questions[:num_questions]
        
        # Create quiz
        quiz_id = f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        quiz = {
            'id': quiz_id,
            'topic': topic,
            'questions': questions,
            'current_question': 0,
            'score': 0,
            'answers': [],
            'started_at': datetime.now().isoformat(),
            'completed': False
        }
        
        self.active_quizzes[quiz_id] = quiz
        logger.info(f"Generated quiz {quiz_id} on {topic} with {len(questions)} questions")
        
        return quiz
    
    def _generate_generic_quiz(self, topic: str, num_questions: int) -> List[Dict]:
        """Generate generic quiz questions for unknown topics"""
        # Placeholder - in production, use AI to generate questions
        return [
            {
                'question': f'Sample question about {topic}?',
                'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                'correct': 0,
                'difficulty': 'medium',
                'explanation': f'This is a sample question about {topic}.'
            }
        ] * num_questions
    
    def get_current_question(self, quiz_id: str) -> Optional[Dict]:
        """Get current question for a quiz"""
        quiz = self.active_quizzes.get(quiz_id)
        if not quiz or quiz['completed']:
            return None
        
        idx = quiz['current_question']
        if idx >= len(quiz['questions']):
            return None
        
        question = quiz['questions'][idx].copy()
        question['number'] = idx + 1
        question['total'] = len(quiz['questions'])
        
        return question
    
    def submit_answer(self, quiz_id: str, answer: int) -> Dict:
        """
        Submit answer for current question
        
        Args:
            quiz_id: Quiz identifier
            answer: Answer index (0-based)
        
        Returns:
            Result dictionary
        """
        quiz = self.active_quizzes.get(quiz_id)
        if not quiz or quiz['completed']:
            return {'error': 'Quiz not found or already completed'}
        
        idx = quiz['current_question']
        if idx >= len(quiz['questions']):
            return {'error': 'No more questions'}
        
        question = quiz['questions'][idx]
        correct = answer == question['correct']
        
        # Record answer
        quiz['answers'].append({
            'question_idx': idx,
            'answer': answer,
            'correct': correct,
            'timestamp': datetime.now().isoformat()
        })
        
        if correct:
            quiz['score'] += 1
        
        # Move to next question
        quiz['current_question'] += 1
        
        # Check if quiz is complete
        if quiz['current_question'] >= len(quiz['questions']):
            quiz['completed'] = True
            quiz['completed_at'] = datetime.now().isoformat()
            self.quiz_history.append(quiz)
        
        result = {
            'correct': correct,
            'explanation': question['explanation'],
            'correct_answer': question['options'][question['correct']],
            'your_answer': question['options'][answer],
            'score': quiz['score'],
            'total': len(quiz['questions']),
            'completed': quiz['completed']
        }
        
        return result
    
    def get_quiz_results(self, quiz_id: str) -> Optional[Dict]:
        """Get final results for a completed quiz"""
        quiz = self.active_quizzes.get(quiz_id)
        if not quiz:
            return None
        
        total = len(quiz['questions'])
        score = quiz['score']
        percentage = (score / total * 100) if total > 0 else 0
        
        # Determine grade
        if percentage >= 90:
            grade = 'A'
            message = 'Outstanding! You\'re a star! 🌟'
        elif percentage >= 80:
            grade = 'B'
            message = 'Great job! Keep it up! 🎉'
        elif percentage >= 70:
            grade = 'C'
            message = 'Good effort! Practice makes perfect! 💪'
        elif percentage >= 60:
            grade = 'D'
            message = 'You can do better! Keep learning! 📚'
        else:
            grade = 'F'
            message = 'Don\'t give up! Review and try again! ✨'
        
        return {
            'quiz_id': quiz_id,
            'topic': quiz['topic'],
            'score': score,
            'total': total,
            'percentage': round(percentage, 1),
            'grade': grade,
            'message': message,
            'answers': quiz['answers'],
            'completed_at': quiz.get('completed_at')
        }
    
    def add_question(self, topic: str, question_data: Dict):
        """Add a new question to the quiz bank"""
        topic_lower = topic.lower()
        if topic_lower not in self.quiz_bank:
            self.quiz_bank[topic_lower] = []
        
        self.quiz_bank[topic_lower].append(question_data)
        logger.info(f"Added question to {topic} quiz bank")
    
    def get_topics(self) -> List[str]:
        """Get list of available quiz topics"""
        return list(self.quiz_bank.keys())
    
    def get_quiz_stats(self) -> Dict:
        """Get overall quiz statistics"""
        total_quizzes = len(self.quiz_history)
        if total_quizzes == 0:
            return {
                'total_quizzes': 0,
                'average_score': 0,
                'topics_covered': []
            }
        
        total_score = sum(q['score'] for q in self.quiz_history)
        total_questions = sum(len(q['questions']) for q in self.quiz_history)
        
        topics = list(set(q['topic'] for q in self.quiz_history))
        
        return {
            'total_quizzes': total_quizzes,
            'total_questions_answered': total_questions,
            'average_score': round(total_score / total_questions * 100, 1) if total_questions > 0 else 0,
            'topics_covered': topics
        }


# Singleton instance
_quiz_engine_instance = None

def get_quiz_engine() -> QuizEngine:
    """Get or create quiz engine instance"""
    global _quiz_engine_instance
    if _quiz_engine_instance is None:
        _quiz_engine_instance = QuizEngine()
    return _quiz_engine_instance
