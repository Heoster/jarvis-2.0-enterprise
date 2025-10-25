"""Logging infrastructure for the On-Device Assistant."""

import logging
import logging.handlers
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive data from log messages."""
    
    # Patterns for sensitive data
    PATTERNS = [
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),  # Email
        (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]'),  # Phone number
        (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]'),  # Credit card
        (r'(?i)(password|passwd|pwd|token|api[_-]?key|secret)["\']?\s*[:=]\s*["\']?([^\s"\']+)', 
         r'\1=[REDACTED]'),  # Passwords and keys
        (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP]'),  # IP address
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record to redact sensitive data.
        
        Args:
            record: Log record to filter
            
        Returns:
            True to allow the record through
        """
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            for pattern, replacement in self.PATTERNS:
                msg = re.sub(pattern, replacement, msg)
            record.msg = msg
        
        return True


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON-formatted log string
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data)



def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_size_mb: int = 100,
    retention_days: int = 7,
    use_json: bool = True,
    redact_sensitive: bool = True,
) -> None:
    """
    Set up logging infrastructure for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, logs to console only
        max_size_mb: Maximum size of log file in MB before rotation
        retention_days: Number of days to retain old log files
        use_json: Whether to use JSON formatting
        redact_sensitive: Whether to redact sensitive data
    """
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    
    if redact_sensitive:
        console_handler.addFilter(SensitiveDataFilter())
    
    root_logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rotating file handler
        max_bytes = max_size_mb * 1024 * 1024
        backup_count = retention_days  # Keep one backup per day
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        
        if redact_sensitive:
            file_handler.addFilter(SensitiveDataFilter())
        
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the logger (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **context: Any
) -> None:
    """
    Log a message with additional context data.
    
    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **context: Additional context data to include
    """
    log_func = getattr(logger, level.lower())
    
    # Create log record with extra data
    extra = {'extra_data': context}
    log_func(message, extra=extra)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds component-specific context to all log messages.
    """
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """
        Process log message to add context.
        
        Args:
            msg: Log message
            kwargs: Keyword arguments
            
        Returns:
            Tuple of (message, kwargs)
        """
        # Add component context to extra data
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        
        if 'extra_data' not in kwargs['extra']:
            kwargs['extra']['extra_data'] = {}
        
        kwargs['extra']['extra_data'].update(self.extra)
        
        return msg, kwargs


def get_component_logger(component_name: str, **context: Any) -> LoggerAdapter:
    """
    Get a logger adapter for a specific component with context.
    
    Args:
        component_name: Name of the component
        **context: Additional context to include in all logs
        
    Returns:
        LoggerAdapter instance
    """
    logger = get_logger(component_name)
    return LoggerAdapter(logger, {'component': component_name, **context})
