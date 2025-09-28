import logging
import os
from deepgram import SpeakOptions

# ========== SHARED CONFIGURATION ==========

# --- Logging ---
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# --- Interview Flow ---
LISTENING_WINDOW = 15  # Seconds
LIE_CONFIDENCE_THRESHOLD = 0.6
MAX_INTERVIEW_DURATION = 20  # 10 minutes

# --- Audio ---
_config_dir = os.path.dirname(os.path.abspath(__file__))
AUDIO_CACHE_DIR = os.path.join(_config_dir, "audio_cache")
SAMPLE_RATE = 24000

# --- Deepgram Models ---
# Use the same model for both live TTS and cached audio to ensure a consistent voice
TTS_MODEL = "aura-2-thalia-en"
STT_MODEL = "nova-2"

# Centralized SpeakOptions for consistency
DEEPGRAM_SPEAK_OPTIONS = SpeakOptions(
    model=TTS_MODEL,
    encoding="linear16",
    container="wav",
    sample_rate=SAMPLE_RATE,
)

# Words for generating cached filler audio
FILLER_WORDS = [
    # Core fillers
    "um... ...",
    "uh... ...",
    "hmm... ...",
    "mmm... ...",
    "ah... ...",
    "oh... ...",
    "er... ...",
    "right... ...",
    "okay... ...",
    "alright... ...",
    "I see... ...",
    "well... ...",
    "so... ...",
    # Extended fillers with long pauses
    "um. . . . . .",
    "uh. . . . . .",
    "hmm. . . . . .",
    "mmm. . . . . .",
    "ah. . . . . .",
    "right. . . . . .",
    "okay. . . . . .",
    "alright. . . . . .",
    # Elongated words mimicking hesitation
    "riiiight... ...",
    "ooookay... ...",
    "weeeell... ...",
    "sooo... ...",
    "hmmmmm... ...",
    "uhhhhh... ...",
    "ummmm... ...",
    "ahhhh... ...",
    # Combinations
    "um... . . . okay... ...",
    "hmm... ... I see... ...",
    "right... . . . so... ...",
    "well... ... uh... ...",
    "mmm... ... alright... ...",
]
