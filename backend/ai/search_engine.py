import datetime
import json
import requests
from openai import OpenAI

client = OpenAI()

RULES_URL = "https://pos.kartingcentral.co.uk/popfinder/rules.txt"
NOTES_URL = "https://pos.kartingcentral.co.uk/popfinder/notes.txt"
PINS_URL = "https://pos.kartingcentral.co.uk/popfinder/pins.json"

def fetch_remote(url):
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.text
    except:
        return ""

def smart_event_search(region, keywords):

    rules = fetch_remote(RULES_URL)
    notes = fetch_remote(NOTES_URL)
    pins = fetch_remote(PINS_URL)

    today = datetime.date.today()
    limit = today + datetime.timedelta(days=90)

    prompt = f"""
You are PopFinder, a UK event intelligence engine.

### RULESET ###
{rules}

### USER NOTES ###
{notes}

### PINNED EVENTS ###
{pins}

Find upcoming events within the next 0–90 days.
Region: {region}
User Keywords: "{keywords}"

Prioritise:
- ExCeL London events
- Olympia London events
- NEC Birmingham events
- County shows (Kent, Sussex, Surrey, Essex)
- Seasonal festivals
- Food festivals, fairs, craft markets
- High-footfall pop-up opportunities
- Consumer shows (Ideal Home Show, Baby Show, Comic Con, etc.)

Return ONLY JSON in this format:
{
  "events": [
      {{"title": "...", "date": "YYYY-MM-DD", "location": "...", "description": "...", "url": "https://"}}
  ]
}
"""

    response = client.responses.create(
        model="gpt-4.1",
        input=prompt,
        response_format={"type": "json_object"}
    )

    try:
        data = response.output[0].content[0].text
        obj = eval(data)
        events = obj.get("events", [])
    except:
        return []

    return filter_future(events)

def filter_future(events):
    today = datetime.date.today()
    limit = today + datetime.timedelta(days=90)
    valid = []

    for ev in events:
        d = ev.get("date", "").strip()
        try:
            parsed = datetime.date.fromisoformat(d)
            if today <= parsed <= limit:
                valid.append(ev)
        except:
            continue

    return valid
