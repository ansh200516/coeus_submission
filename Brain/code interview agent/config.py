"""
Configuration settings for the Code Interview Agent system.

This module centralizes all configuration parameters for the interview system,
including audio settings, browser automation, timing thresholds, and API configurations.
"""

import logging
import os
from typing import Dict, Any

# Import Cerebras SDK
try:
    from cerebras.cloud.sdk import Cerebras
except ImportError:
    Cerebras = None
    print("⚠️  Cerebras SDK not installed. Run: pip install cerebras-cloud-sdk")

# ========== TIMING CONFIGURATION ==========
# Time thresholds (in seconds)
INACTIVITY_THRESHOLD: int = 15  # Time before triggering nudge
POLLING_INTERVAL: int = 5  # How often to check editor content
MAX_INTERVIEW_DURATION: int = 1800  # Maximum interview duration (30 minutes)
LISTENING_WINDOW: int = 30  # Maximum time to wait for candidate response

# ========== BROWSER CONFIGURATION ==========
BROWSER_HEADLESS: bool = False  # Set to True to run browser in background
REACT_APP_URL: str = "http://localhost:3000/coding-engine"  # Next.js app URL
BROWSER_TIMEOUT: int = 10  # Selenium wait timeout in seconds

# ========== AUDIO CONFIGURATION ==========
STT_MODEL: str = "nova-3"  # Deepgram STT model
TTS_MODEL: str = "aura-2-thalia-en"  # Deepgram TTS model
SAMPLE_RATE: int = 24000  # Audio sample rate

# Audio cache directory for filler sounds
AUDIO_CACHE_DIR: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    "..", "lda", "audio_cache"
)

# ========== LOGGING CONFIGURATION ==========
LOG_LEVEL: int = logging.INFO
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ========== AI MODEL CONFIGURATION ==========
# Cerebras model settings
CEREBRAS_MODEL: str = "gpt-oss-120b"
CEREBRAS_TEMPERATURE: float = 1.0
CEREBRAS_MAX_TOKENS: int = 8192
CEREBRAS_TOP_P: float = 1.0
CEREBRAS_REASONING_EFFORT: str = "medium"
CEREBRAS_STREAM: bool = True

# Analysis thresholds
CODE_ANALYSIS_CONFIDENCE_THRESHOLD: float = 0.7
HINT_ESCALATION_LEVELS: Dict[int, str] = {
    1: "gentle",
    2: "direct", 
    3: "explicit",
    4: "solution_hint"
}

# ========== INTERVIEW CONFIGURATION ==========
# Question difficulty progression
DIFFICULTY_PROGRESSION: list = ["easy", "medium", "hard"]
MAX_HINTS_PER_QUESTION: int = 3
MIN_CODE_CHANGE_THRESHOLD: int = 10  # Minimum characters changed to register activity

# Test execution settings
TEST_TIMEOUT: int = 30  # Maximum time for test execution in seconds
MAX_TEST_RETRIES: int = 3

# ========== SESSION MANAGEMENT ==========
# Auto-save intervals
CHECKPOINT_INTERVAL: int = 300  # Save checkpoint every 5 minutes
EMERGENCY_SAVE_ENABLED: bool = True

# Session directories
INTERVIEWS_DIR: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    "interviews"
)
SESSIONS_DIR: str = os.path.join(INTERVIEWS_DIR, "sessions")
ARTIFACTS_DIR: str = os.path.join(INTERVIEWS_DIR, "artifacts")
EXPORTS_DIR: str = os.path.join(INTERVIEWS_DIR, "exports")

# ========== API CONFIGURATION ==========
# Rate limiting
MAX_API_CALLS_PER_MINUTE: int = 60
API_RETRY_ATTEMPTS: int = 3
API_RETRY_DELAY: float = 1.0  # seconds

# ========== VALIDATION FUNCTIONS ==========
def validate_config() -> bool:
    """
    Validate configuration settings and environment variables.
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    required_env_vars = [
        "DEEPGRAM_API_KEY",
        "CEREBRAS_API_KEY"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    # Validate directories exist or can be created
    dirs_to_check = [INTERVIEWS_DIR, SESSIONS_DIR, ARTIFACTS_DIR, EXPORTS_DIR]
    for directory in dirs_to_check:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            print(f"❌ Cannot create directory {directory}: {e}")
            return False
    
    return True

def get_cerebras_client() -> Cerebras:
    """
    Create and return a Cerebras client instance.
    
    Returns:
        Cerebras: Configured Cerebras client
        
    Raises:
        ImportError: If Cerebras SDK is not installed
        ValueError: If CEREBRAS_API_KEY environment variable is not set
    """
    if Cerebras is None:
        raise ImportError("Cerebras SDK not installed. Run: pip install cerebras-cloud-sdk")
    
    api_key = os.environ.get("CEREBRAS_API_KEY")
    if not api_key:
        raise ValueError("CEREBRAS_API_KEY environment variable is required")
    
    return Cerebras(api_key=api_key)

def get_cerebras_completion_params() -> Dict[str, Any]:
    """
    Get standard parameters for Cerebras completion requests.
    
    Returns:
        Dict[str, Any]: Parameters for chat completions
    """
    return {
        "model": CEREBRAS_MODEL,
        "stream": CEREBRAS_STREAM,
        "max_completion_tokens": CEREBRAS_MAX_TOKENS,
        "temperature": CEREBRAS_TEMPERATURE,
        "top_p": CEREBRAS_TOP_P,
        "reasoning_effort": CEREBRAS_REASONING_EFFORT
    }

def get_config_summary() -> Dict[str, Any]:
    """
    Get a summary of current configuration settings.
    
    Returns:
        Dict[str, Any]: Configuration summary
    """
    return {
        "timing": {
            "inactivity_threshold": INACTIVITY_THRESHOLD,
            "polling_interval": POLLING_INTERVAL,
            "max_duration": MAX_INTERVIEW_DURATION,
        },
        "browser": {
            "headless": BROWSER_HEADLESS,
            "url": REACT_APP_URL,
            "timeout": BROWSER_TIMEOUT,
        },
        "audio": {
            "stt_model": STT_MODEL,
            "tts_model": TTS_MODEL,
            "sample_rate": SAMPLE_RATE,
        },
        "ai": {
            "model": CEREBRAS_MODEL,
            "stream": CEREBRAS_STREAM,
            "max_completion_tokens": CEREBRAS_MAX_TOKENS,
            "temperature": CEREBRAS_TEMPERATURE,
            "top_p": CEREBRAS_TOP_P,
            "reasoning_effort": CEREBRAS_REASONING_EFFORT
        }
    }
