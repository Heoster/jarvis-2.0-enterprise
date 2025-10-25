"""Configuration management for the On-Device Assistant."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv


class AssistantConfig(BaseModel):
    """Core assistant configuration."""
    name: str = "Jarvis"
    personality: str = "sophisticated"
    language: str = "en"
    log_level: str = "INFO"


class AIConfig(BaseModel):
    """AI model configuration."""
    use_dialogflow: bool = False
    dialogflow_project_id: Optional[str] = None
    local_model: str = "facebook/blenderbot-400M-distill"
    backend_preference: str = "local"


class STTConfig(BaseModel):
    """Speech-to-text configuration."""
    provider: str = "google"
    google_credentials: Optional[str] = None
    language: str = "en"
    device: str = "cpu"


class TTSConfig(BaseModel):
    """Text-to-speech configuration."""
    provider: str = "google"
    google_credentials: Optional[str] = None
    voice: str = "en-US-Standard-A"
    speed: float = 1.0
    device: str = "cpu"


class NLPConfig(BaseModel):
    """NLP model configuration."""
    spacy_model: str = "en_core_web_sm"


class EmbeddingsConfig(BaseModel):
    """Embeddings model configuration."""
    model: str = "all-MiniLM-L6-v2"
    device: str = "cpu"


class VisionConfig(BaseModel):
    """Computer vision configuration."""
    enabled: bool = True
    face_detection: bool = True
    object_detection: bool = True


class ModelsConfig(BaseModel):
    """All model configurations."""
    ai: AIConfig = Field(default_factory=AIConfig)
    stt: STTConfig = Field(default_factory=STTConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    nlp: NLPConfig = Field(default_factory=NLPConfig)
    embeddings: EmbeddingsConfig = Field(default_factory=EmbeddingsConfig)
    vision: VisionConfig = Field(default_factory=VisionConfig)


class PerformanceConfig(BaseModel):
    """Performance optimization settings."""
    max_concurrent_actions: int = 5
    model_cache_size: int = 3
    response_cache_ttl: int = 3600
    embedding_batch_size: int = 32
    lazy_load_models: bool = True
    model_idle_timeout: int = 300


class DefaultPermissions(BaseModel):
    """Default permission settings."""
    monitor_web: bool = False
    monitor_apps: bool = False
    control_device: bool = False
    control_browser: bool = False
    access_memory: bool = True
    call_apis: bool = False


class PrivacyConfig(BaseModel):
    """Privacy and security settings."""
    data_retention_days: int = 30
    encrypt_memory: bool = True
    local_only: bool = True
    default_permissions: DefaultPermissions = Field(default_factory=DefaultPermissions)


class ServerConfig(BaseModel):
    """Server configuration."""
    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:*"])
    enable_api_key: bool = False
    api_key: Optional[str] = None
    rate_limit_per_minute: int = 60


class WakewordConfig(BaseModel):
    """Wakeword detection settings."""
    enabled: bool = True
    phrase: str = "hey assistant"
    sensitivity: float = 0.5


class VADConfig(BaseModel):
    """Voice activity detection settings."""
    enabled: bool = True
    aggressiveness: int = 2
    frame_duration_ms: int = 30


class AudioConfig(BaseModel):
    """Audio capture settings."""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024


class VoiceConfig(BaseModel):
    """Voice input/output configuration."""
    wakeword: WakewordConfig = Field(default_factory=WakewordConfig)
    vad: VADConfig = Field(default_factory=VADConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)


class RetrievalConfig(BaseModel):
    """Information retrieval settings."""
    top_k_sparse: int = 20
    top_k_dense: int = 10
    min_confidence: float = 0.3
    use_reranking: bool = True


class DatabaseConfig(BaseModel):
    """Database configuration."""
    memory_db: str = "data/memory.db"
    cache_db: str = "data/cache.db"
    vector_index: str = "data/vectors.index"
    enable_wal: bool = True


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    file: str = "data/logs/assistant.log"
    max_size_mb: int = 100
    retention_days: int = 7
    format: str = "json"
    redact_sensitive: bool = True


class ActivityConfig(BaseModel):
    """Activity monitoring configuration."""
    enabled: bool = False
    web_tracking: bool = False
    app_tracking: bool = False
    blacklist_domains: List[str] = Field(default_factory=list)
    whitelist_apps: List[str] = Field(default_factory=list)


class APIIntegrationConfig(BaseModel):
    """Single API integration settings."""
    enabled: bool = False
    api_key: Optional[str] = None
    provider: str


class KnowledgeConfig(BaseModel):
    """Knowledge graph configuration."""
    enabled: bool = True
    use_wikipedia: bool = True
    use_wikidata: bool = False


class APIsConfig(BaseModel):
    """External API configurations."""
    weather: APIIntegrationConfig = Field(
        default_factory=lambda: APIIntegrationConfig(enabled=True, provider="openweathermap")
    )
    news: APIIntegrationConfig = Field(
        default_factory=lambda: APIIntegrationConfig(enabled=True, provider="newsapi")
    )
    search: APIIntegrationConfig = Field(
        default_factory=lambda: APIIntegrationConfig(enabled=True, provider="duckduckgo")
    )
    knowledge: KnowledgeConfig = Field(default_factory=KnowledgeConfig)


class SafetyConfig(BaseModel):
    """Safety and security settings."""
    require_confirmation_for_high_risk: bool = True
    high_risk_cooldown_seconds: int = 5
    sandbox_code_execution: bool = True
    max_code_execution_time: int = 10
    command_whitelist: List[str] = Field(default_factory=list)


class Config(BaseModel):
    """Main configuration class."""
    assistant: AssistantConfig = Field(default_factory=AssistantConfig)
    models: ModelsConfig = Field(default_factory=ModelsConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    privacy: PrivacyConfig = Field(default_factory=PrivacyConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    voice: VoiceConfig = Field(default_factory=VoiceConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    activity: ActivityConfig = Field(default_factory=ActivityConfig)
    apis: APIsConfig = Field(default_factory=APIsConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)

    class Config:
        """Pydantic configuration."""
        extra = "allow"



def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from YAML file with environment variable overrides.
    
    Args:
        config_path: Path to configuration file. If None, uses default.yaml
        
    Returns:
        Config object with loaded settings
    """
    # Load environment variables from .env file if present
    load_dotenv()
    
    # Determine config file path
    if config_path is None:
        config_path = os.getenv("ASSISTANT_CONFIG_PATH", "config/default.yaml")
    
    config_file = Path(config_path)
    
    # Load YAML configuration
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f) or {}
    else:
        config_dict = {}
    
    # Apply environment variable overrides
    config_dict = _apply_env_overrides(config_dict)
    
    # Create and validate config object
    return Config(**config_dict)


def _apply_env_overrides(config_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply environment variable overrides to configuration.
    
    Environment variables should be prefixed with ASSISTANT_ and use
    double underscores for nested keys. For example:
    - ASSISTANT_SERVER__PORT=9000
    - ASSISTANT_MODELS__LLM__DEFAULT=llama3.2:3b
    
    Args:
        config_dict: Base configuration dictionary
        
    Returns:
        Configuration dictionary with environment overrides applied
    """
    prefix = "ASSISTANT_"
    
    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue
        
        # Remove prefix and split by double underscore
        config_key = key[len(prefix):].lower()
        parts = config_key.split("__")
        
        # Navigate to the correct nested dictionary
        current = config_dict
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value (try to parse as int/float/bool)
        final_key = parts[-1]
        current[final_key] = _parse_env_value(value)
    
    return config_dict


def _parse_env_value(value: str) -> Any:
    """
    Parse environment variable value to appropriate type.
    
    Args:
        value: String value from environment variable
        
    Returns:
        Parsed value (int, float, bool, or str)
    """
    # Try boolean
    if value.lower() in ("true", "yes", "1"):
        return True
    if value.lower() in ("false", "no", "0"):
        return False
    
    # Try integer
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try float
    try:
        return float(value)
    except ValueError:
        pass
    
    # Return as string
    return value


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.
    
    Returns:
        Global Config object
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config(config_path: Optional[str] = None) -> Config:
    """
    Reload configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Reloaded Config object
    """
    global _config
    _config = load_config(config_path)
    return _config
