


import json
import requests
import datetime
from openai import OpenAI

client = OpenAI()

# ----------------------------------------------------
# REMOTE FILE LOCATIONS (LIVE FTP URLS)
# ----------------------------------------------------
BASE_URL = "https://pos.kartingcentral.co.uk/home/download/pos2/pos2/popfinder/backend/data"

RULES_URL = f"{BASE_URL}/rules.txt"
NOTES_URL = f"{BASE_URL}/notes.txt"
PINS_URL  = f"{BASE_URL}/pins.json"
SEED_URL  = f"{BASE_URL}/seed_events.json"


# ----------------------------------------------------
# SAFE REMOTE LOADERS
# ----------------------------------------------------
def load_remote(url: str) -> str:
    """Returns text from a remote file or empty string."""
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[PopFinder] Failed to load text from {url}: {e}")
        return ""


def load_json_remote(url: str):
    """Returns JSON array/object or empty list."""
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[PopFinder] Failed to load JSON from {url}: {e}")
        return []


# ----------------------------------------------------
# FILTER PAST EVENTS
# ----------------------------------------------------
def filter_future_events(events):
    today = datetime.date.today()
    valid = []

    for ev in events:
        raw_date = ev.get("date", "")
        if not raw_date:
            continue

        try:
            # Only check first segment if the date is a range.
            date_str = raw_date.split(" ")[0]
            date_obj = datetime.date.fromisoformat(date_str)
            if date_obj >= today:
                valid.append(ev)
        except:
            # Ignore invalid date formats silently
            continue

    return valid


# ----------------------------------------------------
# MAIN SEARCH ENGINE
# ----------------------------------------------------
def smart_event_search(region: str, keywords: str):

    # ------------ Load remote files ------------
    rules_text = load_remote(RULES_URL)
    notes_text = load_remote(NOTES_URL)
    pins_json  = load_json_remote(PINS_URL)
    seeds_json = load_json_remote(SEED_URL)

    today = datetime.date.today().isoformat()

    # ------------ Build GPT prompt ------------
    prompt = f"""
You are PopFinder, the UK's event & pop-up opportunity engine.

Your task: generate *realistic, upcoming* UK events, expos, markets,
festivals, fairs, and high-footfall vendor opportunities.

USER QUERY:
- Region: {region}
- Keywords: {keywords}
- Today’s Date: {today}

CONTEXT FROM SERVER:
--- Rules ---
{rules_text}

--- Notes ---
{notes_text}

--- Pinned Events ---
{json.dumps(pins_json)}

--- Seed Events (verified sources) ---
{json.dumps(seeds_json)}

REQUIREMENTS:
1. ALL events must have dates *after today*.
2. Include real venues such as ExCeL London, Olympia, NEC, Bluewater,
   Alexandra Palace, Southbank, Kent Showground, etc.
3. Use seed events to anchor realism — DO NOT contradict them.
4. You may infer dates only if needed, and must keep them plausible.
5. If keywords provided, boost but do not restrict.
6. Return **ONLY a JSON ARRAY** of objects in this exact structure:

[
  {{
    "title": "",
    "date": "",
    "location": "",
    "description": "",
    "url": ""
  }}
]
"""

    # ------------ GPT Call ------------
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=2500
    )

    # ------------ Parse JSON Output ------------
    try:
        result = json.loads(response.output_text)
    except Exception as e:
        print("[PopFinder] GPT output was not valid JSON:", e)
        return seeds_json  # fallback to seed events

    # ------------ Filter past events ------------
    return filter_future_events(result)
