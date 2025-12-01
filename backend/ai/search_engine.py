import re
import json
import datetime
import requests

BASE_URL = "https://pos.kartingcentral.co.uk/home/download/pos2/pos2/popfinder/backend/data"

RULES_URL = f"{BASE_URL}/rules.txt"
PINS_URL  = f"{BASE_URL}/pins.json"
SEED_URL  = f"{BASE_URL}/seed_events.json"

def load_remote(url):
    try:
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        return r.text
    except:
        return ""

def load_json(url):
    try:
        r = requests.get(url, timeout=6)
        r.raise_for_status()
        return r.json()
    except:
        return []

EVENT_PATTERN = re.compile(
    r"""
    (?P<title>.+?)\s+—\s+
    (?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2}(?:\s+to\s+[0-9]{4}-[0-9]{2}-[0-9]{2})?)\s*\n
    LOCATION:\s*(?P<location>.+?)\n
    DESCRIPTION:\s*(?P<description>.+?)\n
    CATEGORY:\s*(?P<category>.+?)\n
    FOOTFALL:\s*(?P<footfall>\d+)\n
    VENDOR_FIT:\s*(?P<vendor_fit>\d+)
    """,
    re.DOTALL | re.VERBOSE
)

def parse_events(rules_text):
    matches = EVENT_PATTERN.finditer(rules_text)
    events = []

    for m in matches:
        data = m.groupdict()

        # ensure clean formatting
        ev = {
            "title": data["title"].strip(),
            "date": data["date"].strip(),
            "location": data["location"].strip(),
            "description": data["description"].strip(),
            "category": data["category"].strip(),
            "footfall_score": int(data["footfall"]),
            "vendor_fit_score": int(data["vendor_fit"]),
            "url": extract_url(data["description"]),
        }
        events.append(ev)

    return events

def extract_url(desc):
    """Extract the FIRST https:// URL inside the DESCRIPTION line."""
    match = re.search(r"https:\/\/[^\s\)]+", desc)
    return match.group(0) if match else ""

def filter_future(events):
    out = []
    today = datetime.date.today()

    for ev in events:
        raw = ev["date"].split(" ")[0]
        try:
            d = datetime.date.fromisoformat(raw)
            if d >= today:
                out.append(ev)
        except:
            continue

    return out

def keyword_search(events, keywords):
    if not keywords:
        return events

    k = keywords.lower()

    return [
        ev for ev in events
        if k in ev["title"].lower()
        or k in ev["description"].lower()
        or k in ev["location"].lower()
        or k in ev["category"].lower()
    ]

def smart_event_search(region, keywords):
    """Deterministic, GPT-free event engine."""
    rules_text = load_remote(RULES_URL)
    pins = load_json(PINS_URL)
    seeds = load_json(SEED_URL)

    parsed = parse_events(rules_text)
    combined = parsed + pins + seeds

    combined = filter_future(combined)
    combined = keyword_search(combined, keywords)

    return combined[:50]  # Limit for UI performance
