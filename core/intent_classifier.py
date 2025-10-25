"""Intent classification for user inputs."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import asyncio

from core.models import Intent, IntentCategory
from core.text_utils import normalize_text, is_question, is_command, extract_numbers
from core.logger import get_logger

logger = get_logger(__name__)


class IntentClassifier:
    """Machine learning-based intent classifier."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize intent classifier.
        
        Args:
            model_path: Path to saved model file
        """
        self.model_path = Path(model_path) if model_path else Path("models/intent_classifier.pkl")
        self.pipeline: Optional[Pipeline] = None
        
        # Try to load existing model
        if self.model_path.exists():
            self.load_model()
        else:
            # Create new model
            self._create_model()
            # Train with default data
            self._train_default()
    
    def _create_model(self) -> None:
        """Create a new classification pipeline."""
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english'
            )),
            ('classifier', LogisticRegression(
                max_iter=1000,
                multi_class='multinomial',
                random_state=42
            ))
        ])
        
        logger.info("Created new intent classification pipeline")
    
    def _train_default(self) -> None:
        """Train with default training data."""
        # Default training examples - expanded for better accuracy
        training_data = [
            # Commands (device/browser control)
            ("open chrome", "command"),
            ("close the window", "command"),
            ("start spotify", "command"),
            ("turn off the lights", "command"),
            ("set volume to 50", "command"),
            ("navigate to google.com", "command"),
            ("launch calculator", "command"),
            ("shut down the computer", "command"),
            ("open gmail", "command"),
            ("close this tab", "command"),
            ("maximize window", "command"),
            ("minimize all windows", "command"),
            ("lock screen", "command"),
            ("restart computer", "command"),
            ("open file explorer", "command"),
            ("play music", "command"),
            ("pause video", "command"),
            ("increase brightness", "command"),
            ("mute audio", "command"),
            ("take screenshot", "command"),
            ("open settings", "command"),
            ("switch to dark mode", "command"),
            ("go to youtube", "command"),
            ("scroll down", "command"),
            ("click submit button", "command"),
            ("fill in the form", "command"),
            ("refresh page", "command"),
            ("go back", "command"),
            ("open new tab", "command"),
            
            # Questions (information retrieval)
            ("what is the weather today", "question"),
            ("who is the president", "question"),
            ("when is the meeting", "question"),
            ("where is the nearest coffee shop", "question"),
            ("how do I install python", "question"),
            ("why is the sky blue", "question"),
            ("tell me about quantum physics", "question"),
            ("what time is it", "question"),
            ("who invented the telephone", "question"),
            ("where is paris", "question"),
            ("when was world war 2", "question"),
            ("how does photosynthesis work", "question"),
            ("what are the symptoms of flu", "question"),
            ("who won the game", "question"),
            ("where can I buy groceries", "question"),
            ("what does this mean", "question"),
            ("how tall is mount everest", "question"),
            ("when does the store close", "question"),
            ("why do we sleep", "question"),
            ("what is artificial intelligence", "question"),
            ("who wrote hamlet", "question"),
            ("where is the library", "question"),
            ("how many planets are there", "question"),
            ("what is the capital of france", "question"),
            ("tell me the news", "question"),
            ("explain machine learning", "question"),
            ("describe the process", "question"),
            ("what happened yesterday", "question"),
            
            # Math (calculations and equations)
            ("what is 5 plus 3", "math"),
            ("calculate 15 times 7", "math"),
            ("solve x squared equals 16", "math"),
            ("what is the derivative of x squared", "math"),
            ("convert 100 fahrenheit to celsius", "math"),
            ("what is 20 percent of 150", "math"),
            ("add 45 and 67", "math"),
            ("subtract 30 from 100", "math"),
            ("multiply 8 by 9", "math"),
            ("divide 144 by 12", "math"),
            ("what is the square root of 64", "math"),
            ("calculate the area of a circle with radius 5", "math"),
            ("solve for x in 2x plus 5 equals 15", "math"),
            ("integrate x squared", "math"),
            ("what is 15 to the power of 2", "math"),
            ("find the factorial of 5", "math"),
            ("convert 50 miles to kilometers", "math"),
            ("what is the sine of 30 degrees", "math"),
            ("calculate compound interest", "math"),
            ("what is 3 divided by 4", "math"),
            ("compute the average of 10 20 30", "math"),
            ("what is 25 percent off 80", "math"),
            ("solve the equation", "math"),
            ("calculate the sum", "math"),
            
            # Code (programming tasks)
            ("write a python function to sort a list", "code"),
            ("debug this code", "code"),
            ("explain this function", "code"),
            ("how to reverse a string in javascript", "code"),
            ("create a class for user management", "code"),
            ("fix the syntax error", "code"),
            ("write a function", "code"),
            ("implement bubble sort", "code"),
            ("create a rest api", "code"),
            ("write unit tests", "code"),
            ("refactor this code", "code"),
            ("optimize the algorithm", "code"),
            ("add error handling", "code"),
            ("write a loop", "code"),
            ("create a database schema", "code"),
            ("implement authentication", "code"),
            ("write sql query", "code"),
            ("debug the error", "code"),
            ("explain the code", "code"),
            ("review this function", "code"),
            ("write documentation", "code"),
            ("create a component", "code"),
            ("implement the feature", "code"),
            ("fix the bug", "code"),
            
            # Fetch (external data retrieval)
            ("get the latest news", "fetch"),
            ("search for python tutorials", "fetch"),
            ("find restaurants nearby", "fetch"),
            ("look up the definition of algorithm", "fetch"),
            ("check my calendar", "fetch"),
            ("show me my emails", "fetch"),
            ("search google for", "fetch"),
            ("find information about", "fetch"),
            ("look up", "fetch"),
            ("get weather forecast", "fetch"),
            ("fetch stock prices", "fetch"),
            ("search for recipes", "fetch"),
            ("find hotels in", "fetch"),
            ("get directions to", "fetch"),
            ("search youtube for", "fetch"),
            ("find articles about", "fetch"),
            ("look for jobs in", "fetch"),
            ("get sports scores", "fetch"),
            ("search wikipedia", "fetch"),
            ("find movies playing", "fetch"),
            ("get traffic updates", "fetch"),
            ("search for images", "fetch"),
            ("find products on amazon", "fetch"),
            
            # Conversational (social interaction)
            ("hello", "conversational"),
            ("how are you", "conversational"),
            ("thank you", "conversational"),
            ("goodbye", "conversational"),
            ("that's great", "conversational"),
            ("I don't understand", "conversational"),
            ("hi there", "conversational"),
            ("good morning", "conversational"),
            ("good night", "conversational"),
            ("thanks", "conversational"),
            ("bye", "conversational"),
            ("see you later", "conversational"),
            ("nice to meet you", "conversational"),
            ("you're welcome", "conversational"),
            ("no problem", "conversational"),
            ("sure", "conversational"),
            ("okay", "conversational"),
            ("yes", "conversational"),
            ("no", "conversational"),
            ("maybe", "conversational"),
            ("I see", "conversational"),
            ("got it", "conversational"),
            ("understood", "conversational"),
            ("sorry", "conversational"),
            ("excuse me", "conversational"),
            ("pardon", "conversational"),
            ("what", "conversational"),
            ("huh", "conversational"),
        ]
        
        texts = [text for text, _ in training_data]
        labels = [label for _, label in training_data]
        
        self.pipeline.fit(texts, labels)
        logger.info(f"Trained intent classifier with {len(training_data)} examples")
        
        # Save model
        self.save_model()
    
    async def classify(self, text: str) -> Intent:
        """
        Classify user intent.
        
        Args:
            text: Input text
            
        Returns:
            Intent object with category and confidence
        """
        return await asyncio.to_thread(self._classify_sync, text)
    
    def _classify_sync(self, text: str) -> Intent:
        """Synchronous intent classification."""
        # Normalize text
        normalized = normalize_text(text, lowercase=True, remove_punctuation=False)
        
        # Get prediction and probabilities
        prediction = self.pipeline.predict([normalized])[0]
        probabilities = self.pipeline.predict_proba([normalized])[0]
        
        # Get confidence (max probability)
        confidence = float(max(probabilities))
        
        # Map string label to IntentCategory
        category = IntentCategory(prediction)
        
        # Extract parameters based on intent
        parameters = self._extract_parameters(text, category)
        
        return Intent(
            category=category,
            confidence=confidence,
            parameters=parameters,
            context={}
        )
    
    def _extract_parameters(self, text: str, category: IntentCategory) -> Dict[str, Any]:
        """Extract parameters based on intent category."""
        parameters = {}
        
        if category == IntentCategory.MATH:
            # Extract numbers
            numbers = extract_numbers(text)
            if numbers:
                parameters['numbers'] = numbers
        
        elif category == IntentCategory.COMMAND:
            # Extract action verb (first word usually)
            words = text.lower().split()
            if words:
                parameters['action'] = words[0]
                parameters['target'] = ' '.join(words[1:]) if len(words) > 1 else None
        
        elif category == IntentCategory.QUESTION:
            # Extract question type
            question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'which']
            first_word = text.lower().split()[0] if text.split() else ''
            if first_word in question_words:
                parameters['question_type'] = first_word
        
        return parameters
    
    def save_model(self) -> None:
        """Save model to disk."""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, self.model_path)
        logger.info(f"Saved intent classifier to {self.model_path}")
    
    def load_model(self) -> None:
        """Load model from disk."""
        self.pipeline = joblib.load(self.model_path)
        logger.info(f"Loaded intent classifier from {self.model_path}")
    
    def train(self, texts: list, labels: list) -> None:
        """
        Train classifier with custom data.
        
        Args:
            texts: List of training texts
            labels: List of corresponding labels
        """
        if len(texts) != len(labels):
            raise ValueError("Number of texts and labels must match")
        
        self.pipeline.fit(texts, labels)
        logger.info(f"Trained intent classifier with {len(texts)} examples")
        
        # Save updated model
        self.save_model()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model."""
        if self.pipeline is None:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "model_path": str(self.model_path),
            "classes": list(self.pipeline.classes_) if hasattr(self.pipeline, 'classes_') else []
        }
