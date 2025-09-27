import pyaudio
import numpy as np

# ====================================================================
# This script requires numpy and pyaudio.
# You can install them with:
# pip install numpy pyaudio
# ====================================================================

# --- Configuration ---
SAMPLE_RATE = 44100  # Samples per second
FREQUENCY = 440      # Hz, standard A4 pitch
DURATION = 1.0       # seconds
VOLUME = 0.5         # range [0.0, 1.0]

def generate_beep_data(freq, duration, sample_rate, volume):
    """Generates audio data for a sine wave beep."""
    # Generate an array of time points
    t = np.linspace(0., duration, int(sample_rate * duration), endpoint=False)
    
    # Generate the sine wave
    # Formula: amplitude * sin(2 * pi * frequency * time)
    amplitude = 32767 * volume
    data = amplitude * np.sin(2. * np.pi * freq * t)
    
    # Convert to 16-bit integers, which PyAudio expects
    return data.astype(np.int16)

def play_beep(data, sample_rate):
    """Plays the generated beep data using PyAudio."""
    p = pyaudio.PyAudio()

    try:
        stream = p.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=sample_rate,
                        output=True)

        print(f"Playing a {DURATION}-second beep at {FREQUENCY} Hz...")
        # PyAudio expects bytes, so convert the numpy array to bytes
        stream.write(data.tobytes())

        stream.stop_stream()
        stream.close()
        print("Done.")

    finally:
        p.terminate()

if __name__ == "__main__":
    print("Generating beep sound...")
    beep_data = generate_beep_data(FREQUENCY, DURATION, SAMPLE_RATE, VOLUME)
    play_beep(beep_data, SAMPLE_RATE)
