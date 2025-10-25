"""Text preprocessing and utility functions."""

import re
import string
from typing import List, Optional, Dict, Any
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize

from core.logger import get_logger

logger = get_logger(__name__)

# Optional imports
try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logger.warning("langdetect not available, language detection will be limited")

try:
    import dateparser
    DATEPARSER_AVAILABLE = True
except ImportError:
    DATEPARSER_AVAILABLE = False
    logger.warning("dateparser not available, date parsing will be limited")

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except (LookupError, Exception) as e:
    try:
        nltk.download('punkt', quiet=True)
    except Exception as download_error:
        logger.warning(f"Failed to download NLTK punkt: {download_error}")


def normalize_text(
    text: str, 
    lowercase: bool = True, 
    remove_punctuation: bool = False,
    remove_extra_spaces: bool = True,
    strip_accents: bool = False
) -> str:
    """
    Normalize text for processing.
    
    Args:
        text: Input text
        lowercase: Convert to lowercase
        remove_punctuation: Remove punctuation marks
        remove_extra_spaces: Collapse multiple spaces into one
        strip_accents: Remove accent marks from characters
        
    Returns:
        Normalized text
    """
    # Strip accents if requested
    if strip_accents:
        import unicodedata
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )
    
    # Remove extra whitespace
    if remove_extra_spaces:
        text = re.sub(r'\s+', ' ', text).strip()
    
    # Lowercase
    if lowercase:
        text = text.lower()
    
    # Remove punctuation
    if remove_punctuation:
        text = text.translate(str.maketrans('', '', string.punctuation))
    
    return text


def detect_language(text: str) -> str:
    """
    Detect language of text.
    
    Args:
        text: Input text
        
    Returns:
        ISO 639-1 language code (e.g., 'en', 'es', 'fr')
    """
    if not LANGDETECT_AVAILABLE:
        return "en"  # Default to English
    
    try:
        return detect(text)
    except (LangDetectException, Exception):
        logger.warning(f"Could not detect language for text: {text[:50]}...")
        return "en"  # Default to English


def tokenize(text: str, method: str = 'word') -> List[str]:
    """
    Tokenize text into words or sentences.
    
    Args:
        text: Input text
        method: Tokenization method ('word' or 'sentence')
        
    Returns:
        List of tokens
    """
    if method == 'sentence':
        from nltk.tokenize import sent_tokenize
        try:
            return sent_tokenize(text)
        except LookupError:
            nltk.download('punkt', quiet=True)
            return sent_tokenize(text)
    else:
        return word_tokenize(text)


def tokenize_advanced(text: str, remove_stop: bool = False, lemmatize: bool = False) -> List[str]:
    """
    Advanced tokenization with optional stopword removal and lemmatization.
    
    Args:
        text: Input text
        remove_stop: Remove common stopwords
        lemmatize: Convert words to their base form
        
    Returns:
        List of processed tokens
    """
    tokens = word_tokenize(text.lower())
    
    # Remove punctuation tokens
    tokens = [t for t in tokens if t not in string.punctuation]
    
    # Remove stopwords
    if remove_stop:
        tokens = remove_stopwords(tokens)
    
    # Lemmatize
    if lemmatize:
        try:
            from nltk.stem import WordNetLemmatizer
            lemmatizer = WordNetLemmatizer()
            tokens = [lemmatizer.lemmatize(t) for t in tokens]
        except (LookupError, Exception):
            try:
                nltk.download('wordnet', quiet=True)
                from nltk.stem import WordNetLemmatizer
                lemmatizer = WordNetLemmatizer()
                tokens = [lemmatizer.lemmatize(t) for t in tokens]
            except Exception as e:
                logger.warning(f"Failed to lemmatize: {e}")
    
    return tokens


def parse_datetime(
    text: str, 
    settings: Optional[dict] = None,
    languages: Optional[List[str]] = None
) -> Optional[datetime]:
    """
    Parse natural language date/time expressions.
    
    Args:
        text: Text containing date/time expression
        settings: dateparser settings
        languages: List of language codes to try
        
    Returns:
        datetime object or None if parsing fails
    """
    if not DATEPARSER_AVAILABLE:
        logger.warning("dateparser not available, cannot parse datetime")
        return None
    
    if settings is None:
        settings = {
            'PREFER_DATES_FROM': 'future',
            'RETURN_AS_TIMEZONE_AWARE': False
        }
    
    try:
        return dateparser.parse(text, settings=settings, languages=languages)
    except Exception as e:
        logger.warning(f"Failed to parse datetime from '{text}': {e}")
        return None


def extract_dates(text: str) -> List[datetime]:
    """
    Extract all date/time expressions from text.
    
    Args:
        text: Input text
        
    Returns:
        List of datetime objects found
    """
    dates = []
    
    # Common date patterns
    date_patterns = [
        r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',  # Month DD, YYYY
        r'\b(?:today|tomorrow|yesterday)\b',
        r'\b(?:next|last) (?:week|month|year|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b'
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            parsed = parse_datetime(match)
            if parsed:
                dates.append(parsed)
    
    return dates


def extract_numbers(text: str) -> List[float]:
    """
    Extract numeric values from text.
    
    Args:
        text: Input text
        
    Returns:
        List of numbers found
    """
    # Pattern for integers and floats
    pattern = r'-?\d+\.?\d*'
    matches = re.findall(pattern, text)
    
    numbers = []
    for match in matches:
        try:
            if '.' in match:
                numbers.append(float(match))
            else:
                numbers.append(float(int(match)))
        except ValueError:
            continue
    
    return numbers


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text.
    
    Args:
        text: Input text
        
    Returns:
        List of URLs found
    """
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)


def extract_emails(text: str) -> List[str]:
    """
    Extract email addresses from text.
    
    Args:
        text: Input text
        
    Returns:
        List of email addresses found
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def clean_text(text: str) -> str:
    """
    Clean text by removing special characters and normalizing.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def split_sentences(text: str) -> List[str]:
    """
    Split text into sentences.
    
    Args:
        text: Input text
        
    Returns:
        List of sentences
    """
    # Simple sentence splitting (for better results, use spaCy)
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


def remove_stopwords(tokens: List[str], language: str = 'english') -> List[str]:
    """
    Remove stopwords from token list.
    
    Args:
        tokens: List of tokens
        language: Language for stopwords
        
    Returns:
        Filtered token list
    """
    try:
        from nltk.corpus import stopwords
        stop_words = set(stopwords.words(language))
    except (LookupError, Exception):
        try:
            nltk.download('stopwords', quiet=True)
            from nltk.corpus import stopwords
            stop_words = set(stopwords.words(language))
        except Exception as e:
            logger.warning(f"Failed to load stopwords: {e}, returning original tokens")
            return tokens
    
    return [token for token in tokens if token.lower() not in stop_words]


def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """
    Extract keywords from text using simple frequency analysis.
    
    Args:
        text: Input text
        top_n: Number of keywords to extract
        
    Returns:
        List of keywords
    """
    # Tokenize and normalize
    tokens = tokenize(text.lower())
    
    # Remove stopwords and punctuation
    tokens = [t for t in tokens if t not in string.punctuation]
    tokens = remove_stopwords(tokens)
    
    # Count frequencies
    freq = {}
    for token in tokens:
        freq[token] = freq.get(token, 0) + 1
    
    # Sort by frequency
    sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    
    return [token for token, _ in sorted_tokens[:top_n]]


def is_question(text: str) -> bool:
    """
    Determine if text is a question.
    
    Args:
        text: Input text
        
    Returns:
        True if text appears to be a question
    """
    text = text.strip()
    
    # Check for question mark
    if text.endswith('?'):
        return True
    
    # Check for question words at start
    question_words = ['what', 'when', 'where', 'who', 'whom', 'whose', 'why', 'which', 'how']
    first_word = text.split()[0].lower() if text.split() else ''
    
    return first_word in question_words


def is_command(text: str) -> bool:
    """
    Determine if text is a command.
    
    Args:
        text: Input text
        
    Returns:
        True if text appears to be a command
    """
    text = text.strip().lower()
    
    # Check for imperative verbs
    command_verbs = [
        'open', 'close', 'start', 'stop', 'run', 'execute', 'launch',
        'show', 'hide', 'set', 'get', 'create', 'delete', 'remove',
        'play', 'pause', 'search', 'find', 'go', 'navigate', 'turn',
        'switch', 'change', 'adjust', 'increase', 'decrease', 'enable',
        'disable', 'activate', 'deactivate', 'install', 'uninstall'
    ]
    
    first_word = text.split()[0] if text.split() else ''
    
    return first_word in command_verbs


def expand_contractions(text: str) -> str:
    """
    Expand common English contractions.
    
    Args:
        text: Input text
        
    Returns:
        Text with expanded contractions
    """
    contractions = {
        "ain't": "am not",
        "aren't": "are not",
        "can't": "cannot",
        "can't've": "cannot have",
        "could've": "could have",
        "couldn't": "could not",
        "didn't": "did not",
        "doesn't": "does not",
        "don't": "do not",
        "hadn't": "had not",
        "hasn't": "has not",
        "haven't": "have not",
        "he'd": "he would",
        "he'll": "he will",
        "he's": "he is",
        "i'd": "i would",
        "i'll": "i will",
        "i'm": "i am",
        "i've": "i have",
        "isn't": "is not",
        "it'd": "it would",
        "it'll": "it will",
        "it's": "it is",
        "let's": "let us",
        "shouldn't": "should not",
        "that's": "that is",
        "there's": "there is",
        "they'd": "they would",
        "they'll": "they will",
        "they're": "they are",
        "they've": "they have",
        "wasn't": "was not",
        "we'd": "we would",
        "we'll": "we will",
        "we're": "we are",
        "we've": "we have",
        "weren't": "were not",
        "what'll": "what will",
        "what're": "what are",
        "what's": "what is",
        "what've": "what have",
        "where's": "where is",
        "who'd": "who would",
        "who'll": "who will",
        "who're": "who are",
        "who's": "who is",
        "won't": "will not",
        "wouldn't": "would not",
        "you'd": "you would",
        "you'll": "you will",
        "you're": "you are",
        "you've": "you have"
    }
    
    for contraction, expansion in contractions.items():
        text = re.sub(r'\b' + contraction + r'\b', expansion, text, flags=re.IGNORECASE)
    
    return text


def normalize_whitespace(text: str) -> str:
    """
    Normalize all whitespace characters to single spaces.
    
    Args:
        text: Input text
        
    Returns:
        Text with normalized whitespace
    """
    # Replace tabs, newlines, etc. with spaces
    text = re.sub(r'[\t\n\r\f\v]', ' ', text)
    # Collapse multiple spaces
    text = re.sub(r' +', ' ', text)
    return text.strip()


def remove_html_tags(text: str) -> str:
    """
    Remove HTML tags from text.
    
    Args:
        text: Input text with HTML
        
    Returns:
        Text without HTML tags
    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Input text
        
    Returns:
        Word count
    """
    return len(text.split())


def count_sentences(text: str) -> int:
    """
    Count sentences in text.
    
    Args:
        text: Input text
        
    Returns:
        Sentence count
    """
    return len(split_sentences(text))


def get_text_stats(text: str) -> Dict[str, Any]:
    """
    Get comprehensive statistics about text.
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with text statistics
    """
    words = text.split()
    sentences = split_sentences(text)
    
    return {
        'char_count': len(text),
        'word_count': len(words),
        'sentence_count': len(sentences),
        'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
        'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
        'unique_words': len(set(w.lower() for w in words)),
        'is_question': is_question(text),
        'is_command': is_command(text)
    }
