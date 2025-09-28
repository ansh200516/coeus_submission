import logging
import os
import re
import shutil
import time
import wave
from contextlib import closing

from deepgram import DeepgramClient
from dotenv import load_dotenv

# Import from the new centralized config
from config import (
    AUDIO_CACHE_DIR,
    DEEPGRAM_SPEAK_OPTIONS,
    LOG_FORMAT,
    LOG_LEVEL,
)

load_dotenv()


# ========== MAIN SCRIPT ==========


def is_valid_wav(file_path: str) -> bool:
    """Check if a file is a valid, non-empty WAV file."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 2048:
        return False
    try:
        with closing(wave.open(file_path, "rb")) as wf:
            return wf.getnframes() > 0
    except wave.Error:
        return False


def main():
    """Generates and caches audio files for long, combined filler words."""
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
    logger = logging.getLogger(__name__)

    logger.info("Initializing audio cache generator for COMBINATION fillers...")

    # 1. Define base words for combinations
    hesitations = ["mmhmm...", "ahhmmm...", "umm...", "uh...", "hmm..."]
    acknowledgements = ["okay...", "right...", "I see...", "alright..."]
    continuations = ["so...", "well..."]
    pauses = [" . . . "]

    # 2. Generate 2-word and 3-word combinations
    generated_fillers = set()
    for h in hesitations:
        for p in pauses:
            for a in acknowledgements:
                generated_fillers.add(f"{h}{p}{a}")  # e.g., "um... ... okay..."

    for a in acknowledgements:
        for p in pauses:
            for c in continuations:
                generated_fillers.add(f"{a}{p}{c}")  # e.g., "right... . . . so..."

    # 3. Add some of the original elongated words for variety
    original_long_fillers = [
        "riiiight... ...",
        "ooookay... ...",
        "weeeell... ...",
        "sooo... ...",
        "hmmmmm... ...",
        "uhhhhh... ...",
        "ummmm... ...",
        "ahhhh... ...",
    ]
    for filler in original_long_fillers:
        generated_fillers.add(filler)

    all_long_fillers = list(generated_fillers)

    try:
        deepgram = DeepgramClient()
        speak_client = deepgram.speak.rest.v("1")
    except Exception as e:
        logger.error(f"Failed to initialize Deepgram client: {e}")
        return

    if not os.path.exists(AUDIO_CACHE_DIR):
        logger.info(f"Creating cache directory at: {AUDIO_CACHE_DIR}")
        os.makedirs(AUDIO_CACHE_DIR)

    for word in all_long_fillers:
        safe_name = re.sub(r"[^a-zA-Z0-9 ]", "", word).replace(" ", "_").lower()
        filename = f"{safe_name}.wav"
        output_path = os.path.join(AUDIO_CACHE_DIR, filename)
        temp_path = f"{output_path}.tmp"

        if os.path.exists(output_path):
            logger.info(f"Audio for '{word}' already exists. Skipping.")
            continue

        try:
            logger.info(f"Generating audio for '{word}' -> {output_path}")
            time.sleep(1.5)  # Avoid rate limiting
            # Use the centralized speak options
            speak_client.save(temp_path, {"text": word}, DEEPGRAM_SPEAK_OPTIONS)

            if is_valid_wav(temp_path):
                shutil.move(temp_path, output_path)
                logger.info(f"Successfully saved and verified {output_path}")
            else:
                logger.error(f"Generated file for '{word}' is invalid. Deleting.")
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        except Exception as e:
            logger.error(f"Failed to generate audio for '{word}': {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)

    logger.info("Audio cache generation complete.")


if __name__ == "__main__":
    main()
