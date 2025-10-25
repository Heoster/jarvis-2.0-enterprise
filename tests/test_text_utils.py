"""Tests for text utility functions."""

import pytest
from datetime import datetime
from core.text_utils import (
    normalize_text,
    detect_language,
    tokenize,
    parse_datetime,
    extract_numbers,
    extract_urls,
    extract_emails,
    is_question,
    is_command,
    expand_contractions,
    get_text_stats,
    extract_dates
)


def test_normalize_text():
    """Test text normalization."""
    text = "  Hello   World!  "
    normalized = normalize_text(text)
    assert normalized == "hello world!"
    
    # Test without lowercase
    normalized = normalize_text(text, lowercase=False)
    assert normalized == "Hello World!"
    
    # Test with punctuation removal
    normalized = normalize_text(text, remove_punctuation=True)
    assert normalized == "hello world"


def test_detect_language():
    """Test language detection."""
    assert detect_language("Hello, how are you?") == "en"
    assert detect_language("Bonjour, comment allez-vous?") == "fr"
    assert detect_language("Hola, ¿cómo estás?") == "es"


def test_tokenize():
    """Test tokenization."""
    text = "Hello, world! How are you?"
    tokens = tokenize(text)
    assert len(tokens) > 0
    assert "Hello" in tokens or "hello" in tokens


def test_parse_datetime():
    """Test datetime parsing."""
    result = parse_datetime("tomorrow")
    assert result is not None
    assert isinstance(result, datetime)
    
    result = parse_datetime("next Monday")
    assert result is not None
    
    result = parse_datetime("2024-12-25")
    assert result is not None


def test_extract_numbers():
    """Test number extraction."""
    text = "I have 5 apples and 3.14 oranges"
    numbers = extract_numbers(text)
    assert 5.0 in numbers
    assert 3.14 in numbers


def test_extract_urls():
    """Test URL extraction."""
    text = "Visit https://example.com and http://test.org"
    urls = extract_urls(text)
    assert len(urls) == 2
    assert "https://example.com" in urls
    assert "http://test.org" in urls


def test_extract_emails():
    """Test email extraction."""
    text = "Contact me at test@example.com or admin@test.org"
    emails = extract_emails(text)
    assert len(emails) == 2
    assert "test@example.com" in emails
    assert "admin@test.org" in emails


def test_is_question():
    """Test question detection."""
    assert is_question("What is your name?")
    assert is_question("How are you?")
    assert is_question("Where is the library")  # Question word
    assert not is_question("Hello there")
    assert not is_question("Open the door")


def test_is_command():
    """Test command detection."""
    assert is_command("Open the file")
    assert is_command("Close the window")
    assert is_command("Start the application")
    assert not is_command("What is this?")
    assert not is_command("Hello there")


def test_expand_contractions():
    """Test contraction expansion."""
    text = "I'm going to the store. Don't forget!"
    expanded = expand_contractions(text)
    assert "i am" in expanded.lower()
    assert "do not" in expanded.lower()


def test_get_text_stats():
    """Test text statistics."""
    text = "Hello world. How are you? I am fine."
    stats = get_text_stats(text)
    
    assert stats["word_count"] > 0
    assert stats["sentence_count"] > 0
    assert stats["char_count"] == len(text)
    assert "avg_word_length" in stats
    assert "is_question" in stats
    assert "is_command" in stats


def test_extract_dates():
    """Test date extraction from text."""
    text = "Meet me on 2024-12-25 or tomorrow at 3pm"
    dates = extract_dates(text)
    assert len(dates) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
