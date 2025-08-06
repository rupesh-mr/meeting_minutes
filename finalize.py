from datetime import datetime
from worker import transcribed_chunks
from utils.summarizer import generate_minutes
from utils.db import save_minutes
from utils.calendar import add_event


def finalize_session():
    print("📦 Finalizing meeting...")
    full_transcript = "\n".join(transcribed_chunks)

    if not full_transcript.strip():
        print("⚠️ No transcript to save.")
        return

    minutes = generate_minutes(full_transcript)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_minutes(
        meeting_datetime=now,
        summary=minutes.get("summary", ""),
        action_items=minutes.get("action_items", []),
        decisions=minutes.get("decisions", []),
        dates=minutes.get("dates", []),
        diarized_transcript=full_transcript
    )

    for date in minutes.get("dates", []):
        add_event("Meeting Follow-up", date)

    print("✅ Final meeting summary saved to database.")