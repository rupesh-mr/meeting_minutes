import sounddevice as sd
import soundfile as sf
import numpy as np
import os
from threading import Event

CHUNK_DURATION = 30  # seconds
SAMPLE_RATE = 16000
CHANNELS = 3
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Input device index (e.g., Aggregate Device)
sd.default.device = (4, None)  # Replace 4 with your input device index

chunk_paths = []
stop_event = Event()
chunk_counter = 0

def record_chunks():
    global chunk_counter
    while not stop_event.is_set():
        print(f"🎙 Recording chunk {chunk_counter}...")
        chunk = sd.rec(int(CHUNK_DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
        sd.wait()

        path = os.path.join(OUTPUT_DIR, f"chunk_{chunk_counter}.wav")
        sf.write(path, chunk, SAMPLE_RATE)
        chunk_paths.append(path)

        print(f"✅ Saved: {path}")
        chunk_counter += 1