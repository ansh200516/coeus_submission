"""
Utility functions for the Code Interview Agent system.

This module provides common utility functions for text processing,
file operations, session management, and other helper functionalities.
"""

import os
import re
import json
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


# ========== TEXT PROCESSING UTILITIES ==========

def strip_markdown(text: str) -> str:
    """
    Remove markdown formatting from text for speech synthesis.
    
    Args:
        text: Text potentially containing markdown
        
    Returns:
        str: Clean text without markdown formatting
    """
    if not text:
        return ""
    
    # Remove markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'`(.*?)`', r'\1', text)        # Inline code
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)  # Code blocks
    text = re.sub(r'#{1,6}\s*(.*)', r'\1', text)  # Headers
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Links
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)  # Lists
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)  # Numbered lists
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def remove_asterisks_from_response(text: str) -> str:
    """
    Remove asterisks from LLM responses.
    
    Args:
        text: Raw text response from LLM
        
    Returns:
        str: Text with asterisks removed
    """
    if not text:
        return ""
    
    # Remove all asterisks from the text
    text = text.replace('*', '')
    
    # Clean up any extra whitespace that might result from asterisk removal
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def clean_text_for_speech(text: str) -> str:
    """
    Clean and prepare text for text-to-speech synthesis.
    
    Args:
        text: Raw text to clean
        
    Returns:
        str: Text optimized for speech synthesis
    """
    if not text:
        return ""
    
    # Remove asterisks first
    text = remove_asterisks_from_response(text)
    
    # Remove markdown
    text = strip_markdown(text)
    
    # Replace technical symbols with spoken equivalents
    replacements = {
        '&&': ' and ',
        '||': ' or ',
        '!=': ' not equals ',
        '==': ' equals ',
        '<=': ' less than or equal to ',
        '>=': ' greater than or equal to ',
        '++': ' increment ',
        '--': ' decrement ',
        '->': ' arrow ',
        '=>': ' arrow ',
        '[]': ' array ',
        '{}': ' object ',
        '()': ' parentheses ',
    }
    
    for symbol, replacement in replacements.items():
        text = text.replace(symbol, replacement)
    
    # Remove excessive punctuation
    text = re.sub(r'[.]{2,}', '.', text)
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    
    # Ensure proper sentence spacing
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def sanitize_llm_json_output(text: str) -> str:
    """
    Sanitize LLM output to ensure valid JSON parsing.
    
    Args:
        text: Raw LLM output that should contain JSON
        
    Returns:
        str: Sanitized JSON string
    """
    if not text:
        return "{}"
    
    # Remove markdown code block formatting
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*$', '', text)
    
    # Remove any text before the first { or [
    json_start = max(text.find('{'), text.find('['))
    if json_start != -1:
        text = text[json_start:]
    
    # Remove any text after the last } or ]
    json_end = max(text.rfind('}'), text.rfind(']'))
    if json_end != -1:
        text = text[:json_end + 1]
    
    # Fix common JSON issues
    text = re.sub(r',\s*}', '}', text)  # Remove trailing commas in objects
    text = re.sub(r',\s*]', ']', text)  # Remove trailing commas in arrays
    
    return text.strip()


# ========== FILE AND PATH UTILITIES ==========

def find_project_root(start_path: Optional[str] = None) -> Optional[str]:
    """
    Find the project root directory by looking for specific marker files.
    
    Args:
        start_path: Starting path to search from (defaults to current file's directory)
        
    Returns:
        Optional[str]: Path to project root, or None if not found
    """
    if start_path is None:
        start_path = os.path.dirname(os.path.abspath(__file__))
    
    current_path = Path(start_path).resolve()
    
    # Look for common project root indicators
    markers = [
        'pyproject.toml',
        'requirements.txt',
        '.git',
        'README.md',
        'package.json'
    ]
    
    # Traverse up the directory tree
    for parent in [current_path] + list(current_path.parents):
        for marker in markers:
            if (parent / marker).exists():
                return str(parent)
    
    return None


def ensure_directory(path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure
        
    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False


def safe_json_load(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Safely load JSON from a file with error handling.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Optional[Dict[str, Any]]: Loaded JSON data or None if failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON from {file_path}: {e}")
        return None


def safe_json_save(data: Dict[str, Any], file_path: str) -> bool:
    """
    Safely save JSON to a file with error handling.
    
    Args:
        data: Data to save as JSON
        file_path: Path to save JSON file
        
    Returns:
        bool: True if saved successfully, False otherwise
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if directory and not ensure_directory(directory):
            return False
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False, default=str)
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON to {file_path}: {e}")
        return False


# ========== SESSION MANAGEMENT UTILITIES ==========

def generate_session_id() -> str:
    """
    Generate a unique session identifier.
    
    Returns:
        str: Unique session ID
    """
    return f"S{uuid.uuid4().hex[:8]}"


def generate_timestamp_string() -> str:
    """
    Generate a timestamp string for file naming.
    
    Returns:
        str: Formatted timestamp string
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_session_file_path(session_id: str, base_dir: str, file_type: str = "checkpoint") -> str:
    """
    Get the file path for a session file.
    
    Args:
        session_id: Session identifier
        base_dir: Base directory for session files
        file_type: Type of file ("checkpoint", "emergency", "export")
        
    Returns:
        str: Full file path
    """
    filename = f"{session_id}_{file_type}.json"
    return os.path.join(base_dir, session_id, filename)


# ========== CODE ANALYSIS UTILITIES ==========

def analyze_code_complexity(code: str) -> Dict[str, Any]:
    """
    Analyze code complexity metrics.
    
    Args:
        code: Source code to analyze
        
    Returns:
        Dict[str, Any]: Complexity metrics
    """
    if not code.strip():
        return {"lines": 0, "functions": 0, "classes": 0, "complexity": "empty"}
    
    lines = len([line for line in code.split('\n') if line.strip()])
    
    # Count functions and classes (basic regex-based counting)
    functions = len(re.findall(r'def\s+\w+\s*\(', code))
    classes = len(re.findall(r'class\s+\w+\s*[:\(]', code))
    
    # Basic complexity estimation
    complexity_indicators = [
        len(re.findall(r'\bif\b', code)),
        len(re.findall(r'\bfor\b', code)),
        len(re.findall(r'\bwhile\b', code)),
        len(re.findall(r'\btry\b', code)),
        len(re.findall(r'\bexcept\b', code)),
    ]
    
    total_complexity = sum(complexity_indicators)
    
    if total_complexity == 0:
        complexity_level = "simple"
    elif total_complexity <= 3:
        complexity_level = "moderate"
    elif total_complexity <= 7:
        complexity_level = "complex"
    else:
        complexity_level = "very_complex"
    
    return {
        "lines": lines,
        "functions": functions,
        "classes": classes,
        "control_structures": total_complexity,
        "complexity": complexity_level
    }


def extract_code_changes(old_code: str, new_code: str) -> Dict[str, Any]:
    """
    Extract and analyze changes between two code versions.
    
    Args:
        old_code: Previous version of code
        new_code: Current version of code
        
    Returns:
        Dict[str, Any]: Change analysis
    """
    if not old_code:
        return {
            "type": "initial",
            "lines_added": len(new_code.split('\n')) if new_code else 0,
            "lines_removed": 0,
            "significant_change": bool(new_code.strip())
        }
    
    old_lines = old_code.split('\n')
    new_lines = new_code.split('\n')
    
    lines_added = max(0, len(new_lines) - len(old_lines))
    lines_removed = max(0, len(old_lines) - len(new_lines))
    
    # Simple change detection (character-based)
    char_changes = abs(len(new_code) - len(old_code))
    significant_change = char_changes > 10  # More than 10 character changes
    
    return {
        "type": "modification",
        "lines_added": lines_added,
        "lines_removed": lines_removed,
        "char_changes": char_changes,
        "significant_change": significant_change
    }


# ========== AUDIO UTILITIES ==========

def get_random_filler_audio(audio_cache_dir: str) -> Optional[str]:
    """
    Get a random filler audio file from the cache directory.
    
    Args:
        audio_cache_dir: Directory containing filler audio files
        
    Returns:
        Optional[str]: Path to random filler audio file, or None if none available
    """
    try:
        if not os.path.exists(audio_cache_dir):
            return None
        
        audio_files = [
            f for f in os.listdir(audio_cache_dir) 
            if f.endswith(('.wav', '.mp3'))
        ]
        
        if not audio_files:
            return None
        
        import random
        selected_file = random.choice(audio_files)
        return os.path.join(audio_cache_dir, selected_file)
    
    except Exception as e:
        logger.error(f"Error selecting filler audio: {e}")
        return None


# ========== VALIDATION UTILITIES ==========

def validate_question_data(question_data: Dict[str, Any]) -> bool:
    """
    Validate question data structure.
    
    Args:
        question_data: Question data to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ["id", "title", "difficulty", "description"]
    return all(field in question_data for field in required_fields)


def validate_session_data(session_data: Dict[str, Any]) -> bool:
    """
    Validate session data structure.
    
    Args:
        session_data: Session data to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_sections = ["session_info", "progress", "current_state"]
    return all(section in session_data for section in required_sections)


# ========== LOGGING UTILITIES ==========

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
