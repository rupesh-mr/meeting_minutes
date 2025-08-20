import sounddevice as sd
import numpy as np
import whisper
import soundfile as sf
import os
from datetime import datetime
from utils.summarizer import generate_minutes
from utils.db import init_db, save_minutes
from utils.calendar import add_event
from utils.diarizer import diarize_audio, merge_transcript_with_speakers

DURATION = 10
SAMPLE_RATE = 16000
CHANNELS = 3
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

sd.default.device = ("MEETMIC", None)

model = whisper.load_model("small")

init_db()

def record_audio():
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
    sd.wait()
    return audio

def preprocess(audio):
    return audio.mean(axis=1)

def transcribe(audio_data):
    audio_data = (audio_data * 32767).astype(np.int16)
    temp_wav = os.path.join(OUTPUT_DIR, "temp.wav")
    sf.write(temp_wav, audio_data, SAMPLE_RATE)

    result = model.transcribe(temp_wav, word_timestamps=False)
    text_segments = result['segments']

    diarized_segments = diarize_audio(temp_wav)

    diarized_text = merge_transcript_with_speakers(text_segments, diarized_segments)
    print("Diarized Transcript:\n", diarized_text)

    return diarized_text

while True:
    try:
        raw_audio = record_audio()
        audio = preprocess(raw_audio)
        sf.write("last_chunk.wav", audio, SAMPLE_RATE)

        transcript = transcribe(audio)
        print("Transcript:", transcript)

        minutes = generate_minutes(transcript)
        print("Summary:", minutes.get("summary", ""))

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_minutes(
            meeting_datetime=now,
            summary=minutes.get("summary", ""),
            action_items=minutes.get("action_items", []),
            decisions=minutes.get("decisions", []),
            dates=minutes.get("dates", []),
            diarized_transcript=transcript
        )
        print("Meeting minutes saved to database.")
        for date in minutes.get("dates", []):
            add_event("Meeting Follow-up", date)

    except KeyboardInterrupt:
        print("\nStopped by user.")
        break
