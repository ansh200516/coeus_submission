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
    Removes common markdown formatting characters from a string.
    Simply removes all asterisks, underscores, and backticks.
    """
    # Remove all asterisks
    text = text.replace("*", "")
    # Remove underscores (but keep spaces)
    text = re.sub(r"_", "", text)
    # Remove backticks
    text = text.replace("`", "")
    # Clean up any extra spaces that might be left
    text = re.sub(r"\s+", " ", text).strip()
    return text