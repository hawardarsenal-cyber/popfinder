import json
import os
from openai import OpenAI

client = OpenAI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_FILE = os.path.join(BASE_DIR, "rules.txt")
PINS_FILE = os.path.join(BASE_DIR, "pinned.json")
NOTES_FILE = os.path.join(BASE_DIR, "notes.txt")


def load_file(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def smart_event_search(region: str, keywords: str):
    rules_text = load_file(RULES_FILE)
    notes_text = load_file(NOTES_FILE)
    pins_text = load_file(PINS_FILE)

    prompt = f"""
You are PopFinder, an assistant generating pop-up opportunities, markets, events
and high-footfall hotspots in the UK.

USER QUERY:
- Region: {region}
- Keywords: {keywords}

CONTEXT SOURCES:
- Rules: {rules_text}
- Notes: {notes_text}
- Pinned Events: {pins_text}

TASK:
Generate a JSON array of events.
Each event must be structured like this:
{{
    "title": "...",
    "date": "...",
    "location": "...",
    "description": "...",
    "url": "https://..."
}}

If unsure, estimate or infer likely details.
Return ONLY JSON.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=1000
    )

    try:
        return json.loads(response.output_text)
    except:
        return []
