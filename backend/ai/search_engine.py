import json
import requests
import datetime
from openai import OpenAI

client = OpenAI()

# ----------------------------------------------------
# REMOTE FILE LOCATIONS (FTP PUBLIC URLs)
# ----------------------------------------------------
RULES_URL = "https://pos.kartingcentral.co.uk/popfinder/rules.txt"
NOTES_URL = "https://pos.kartingcentral.co.uk/popfinder/notes.txt"
PINS_URL  = "https://pos.kartingcentral.co.uk/popfinder/pins.json"
SEED_URL  = "https://pos.kartingcentral.co.uk/popfinder/seed_events.json"


# ----------------------------------------------------
# Load remote files safely
# ----------------------------------------------------
def load_remote(url):
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.text
    except:
        return ""


def load_json_remote(url):
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.json()
    except:
        return []


# ----------------------------------------------------
# MAIN SEARCH ENGINE
# ----------------------------------------------------
def smart_event_search(region: str, keywords: str):

    # Load remote contextual files
    rules_text = load_remote(RULES_URL)
    notes_text = load_remote(NOTES_URL)
    pins_json  = load_json_remote(PINS_URL)
    seeds_json = load_json_remote(SEED_URL)

    today = datetime.date.today().isoformat()

    # Build GPT prompt
    prompt = f"""
You are PopFinder, the UK's vendor opportunity engine.

USER QUERY:
- Region: {region}
- Keywords: {keywords}
- Today: {today}

CONTEXT:
- Rules: {rules_text}
- Notes: {notes_text}
- Pinned (avoid duplicates): {json.dumps(pins_json)}
- Seed Events (always consider these): {json.dumps(seeds_json)}

TASK:
Combine seed events + inferred upcoming events.

RULES:
1. ALL events must be future-dated after today.
2. Must include major venues:
   - ExCeL, Olympia, NEC, Ally Pally, Kent Showground, Bluewater.
3. Include markets, fairs, expos, food festivals, county shows.
4. Infer realistic dates if uncertain.
5. Output ONLY JSON array, no commentary.

EVENT FORMAT:
{{
  "title": "",
  "date": "",
  "location": "",
  "description": "",
  "url": "",
  "category": "",
  "footfall_score": 0,
  "vendor_fit_score": 0
}}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=1600
    )

    try:
        events = json.loads(response.output_text)
    except:
        return seeds_json  # safe fallback

    # Filter out past dates if included by mistake
    return filter_future_events(events)


# ----------------------------------------------------
# Event date filtering
# ----------------------------------------------------
def filter_future_events(events):
    today = datetime.date.today()
    valid_events = []

    for ev in events:
        try:
            date_str = ev.get("date", "").split(" ")[0]
            date_obj = datetime.date.fromisoformat(date_str)
            if date_obj >= today:
                valid_events.append(ev)
        except:
            continue

    return valid_events
