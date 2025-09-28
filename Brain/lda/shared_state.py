import asyncio


class AudioState:
    """A simple, shared state object to signal when TTS is active."""

    def __init__(self):
        self._is_speaking = asyncio.Event()

    def set_speaking(self, is_speaking: bool):
        """Set the speaking state."""
        if is_speaking:
            self._is_speaking.set()
        else:
            self._is_speaking.clear()

    def is_speaking(self) -> bool:
        """Check if TTS is currently active."""
        return self._is_speaking.is_set()
