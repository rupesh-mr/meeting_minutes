# Meeting Minutes Recorder & Summarizer

A web-based tool to record, diarize, transcribe, and summarize meetings.  
The system captures audio in real-time, processes it in 30-second chunks, applies speaker diarization and transcription, and generates a complete transcript with summaries after the meeting ends.  
Each transcript is tagged with the meeting date/time  
Additionally, the system detects any future dates mentioned during the meeting conversation and generates calendar links (Google Calendar) for them.

---

## Features

- Continuous recording in 30-second segments.  
- Automatic speaker diarization.  
- Transcription using speech-to-text models.  
- Progress bar showing transcription status after recording stops.  
- Database storage with timestamps.  
- Calendar integration:   
  - Automatically generate calendar event links for any dates mentioned inside the meeting.  
- Summarization for concise meeting notes.

---

## Tech Stack

- **Backend**: Python (Flask)  
- **Audio Processing**: PyDub / sounddevice / ffmpeg  
- **ASR**: OpenAI Whisper / faster-whisper (configurable)  
- **Diarization**: pyannote.audio  
- **Frontend**: HTML + JavaScript  
- **Database**: SQLite (with timestamp and calendar fields)  

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/meeting-minutes.git
   cd meeting-minutes
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate      # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install ffmpeg if not already available:
   - Mac: `brew install ffmpeg`  
   - Ubuntu: `sudo apt install ffmpeg`  
   - Windows: [download ffmpeg](https://ffmpeg.org/download.html)

---

## Usage

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open the application in your browser at:
   ```
   http://127.0.0.1:5000
   ```

3. Start recording to capture audio in 30-second chunks. Each chunk is processed in the background (diarization + transcription).

4. Stop recording to finish processing. The progress bar will indicate transcription status. Once complete:  
   - The transcript and summary are stored in the database.  
   - The entry is timestamped with date and time.   
   - Any dates mentioned within the meeting are also extracted and calendar links are created for them.

---

## Project Structure

```
meeting-minutes/
│── app.py                 # Flask backend
│── static/                # Frontend JS/CSS
│── templates/             # HTML templates
│── transcriber.py         # Handles ASR + diarization
│── summarizer.py          # Generates meeting summaries
│── database.py            # SQLite storage (timestamps + calendar links)
│── calendar_utils.py      # Calendar event link generation
│── requirements.txt       # Dependencies
│── README.md              # Documentation
```
---
## License

MIT License © 2025 Mallireddy Rupesh
