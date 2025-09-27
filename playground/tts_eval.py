#!/usr/bin/env python3
"""
TTS Engine Latency Evaluation

Measures time to first audio (TTFA) for different TTS engines:
- OpenAI
- Azure
- gTTS
- Deepgram

Usage: python tts_eval.py
"""

import time
import asyncio
import statistics
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import logging

# Add rtts directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Suppress verbose logging for cleaner output
logging.getLogger("RealtimeTTS").setLevel(logging.WARNING)
logging.getLogger("azure.core").setLevel(logging.WARNING)


class TTSEvaluator:
    def __init__(self):
        self.results = {}
        self.test_text = (
            "Hello, this is a test of the text to speech engine latency measurement."
        )

    def measure_openai_latency(self, iterations=3) -> List[float]:
        """Measure OpenAI TTS latency using main_openai.py"""
        print("Testing OpenAI TTS...")
        latencies = []

        for i in range(iterations):
            try:
                import main_openai
                from RealtimeTTS import TextToAudioStream, OpenAIEngine

                # Capture the timing from the engine
                first_audio_time = None
                start_time = time.time()

                def test_generator():
                    yield self.test_text

                # Create engine and stream like main_openai.py
                engine = OpenAIEngine()
                stream = TextToAudioStream(engine)

                # Override the on_audio_stream_start callback to capture timing
                def on_audio_start():
                    nonlocal first_audio_time
                    if first_audio_time is None:
                        first_audio_time = time.time()

                stream.on_audio_stream_start = on_audio_start

                # Start timing and play
                start_time = time.time()
                stream.feed(test_generator()).play(muted=True)

                if first_audio_time:
                    latency = first_audio_time - start_time
                else:
                    latency = time.time() - start_time

                latencies.append(latency)
                print(f"  Run {i+1}: {latency:.3f}s")

                engine.shutdown()

            except Exception as e:
                print(f"  Run {i+1}: Error - {e}")

        return latencies

    def measure_azure_latency(self, iterations=3) -> List[float]:
        """Measure Azure TTS latency using main_azure.py"""
        print("Testing Azure TTS...")
        latencies = []

        for i in range(iterations):
            try:
                import main_azure

                # Create a test text stream
                def test_text_stream():
                    yield self.test_text

                # Capture timing by overriding the stream_tts function behavior
                first_audio_time = None
                start_time = time.time()

                # Create TTS instance like main_azure.py
                tts = main_azure.RealtimeTTS(voice="Ava", debug=False)

                # Override the on_audio_stream_start callback
                def on_audio_start():
                    nonlocal first_audio_time
                    if first_audio_time is None:
                        first_audio_time = time.time()

                tts.stream.on_audio_stream_start = on_audio_start

                # Start timing
                start_time = time.time()

                # Feed and play the text (muted)
                tts.stream.feed(self.test_text).play(muted=True)

                if first_audio_time:
                    latency = first_audio_time - start_time
                else:
                    latency = time.time() - start_time

                latencies.append(latency)
                print(f"  Run {i+1}: {latency:.3f}s")

                tts.shutdown()

            except Exception as e:
                print(f"  Run {i+1}: Error - {e}")

        return latencies

    def measure_gtts_latency(self, iterations=3) -> List[float]:
        """Measure gTTS latency using main_gtts.py"""
        print("Testing gTTS...")
        latencies = []

        for i in range(iterations):
            try:
                import main_gtts
                from RealtimeTTS import TextToAudioStream, GTTSEngine, GTTSVoice

                # Create engine and stream like main_gtts.py
                voice = GTTSVoice(speed=1.3)
                engine = GTTSEngine(voice)
                stream = TextToAudioStream(engine)

                first_audio_time = None
                start_time = time.time()

                def on_audio_start():
                    nonlocal first_audio_time
                    if first_audio_time is None:
                        first_audio_time = time.time()

                stream.on_audio_stream_start = on_audio_start

                def test_generator():
                    yield self.test_text

                start_time = time.time()
                stream.feed(test_generator()).play(muted=True)

                if first_audio_time:
                    latency = first_audio_time - start_time
                else:
                    latency = time.time() - start_time

                latencies.append(latency)
                print(f"  Run {i+1}: {latency:.3f}s")

            except Exception as e:
                print(f"  Run {i+1}: Error - {e}")

        return latencies

    async def measure_deepgram_latency(self, iterations=3) -> List[float]:
        """Measure Deepgram TTS latency using main_deepgram.py"""
        print("Testing Deepgram TTS...")
        latencies = []

        for i in range(iterations):
            try:
                import main_deepgram

                # Create TTS instance like main_deepgram.py
                tts = main_deepgram.DeepgramTTS()

                # Connect to Deepgram
                if not await tts.connect():
                    print(f"  Run {i+1}: Error - Failed to connect")
                    continue

                first_audio_time = None
                start_time = time.time()

                # Override the listen_for_audio method to capture first audio timing
                original_listen = tts.listen_for_audio

                async def timed_listen_for_audio():
                    nonlocal first_audio_time
                    try:
                        async for message in tts.websocket:
                            if isinstance(message, bytes) and first_audio_time is None:
                                first_audio_time = time.time()
                                break
                            elif not isinstance(message, bytes):
                                try:
                                    data = json.loads(message)
                                    if data.get("type") == "Close":
                                        break
                                except:
                                    pass
                    except Exception as e:
                        pass

                # Start listening task
                listen_task = asyncio.create_task(timed_listen_for_audio())

                # Send text and measure
                start_time = time.time()
                await tts.send_text(self.test_text)

                # Wait for first audio or timeout
                try:
                    await asyncio.wait_for(listen_task, timeout=5.0)
                except asyncio.TimeoutError:
                    pass

                # Close connection
                await tts.close()

                if first_audio_time:
                    latency = first_audio_time - start_time
                else:
                    latency = time.time() - start_time

                latencies.append(latency)
                print(f"  Run {i+1}: {latency:.3f}s")

            except Exception as e:
                print(f"  Run {i+1}: Error - {e}")

        return latencies

    def calculate_stats(self, latencies: List[float]) -> Dict[str, float]:
        """Calculate statistics for latency measurements"""
        if not latencies:
            return {"mean": 0, "median": 0, "min": 0, "max": 0, "std": 0}

        return {
            "mean": statistics.mean(latencies),
            "median": statistics.median(latencies),
            "min": min(latencies),
            "max": max(latencies),
            "std": statistics.stdev(latencies) if len(latencies) > 1 else 0,
        }

    async def run_evaluation(self, iterations=3):
        """Run complete evaluation of all TTS engines"""
        print(f"TTS Engine Latency Evaluation")
        print(f"Test text: {self.test_text}")
        print(f"Iterations per engine: {iterations}")
        print("=" * 60)

        # Test each engine
        engines = {
            "openai": self.measure_openai_latency,
            "azure": self.measure_azure_latency,
            "gtts": self.measure_gtts_latency,
            "deepgram": self.measure_deepgram_latency,
        }

        for engine_name, test_func in engines.items():
            try:
                if engine_name == "deepgram":
                    latencies = await test_func(iterations)
                else:
                    latencies = test_func(iterations)

                stats = self.calculate_stats(latencies)
                self.results[engine_name] = {"latencies": latencies, "stats": stats}

                print(
                    f"  Stats: mean={stats['mean']:.3f}s, median={stats['median']:.3f}s, min={stats['min']:.3f}s, max={stats['max']:.3f}s"
                )
                print()

            except Exception as e:
                print(f"  Failed to test {engine_name}: {e}")
                self.results[engine_name] = {"error": str(e)}
                print()

        self.print_summary()
        self.save_results()

    def print_summary(self):
        """Print summary of results"""
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)

        # Sort by median latency
        valid_results = {k: v for k, v in self.results.items() if "stats" in v}
        sorted_engines = sorted(
            valid_results.items(), key=lambda x: x[1]["stats"]["median"]
        )

        print(
            f"{'Engine':<12} {'Median (s)':<12} {'Mean (s)':<12} {'Min (s)':<12} {'Max (s)':<12}"
        )
        print("-" * 60)

        for engine, data in sorted_engines:
            stats = data["stats"]
            print(
                f"{engine:<12} {stats['median']:<12.3f} {stats['mean']:<12.3f} {stats['min']:<12.3f} {stats['max']:<12.3f}"
            )

        if sorted_engines:
            fastest = sorted_engines[0]
            print(
                f"\nFastest engine: {fastest[0]} (median: {fastest[1]['stats']['median']:.3f}s)"
            )

    def save_results(self):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tts_evaluation_{timestamp}.json"

        output = {
            "timestamp": timestamp,
            "test_text": self.test_text,
            "results": self.results,
        }

        with open(filename, "w") as f:
            json.dump(output, f, indent=2)

        print(f"\nResults saved to {filename}")


async def main():
    evaluator = TTSEvaluator()
    await evaluator.run_evaluation(iterations=5)


if __name__ == "__main__":
    asyncio.run(main())
