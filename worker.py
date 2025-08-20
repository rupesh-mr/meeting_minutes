import time
import os
import soundfile as sf
import whisper
from recorder import chunk_paths
from utils.diarizer import diarize_audio, merge_transcript_with_speakers
from utils.summarizer import generate_minutes

transcribed_chunks = []
model = whisper.load_model("small")

PROCESSED_DIR = "processed"
os.makedirs(PROCESSED_DIR, exist_ok=True)

def background_worker():
    print("Background worker started.")
    processed = set()
    while True:
        new_chunks = [p for p in chunk_paths if p not in processed]
        if not new_chunks:
            time.sleep(2)
            if os.getenv("RECORDING_STOPPED") == "1":
                break
            continue

        for path in new_chunks:
            print(f"Processing {path}...")
            audio, sr = sf.read(path)
            mono_audio = audio.mean(axis=1)
            temp_path = path.replace("output", PROCESSED_DIR)
            sf.write(temp_path, mono_audio, sr)

            result = model.transcribe(temp_path, word_timestamps=False)
            text_segments = result["segments"]
            diarized = diarize_audio(temp_path)
            final_text = merge_transcript_with_speakers(text_segments, diarized)

            transcribed_chunks.append(final_text)
            processed.add(path)
            print(f"Finished: {path}")
    print("Worker done.")
