import google.generativeai as genai
import os
import json
import re

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-pro")

def generate_minutes(transcript: str) -> dict:
    prompt = f"""
You are an AI meeting assistant.

Given the transcript below, extract and return a valid JSON object with:
- "summary": string
- "action_items": list of strings
- "decisions": list of strings
- "dates": list of natural language strings like "Friday", "August 5th", or "next Tuesday at 3pm"

Return only valid JSON. Do not include markdown (like ```json), explanations, or headings.

Transcript:
\"\"\"
{transcript}
\"\"\"
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # 💡 Remove Markdown wrapper if present
    if raw.startswith("```json"):
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print("Failed to parse Gemini JSON:", e)
        print("Raw Gemini output:", repr(raw))
        return {"summary": "No valid response from Gemini", "action_items": [], "decisions": [], "dates": []}