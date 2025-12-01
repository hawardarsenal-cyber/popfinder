import json
import requests
import datetime
from openai import OpenAI

client = OpenAI()

# ===============================================================
#  CONFIG — Remote data directories
# ===============================================================

BASE_URL = "https://pos.kartingcentral.co.uk/home/download/pos2/pos2/popfinder/backend/data"

RULES_URL = f"{BASE_URL}/rules.txt"        # NOW: contains the event list
NOTES_URL = f"{BASE_URL}/notes.txt"
PINS_URL  = f"{BASE_URL}/pins.json"
SEED_URL  = f"{BASE_URL}/seed_events.json"


# ===============================================================
#  HELPERS
# ===============================================================

def load_remote(url: str) -> str:
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.text
    except Exception:
        return ""


def load_json_remote(url: str):
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


def url_seems_real(url: str) -> bool:
    """
    A VERY strict URL checker to prevent hallucinations.
    """
    if not isinstance(url, str) or len(url) < 10:
        return False

    trusted = [
        "excel.london", "olympia.london", "thenec.co.uk", "necgroup.co.uk",
        "eventbrite", "ticketmaster", "see.tickets",
        "kew.org", "goodwood.com",
        "bluewater.co.uk", "dreamland.co.uk",
        "alexandrapalace.com",
        "visitlondon.com",
        "hydeparkwinterwonderland.com",
        "winterlandbluewater.com",
        "lovefairs.com",
        "kenteventcentre.co.uk",
        "harrogateconventioncentre",
        "brighton", "harrogate"
    ]

    low = url.lower()
    return any(t in low for t in trusted)


def filter_future_and_valid(events):
    """
    Final pass filtering for:
    - future dates
    - valid URLs (or titles indicating known market/fair types)
    - banned hallucination patterns
    """
    today = datetime.date.today()
    out = []

    for ev in events:
        try:
            raw = ev.get("date", "")
            first = raw.split(" ")[0]
            date = datetime.date.fromisoformat(first)

            # Only future events
            if date < today:
                continue

            title = (ev.get("title", "")).lower()

            banned = [
                "gaming expo", "tech & gaming", "retro gaming",
                "winter tech expo", "london comics expo"
            ]

            if any(b in title for b in banned):
                continue

            url = ev.get("url", "")

            if not url_seems_real(url):
                # allow fairs/markets even if URL is not strong
                recur = ["festival", "market", "fair", "christmas", "county show"]
                if not any(r in title for r in recur):
                    continue

            out.append(ev)

        except Exception:
            continue

    return out


# ===============================================================
#  MAIN SEARCH ENGINE
# ===============================================================

def smart_event_search(region: str, keywords: str):
    """
    Main PopFinder engine:
    - rules.txt = the definitive list of event data (user-provided / GPT-generated)
    - pinned + seed events also included
    - NEVER hallucinate
    """

    # Load all distributed data sources
    rules_text = load_remote(RULES_URL)        # now used as the event catalogue
    notes_text = load_remote(NOTES_URL)
    pins_json  = load_json_remote(PINS_URL)
    seeds_json = load_json_remote(SEED_URL)

    today = datetime.date.today().isoformat()

    # ===========================================================
    # GPT Prompt — DO NOT change unless updating system behaviour
    # ===========================================================
    prompt = f"""
You are PopFinder, the UK’s vendor event extraction AI.

CRITICAL RULE:
The file rules.txt below contains the REAL event data. 
You must ONLY extract events that appear inside rules.txt, OR are listed in pinned events OR seed events.
You MUST NOT create or invent any new events.
You MUST NOT guess URLs.
You MUST NOT hallucinate.

Your job:
1. Read rules.txt event data.
2. Extract ALL real events with:
   - real title
   - real date or date range
   - real venue/location
   - real URL from the text
3. Combine these with pinned events and seed events.
4. Filter by region + keyword if relevant.
5. Future dates only.
6. Remove any duplicates.
7. Output ONLY 12–24 events MAX, sorted by relevance.

---------------------------
RULES.TXT CONTENT (EVENT LIST)
---------------------------
{rules_text}

---------------------------
NOTES.TXT (optional hints)
---------------------------
{notes_text}

---------------------------
PINNED EVENTS (always keep)
---------------------------
{json.dumps(pins_json)}

---------------------------
SEED EVENTS (verified)
---------------------------
{json.dumps(seeds_json)}

---------------------------
USER QUERY
---------------------------
Region: {region}
Keywords: {keywords}
Today: {today}

---------------------------
OUTPUT FORMAT RULES
---------------------------
Return ONLY a JSON array:
[
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
]

NO commentary.
NO markdown.
NO text outside JSON.
"""

    # ===========================================================
    # Run GPT
    # ===========================================================
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=3500
    )

    # ===========================================================
    # Parse JSON
    # ===========================================================
    try:
        events = json.loads(response.output_text)
        if not isinstance(events, list):
            raise ValueError("GPT returned non-list JSON")
    except Exception:
        return filter_future_and_valid(seeds_json)

    # ===========================================================
    # Final cleaning and dedupe
    # ===========================================================
    cleaned = filter_future_and_valid(events)
    future_seeds = filter_future_and_valid(seeds_json)

    merged = cleaned + future_seeds

    # dedupe
    final = []
    seen = set()

    for ev in merged:
        key = (
            (ev.get("title") or "").lower().strip(),
            (ev.get("date") or "").lower().strip(),
            (ev.get("location") or "").lower().strip(),
        )

        if key in seen:
            continue

        seen.add(key)
        final.append(ev)

    return final
