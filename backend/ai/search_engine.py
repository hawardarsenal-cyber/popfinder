import json
import os
import datetime
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

    today = datetime.date.today().isoformat()

    prompt = f"""
You are PopFinder, a UK event-intelligence engine.

Your job is to generate **upcoming** (future-dated) pop-ups, markets, expos,
festivals, fairs, county shows and high-footfall opportunities.

USER QUERY:
- Region: {region}
- Keywords: {keywords}
- Today's date: {today}

CONTEXT SOURCES:
- Core Rules: {rules_text}
- User Notes: {notes_text}
- Pinned Events (avoid duplicates): {pins_text}

REQUIREMENTS:
1. ALL generated events must have dates in the **future**, not older than today.
2. ALWAYS include events relevant to:
   - Excel London
   - Olympia London
   - NEC Birmingham
   - Alexandra Palace
   - Large seasonal fairs
   - County shows (Kent, Sussex, Essex, Surrey etc.)
   - Major UK markets with vendor pop-up access
3. If no info exists, **infer plausible upcoming dates**.
4. Provide events for next **90 days** unless user keywords override.
5. The list must be diverse and not repetitive.
6. Return ONLY valid JSON list, no explanation.

Event object structure:
{{
    "title": "",
    "date": "",
    "location": "",
    "description": "",
    "url": ""
}}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=1200
    )

    try:
        return json.loads(response.output_text)
    except:
        return []
