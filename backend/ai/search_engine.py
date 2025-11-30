import json
import requests
import datetime
from openai import OpenAI

client = OpenAI()

# ----------------------------------------------------
# REMOTE FILE LOCATIONS (PUBLIC FTP URLs)
# ----------------------------------------------------
BASE_URL = "https://pos.kartingcentral.co.uk/home/download/pos2/pos2/popfinder/backend/data"

RULES_URL = f"{BASE_URL}/rules.txt"
NOTES_URL = f"{BASE_URL}/notes.txt"
PINS_URL  = f"{BASE_URL}/pins.json"
SEED_URL  = f"{BASE_URL}/seed_events.json"


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
- Pinned Events (avoid duplicates): {json.dumps(pins_json)}
- Seed Events: {json.dumps(seeds_json)}

TASK:
Merge seed events + inferred upcoming events + rule logic.

REQUIREMENTS:
1. ALL generated events must be *future dated* after today.
2. MUST include large event venues such as ExCeL, Olympia, NEC, Ally Pally, Kent Showground, Bluewater, etc.
3. Include markets, craft fairs, food festivals, expos, county shows.
4. Infer believable dates if needed.
5. Return ONLY a JSON array.
6. Each event object must be:

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

    # Parse output
    try:
        events = json.loads(response.output_text)
    except:
        return seeds_json  # safe fallback

    return filter_future_events(events)


# ----------------------------------------------------
# Filter out past-dated events
# ----------------------------------------------------
def filter_future_events(events):
    today = datetime.date.today()
    valid = []

    for ev in events:
        try:
            raw = ev.get("date", "")
            date_str = raw.split(" ")[0]  # handle ranges
            date = datetime.date.fromisoformat(date_str)
            if date >= today:
                valid.append(ev)
        except:
            continue

    return valid
