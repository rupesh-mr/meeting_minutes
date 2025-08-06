from flask import Flask, request, jsonify, render_template
import threading
import time
from datetime import datetime
from utils.db import init_db, get_all_meetings, save_minutes
from utils.summarizer import generate_minutes
from utils.diarizer import diarize_audio, merge_transcript_with_speakers
from utils.calendar import add_event as add_to_calendar
import sounddevice as sd
import numpy as np
import whisper
import soundfile as sf
import os
import sqlite3
import queue
import json

app = Flask(__name__)

# Globals
recording = False
processing = False
processed_chunks = []
chunk_queue = queue.Queue()
stop_event = threading.Event()
status_dict = {"status": "idle", "total_chunks": 0, "processed_chunks": 0}

AUDIO_DIR = "chunks"
os.makedirs(AUDIO_DIR, exist_ok=True)
CHUNK_DURATION = 30  # seconds
SAMPLE_RATE = 16000
CHANNELS = 3
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
model = whisper.load_model("small")
sd.default.device = (3, None)
init_db()

def record_loop():
    try:
        print("🎙️ Recording started")
        status_dict["status"] = "recording"
        status_dict["total_chunks"] = 0
        status_dict["processed_chunks"] = 0

        while not stop_event.is_set():
            duration_samples = int(CHUNK_DURATION * SAMPLE_RATE)
            audio = sd.rec(duration_samples, samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32')
            sd.wait()
            chunk = audio.copy()
            chunk_queue.put(chunk)
            if not stop_event.is_set():
                status_dict["total_chunks"] += 1
            else:
                chunk_queue.put(None)
            print(f"✅ Recorded chunk {status_dict['total_chunks']}")

    except Exception as e:
        print(f"❌ Recording error: {e}")
    finally:
        print("🛑 Recording stopped")
        status_dict["status"] = "processing"

def process_chunk_worker():
    idx = 0
    while True:
        chunk = chunk_queue.get()
        if chunk is None:
            # Before breaking, make sure queue is empty
            if chunk_queue.qsize() == 0 :
                break
            else:
                continue  # Still have chunks to process

        try:
            mono = chunk.mean(axis=1)
            chunk_path = f"{OUTPUT_DIR}/chunk_{idx}.wav"
            sf.write(chunk_path, (mono * 32767).astype(np.int16), SAMPLE_RATE)
            result = model.transcribe(chunk_path, word_timestamps=False)
            segments = result['segments']
            diarized = diarize_audio(chunk_path)
            merged = merge_transcript_with_speakers(segments, diarized)
            processed_chunks.append(merged)
            status_dict["processed_chunks"] += 1
            print(f"✅ Processed chunk {idx}")
            idx += 1
        except Exception as e:
            print(f"❌ Error processing chunk: {e}")
    
    

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start():
    global recording, stop_event
    if not recording:
        recording = True
        stop_event.clear()
        threading.Thread(target=record_loop).start()
        threading.Thread(target=process_chunk_worker).start()
    return "", 204

@app.route("/stop", methods=["POST"])
def stop():
    global recording
    if recording:
        stop_event.set() 
        status_dict["total_chunks"] += 1
        def wait_then_process():
            while status_dict["processed_chunks"] < status_dict["total_chunks"]:
                print(f"⏳ Waiting... {status_dict['processed_chunks']}/{status_dict['total_chunks']}")
                time.sleep(1)
            print("🧠 All chunks processed, generating minutes...")
            process_all()
        threading.Thread(target=wait_then_process).start()
        recording = False
    return "", 204

def process_all():
    global processing
    processing = True

    full_transcript = "\n".join(processed_chunks)
    print("✅ Full transcript done")

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
        add_to_calendar("Meeting Follow-up", date)

    processed_chunks.clear()
    status_dict["status"] = "idle"
    processing = False

@app.route("/add_event", methods=["POST"])
def add_event():
    data = request.get_json()
    summary = data.get("summary")
    date = data.get("date")

    if not summary or not date:
        return jsonify({"error": "Missing summary or date"}), 400

    try:
        link = add_to_calendar(summary, date)
        return jsonify({"status": "success", "link": link})
    except Exception as e:
        print(f"❌ Calendar error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/status")
def status():
    return jsonify({
        "status": status_dict["status"],
        "total_chunks": status_dict["total_chunks"],
        "processed_chunks": status_dict["processed_chunks"]
    })

@app.route("/history", methods=["GET"])
def get_history():
    conn = sqlite3.connect("meeting_minutes.db")
    c = conn.cursor()
    c.execute("SELECT meeting_datetime, summary, dates FROM meeting_minutes ORDER BY meeting_datetime DESC")
    rows = c.fetchall()
    conn.close()

    history = []
    for dt, summary, dates_json in rows:
        try:
            dates = json.loads(dates_json) if dates_json else []
        except Exception:
            dates = []
        history.append({
            "datetime": dt,
            "summary": summary,
            "dates": dates
        })
    return jsonify(history)

@app.route("/all", methods=["GET"])
def view_all():
    conn = sqlite3.connect("meeting_minutes.db")
    c = conn.cursor()
    c.execute("SELECT * FROM meeting_minutes ORDER BY meeting_datetime DESC")
    rows = c.fetchall()
    conn.close()

    return render_template("all_entries.html", entries=rows)

if __name__ == "__main__":
    app.run(debug=True)
