
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


def url_seems_real(url: str) -> bool:
    if not isinstance(url, str) or len(url) < 10:
        return False

    trusted = [
        "excel.london", "olympia.london", "thenec.co.uk", "necgroup.co.uk",
        "eventbrite", "kew.org", "bluewater.co.uk", "dreamland.co.uk",
        "goodwood.com", "visitlondon.com", "mcmcomiccon.com", "ticketmaster",
        "brighton", "harrogate"
    ]
    return any(t in url.lower() for t in trusted)


def filter_future_and_valid(events):
    today = datetime.date.today()
    out = []

    for ev in events:
        try:
            raw = ev.get("date", "")
            first = raw.split(" ")[0]
            date = datetime.date.fromisoformat(first)

            if date < today:
                continue

            title = ev.get("title", "").lower()

            banned = [
                "gaming expo", "tech & gaming", "winter tech expo",
                "london comics expo", "retro gaming expo"
            ]
            if any(b in title for b in banned):
                continue

            url = ev.get("url", "")
            if not url_seems_real(url):
                recur = ["festival", "market", "fair", "christmas", "county show"]
                if not any(r in title for r in recur):
                    continue

            out.append(ev)
        except:
            continue

    return out


def smart_event_search(region: str, keywords: str):

    rules_text = load_remote(RULES_URL)
    notes_text = load_remote(NOTES_URL)
    pins_json  = load_json_remote(PINS_URL)
    seeds_json = load_json_remote(SEED_URL)

    today = datetime.date.today().isoformat()

    prompt = f"""
You are PopFinder, the UK's vendor opportunity engine.
Return ONLY legitimate, upcoming, recurring events.

USER QUERY:
Region: {region}
Keywords: {keywords}
Today: {today}

Rules:
{rules_text}

Notes:
{notes_text}

Pinned Events:
{json.dumps(pins_json)}

Seed Events (verified):
{json.dumps(seeds_json)}

RULES:
1. DO NOT invent events.
2. Dates must be future.
3. Use seed events as reliable ground truth.
4. Give 12–24 events.
5. Only use realistic URLs.
6. ELIMINATE events if unsure of legitimacy.

Output ONLY JSON array of:
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
        max_output_tokens=3000
    )

    try:
        raw = json.loads(response.output_text)
    except:
        return seeds_json

    cleaned = filter_future_and_valid(raw)
    future_seeds = filter_future_and_valid(seeds_json)

    return future_seeds + cleaned
