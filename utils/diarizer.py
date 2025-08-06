import os
from pyannote.audio import Pipeline
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization@2.1",
    use_auth_token=os.getenv("HF_TOKEN")
)

def diarize_audio(audio_path):
    diarization = pipeline(audio_path)
    segments = []

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })

    return segments

def merge_transcript_with_speakers(whisper_segments, diarization_segments):
    result = []

    for ws in whisper_segments:
        ws_start = ws.get('start')
        ws_end = ws.get('end')
        text = ws.get('text', '').strip()

        # Default to 'Unknown' if no matching segment
        speaker = "Unknown"

        # Match by overlap — more robust than just `ws_start in [start, end]`
        for d in diarization_segments:
            dia_start = d['start']
            dia_end = d['end']
            if ws_start < dia_end and ws_end > dia_start:
                speaker = d['speaker']
                break

        result.append(f"[{speaker}]: {text}")

    return "\n".join(result)
