import json
import re
import requests
import datetime
from openai import OpenAI

client = OpenAI()

# ----------------------------------------------------
# REMOTE FILE LOCATIONS
# ----------------------------------------------------
BASE_URL = "https://pos.kartingcentral.co.uk/home/download/pos2/pos2/popfinder/backend/data"

RULES_URL = f"{BASE_URL}/rules.txt"
NOTES_URL = f"{BASE_URL}/notes.txt"
PINS_URL  = f"{BASE_URL}/pins.json"
SEED_URL  = f"{BASE_URL}/seed_events.json"


# ----------------------------------------------------
# HELPERS TO LOAD REMOTE FILES
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
# EXTRACT EVENT DATA SECTION FROM rules.txt
# ----------------------------------------------------
def extract_event_data_block(rules_text: str) -> str:
    """
    Extract the segment between:
    >>> BEGIN_EVENT_DATA
    >>> END_EVENT_DATA
    """

    match = re.search(
        r"BEGIN_EVENT_DATA(.*?)END_EVENT_DATA",
        rules_text,
        re.DOTALL | re.IGNORECASE
    )
    return match.group(1).strip() if match else ""


# ----------------------------------------------------
# PARSE RAW TEXT INTO EVENT OBJECTS
# ----------------------------------------------------
def parse_events_from_text(text: str) -> list:
    """
    Converts messy text into clean structured events.
    Uses pattern recognition, URL detection, date extraction.
    """

    if not text.strip():
        return []

    blocks = re.split(r"\n\s*\n", text.strip())  # separate by blank lines
    events = []

    for block in blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue

        title = lines[0]
        url = ""
        date = ""
        location = ""
        desc = ""

        # detect URL
        for l in lines:
            m = re.search(r"https?://[^\s]+", l)
            if m:
                url = m.group(0)
                break

        # detect date-like strings
        for l in lines:
            if re.search(r"\d{4}|\d{1,2}\s+\w+", l):
                date = l
                break

        # detect location-like lines
        for l in lines:
            if any(x in l.lower() for x in ["london", "kent", "birmingham", "manchester", "glasgow",
                                            "brighton", "showground", "park", "centre", "hall"]):
                location = l
                break

        # description = everything else
        desc = " ".join(lines[1:])

        # MUST have a title + something else
        if len(title) < 3:
            continue

        events.append({
            "title": title,
            "date": date or "",
            "location": location or "",
            "description": desc or "",
            "url": url or "",
            "category": "",
            "footfall_score": 0,
            "vendor_fit_score": 0
        })

    return events


# ----------------------------------------------------
# VALID URL CHECK
# ----------------------------------------------------
def url_seems_real(url: str) -> bool:
    if not isinstance(url, str) or len(url) < 12:
        return False

    trusted_domains = [
        "excel.london",
        "olympia.london",
        "necgroup",
        "thenec",
        "allypally",
        "eventbrite",
        "bluewater",
        "dreamland",
        "goodwood",
        "visitlondon",
        "ticketmaster",
        "brighton",
        "harrogate",
        "festival",
        "gov.uk"
    ]

    return any(domain in url.lower() for domain in trusted_domains)


# ----------------------------------------------------
# DATE NORMALISATION & FILTERING
# ----------------------------------------------------
def normalize_and_validate(ev):
    raw = ev.get("date", "").strip()
    if not raw:
        return None

    today = datetime.date.today()

    # Try ISO first
    try:
        iso = raw.split(" ")[0]
        date_obj = datetime.date.fromisoformat(iso)
        if date_obj < today:
            return None
        return ev
    except:
        pass

    # Try extracting any year-month-day in text
    m = re.search(r"(20\d{2})", raw)
    if not m:
        return None  # reject if no future year

    return ev  # Accept as recurring or fuzzy but future


# ----------------------------------------------------
# MAIN SEARCH ENGINE
# ----------------------------------------------------
def smart_event_search(region: str, keywords: str):

    # Load remote files
    rules_text = load_remote(RULES_URL)
    notes_text = load_remote(NOTES_URL)
    pins_json  = load_json_remote(PINS_URL)
    seeds_json = load_json_remote(SEED_URL)

    # Extract event block
    event_block = extract_event_data_block(rules_text)
    extracted_events = parse_events_from_text(event_block)

    # Normalise & filter event data
    cleaned = []
    for ev in extracted_events:
        valid = normalize_and_validate(ev)
        if not valid:
            continue

        # Reject hallucinated events
        if ev["url"] and not url_seems_real(ev["url"]):
            continue

        cleaned.append(ev)

    # Merge seed events
    merged = cleaned + seeds_json

    # Apply keyword boosting (soft boost only)
    if keywords.strip():
        kw = keywords.lower()

        boosted = [
            ev for ev in merged
            if kw in ev["title"].lower()
            or kw in ev["description"].lower()
        ]

        # ensure fallback if keyword too restrictive
        merged = boosted if boosted else merged

    return merged
