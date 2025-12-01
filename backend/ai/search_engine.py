import json
import requests
import datetime
from openai import OpenAI

client = OpenAI()

BASE_URL = "https://pos.kartingcentral.co.uk/home/download/pos2/pos2/popfinder/backend/data"

RULES_URL = f"{BASE_URL}/rules.txt"
NOTES_URL = f"{BASE_URL}/notes.txt"
PINS_URL  = f"{BASE_URL}/pins.json"
SEED_URL  = f"{BASE_URL}/seed_events.json"

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

def smart_event_search(region: str, keywords: str):

    rules_text = load_remote(RULES_URL)
    notes_text = load_remote(NOTES_URL)
    pins_json  = load_json_remote(PINS_URL)
    seeds_json = load_json_remote(SEED_URL)

    today = datetime.date.today().isoformat()

    prompt = f"""
You are PopFinder, an event-intelligence engine for UK vendor opportunities.

USER QUERY:
Region: {region}
Keywords: {keywords}
Today: {today}

CONTEXT:
Rules: {rules_text}
Notes: {notes_text}
Pinned Events: {json.dumps(pins_json)}
Seed Events: {json.dumps(seeds_json)}

TASK:
Generate **realistic upcoming events** based on the homepage sources listed in the rules.
If scraper data is missing (currently not implemented), infer events that are consistent
with venue type and seasonal timing.

Strict Requirements:
1. Events must be future-dated only.
2. Prefer real events tied to venue homepages.
3. If uncertain, infer believable events based on common venue usage.
4. Do NOT fabricate URLs. Use homepage + "/events" or homepage root if unknown.
5. Return ONLY JSON array.

Each event must include:
{
  "title": "",
  "date": "",
  "location": "",
  "description": "",
  "url": ""
}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=2500
    )

    try:
        events = json.loads(response.output_text)
    except:
        return seeds_json

    return filter_future(events)

def filter_future(events):
    today = datetime.date.today()
    valid = []
    for ev in events:
        try:
            raw = ev.get("date", "")
            iso = raw.split(" ")[0]
            dt = datetime.date.fromisoformat(iso)
            if dt >= today:
                valid.append(ev)
        except:
            continue
    return valid

