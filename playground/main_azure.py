import os
import random
from RealtimeTTS import TextToAudioStream, AzureEngine
from dotenv import load_dotenv

load_dotenv()


class RealtimeTTS:
    def __init__(self, voice="Ava", debug=False):
        self.engine = AzureEngine(
            os.environ["AZURE_SPEECH_KEY"],
            os.environ["AZURE_SPEECH_REGION"],
            debug=debug,
            audio_format="riff-48khz-16bit-mono-pcm",
        )
        self.stream = TextToAudioStream(self.engine, log_characters=True)
        self.voice = voice
        self.engine.set_voice(voice)

    def feed_text_stream(self, text_stream):
        all_text = "".join(text_stream)
        if all_text.strip():
            self.stream.feed(all_text).play()

    def shutdown(self):
        self.engine.shutdown()


def stream_tts_with_fillers(text_stream, voice="Ava", debug=False):
    tts = RealtimeTTS(voice=voice, debug=debug)
    try:
        tts.feed_text_stream(text_stream)
    finally:
        tts.shutdown()


def llm_text_generator():
    text_stream = [
        "Hey guys! These here are realtime spoken sentences based on local text synthesis. ",
        "With a local, neuronal, cloned voice. So every spoken sentence sounds unique.",
    ]

    for text in text_stream:
        yield text


if __name__ == "__main__":
    try:
        stream_tts_with_fillers(llm_text_generator(), debug=True)
    except Exception as e:
        print(f"Error: {e}")
