# import sounddevice as sd
# import numpy as np
# import whisper
# import time
# import os
# import soundfile as sf
# from utils.summarizer import generate_minutes
# from utils.db import init_db, save_minutes
# from datetime import datetime
# from utils.calendar import add_event

# sd.default.device = (6, None)  # (input, output)
# CHANNELS = 2  # Because Aggregate is usually stereo


# init_db()

# model = whisper.load_model("base")
# OUTPUT_DIR = "output"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# SAMPLE_RATE = 16000
# DURATION = 10  # seconds
# CHANNELS = 1

# def record_audio():
#     print("Recording...")
#     audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
#     sd.wait()
#     return audio.flatten()

# def transcribe(audio_data):
#     audio_data = (audio_data * 32767).astype(np.int32)
#     temp_wav = os.path.join(OUTPUT_DIR, "temp.wav")
#     sf.write(temp_wav, audio_data, SAMPLE_RATE)
#     result = model.transcribe(temp_wav)
#     return result["text"]

# if __name__ == "__main__":
#     print("Starting live transcription...")
#     with open(os.path.join(OUTPUT_DIR, "live_minutes.md"), "w") as f:
#         f.write("# Live Meeting Minutes\n\n")

#     while True:
#         try:
#             audio = record_audio()
#             sf.write("test.wav", audio, SAMPLE_RATE)
#             text = transcribe(audio)
#             print("Transcribed:\n", text)
#             minutes = generate_minutes(text)
#             print(minutes)
#             now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#             save_minutes(
#                 meeting_datetime=now,
#                 summary=minutes.get("summary", ""),
#                 action_items=minutes.get("action_items", []),
#                 decisions=minutes.get("decisions", []),
#                 dates=minutes.get("dates", [])
#             )
#             for date in minutes.get("dates", []):
#                 add_event("Meeting Follow-up", date)
#             print(minutes.get("dates", []))

#             print("✅ Meeting minutes saved to database.")
#             with open(os.path.join(OUTPUT_DIR, "live_minutes.md"), "a") as f:
#                 f.write(f"- {text}\n")
#         except KeyboardInterrupt:
#             print("\nStopped.")
#             break

import sounddevice as sd
import numpy as np
import whisper
import soundfile as sf
import os
from datetime import datetime
from utils.summarizer import generate_minutes
from utils.db import init_db, save_minutes
from utils.calendar import add_event  # optional
from utils.diarizer import diarize_audio, merge_transcript_with_speakers

DURATION = 10  # seconds
SAMPLE_RATE = 16000
CHANNELS = 3 # Stereo: mic + Google Meet
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 👉 Set input device to your Aggregate Device
sd.default.device = (4, None)  # Replace "MeetMic" with your Aggregate name

print("🔁 Initializing Whisper...")
model = whisper.load_model("small")

init_db()

def record_audio():
    print("🎙 Recording...")
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
    sd.wait()
    print("🎧 Done recording.")
    return audio

def preprocess(audio):
    # Stereo to mono
    mono_audio = audio.mean(axis=1)
    return mono_audio

def transcribe(audio_data):
    # Save temp WAV
    audio_data = (audio_data * 32767).astype(np.int16)
    temp_wav = os.path.join(OUTPUT_DIR, "temp.wav")
    sf.write(temp_wav, audio_data, SAMPLE_RATE)

    # 1. Transcribe
    result = model.transcribe(temp_wav, word_timestamps=False)
    text_segments = result['segments']  # [{'start': ..., 'end': ..., 'text': ...}]

    # 2. Diarize
    diarized_segments = diarize_audio(temp_wav)

    # 3. Merge
    diarized_text = merge_transcript_with_speakers(text_segments, diarized_segments)
    print("🔊 Diarized Transcript:\n", diarized_text)

    return diarized_text

while True:
    try:
        raw_audio = record_audio()
        audio = preprocess(raw_audio)
        sf.write("last_chunk.wav", audio, SAMPLE_RATE)

        transcript = transcribe(audio)
        print("📝 Transcript:", transcript)

        minutes = generate_minutes(transcript)
        print("📋 Summary:", minutes.get("summary", ""))

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_minutes(
            meeting_datetime=now,
            summary=minutes.get("summary", ""),
            action_items=minutes.get("action_items", []),
            decisions=minutes.get("decisions", []),
            dates=minutes.get("dates", []),
            diarized_transcript=transcript  # ✅ Save the full speaker-tagged transcript
        )
        print("✅ Meeting minutes saved to database.")
        for date in minutes.get("dates", []):
            add_event("Meeting Follow-up", date)

    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
        break
