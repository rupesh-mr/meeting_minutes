from datetime import datetime
from worker import transcribed_chunks
from utils.summarizer import generate_minutes
from utils.db import save_minutes
from utils.calendar import add_event
import dateparser


def finalize_session():
    print("Finalizing meeting...")
    full_transcript = "\n".join(transcribed_chunks)

    if not full_transcript.strip():
        print("No transcript to save.")
        return

    minutes = generate_minutes(full_transcript)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    raw_dates = minutes.get("dates", [])
    parsed_dates = []
    for raw_date in raw_dates:
        dt = dateparser.parse(raw_date)
        if dt:
            parsed_dates.append(dt.date().isoformat())  
        else:
            print(f"Could not parse date: '{raw_date}', saving raw.")
            parsed_dates.append(raw_date)  

    save_minutes(
        meeting_datetime=now,
        summary=minutes.get("summary", ""),
        action_items=minutes.get("action_items", []),
        decisions=minutes.get("decisions", []),
        dates=parsed_dates,
        diarized_transcript=full_transcript
    )

    for date in parsed_dates:
        try:
            add_event("Meeting Follow-up", date)
        except Exception as e:
            print(f"Failed to add calendar event for {date}: {e}")

    print("Final meeting summary saved to database.")
