import os
import re
from typing import Optional


def find_project_root(marker=".git") -> Optional[str]:
    """Finds the project root by searching upwards for a marker."""
    path = os.path.abspath(os.path.dirname(__file__))
    while True:
        if os.path.exists(os.path.join(path, marker)):
            return path
        parent = os.path.dirname(path)
        if parent == path:
            return None
        path = parent

def sanitize_llm_json_output(text: str) -> str:
    """
    Extracts a JSON string from a text that might contain markdown code blocks
    and other conversational text.
    """
    # Find JSON wrapped in markdown code blocks (e.g., ```json ... ```)
    match = re.search(r"```(?:json)?\s*({.*?})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)

    # If no markdown block, find the first '{' and last '}' as a fallback
    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return text[start:end]
    except ValueError:
        # If no JSON structure is found, return the original text, stripped.
        # The parser will likely fail, but this provides a last-resort fallback.
        return text.strip()


def strip_markdown(text: str) -> str:
    """
    Removes common markdown formatting (like **, *, _) from a string.
    """
    # Remove bold and italics
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)
    # Remove inline code backticks
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text