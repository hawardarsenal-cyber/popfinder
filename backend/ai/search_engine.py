import json
import requests
import datetime
from openai import OpenAI

client = OpenAI()

BASE_URL = "https://pos.kartingcentral.co.uk/home/download/pos2/pos2/popfinder/backend/data"

RULES_URL = f"{BASE_URL}/rules.txt"         # NOW treated as event list
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

    # THE BIG CHANGE:
    # rules.txt now contains the EVENT LIST provided by GPT.
    rules_text = load_remote(RULES_URL)

    notes_text = load_remote(NOTES_URL)
    pins_json  = load_json_remote(PINS_URL)
    seeds_json = load_json_remote(SEED_URL)

    today = datetime.date.today().isoformat()

    prompt = f"""
You are PopFinder, the UK’s event intelligence engine.

IMPORTANT:
- The content below (rules.txt) IS THE EVENT LIST.
- Do NOT create new events.
- Do NOT invent URLs.
- Do NOT guess anything.
- ONLY use events found inside rules.txt, seed events, or pinned events.
- You may filter, rank, reformat, and extract, but never fabricate.

-------------------------
EVENT DATA (rules.txt):
-------------------------
{rules_text}

-------------------------
USER CONTEXT
-------------------------
Region: {region}
Keywords: {keywords}
Today: {today}

-------------------------
ADDITIONAL NOTES
-------------------------
{notes_text}

-------------------------
PINNED EVENTS (extra priority)
-------------------------
{json.dumps(pins_json)}

-------------------------
SEED EVENTS (verified baseline)
-------------------------
{json.dumps(seeds_json)}

-------------------------
YOUR TASK
-------------------------
1. Merge events from rules.txt + pins + seed events.
2. Filter events to match region + keyword where meaningful.
3. Remove irrelevant, outdated, or suspicious events.
4. Keep future dates only.
5. Remove duplicates.
6. ALWAYS prefer pinned events first, then seed events, then rules.txt entries.
7. Output 12–24 events maximum.

FORMAT:
Return ONLY a JSON array of:
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

DO NOT output anything except JSON.
"""

    # GPT CALL
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=3500
    )

    # Parse output
    try:
        raw = json.loads(response.output_text)
    except Exception:
        # fallback
        return filter_future_and_valid(seeds_json)

    # Clean
    cleaned = filter_future_and_valid(raw)
    future_seeds = filter_future_and_valid(seeds_json)

    return future_seeds + cleaned
