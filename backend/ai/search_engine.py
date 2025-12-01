import json
import requests
import datetime
from openai import OpenAI

client = OpenAI()

# ----------------------------------------------------
# REMOTE FILE LOCATIONS (PUBLICLY ACCESSIBLE FTP URLS)
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
# BASIC URL SANITY CHECK (Soft verification)
# ----------------------------------------------------
def url_seems_real(url: str) -> bool:
    if not isinstance(url, str) or len(url) < 10:
        return False

    trusted_domains = [
        "excel.london",
        "olympia.london",
        "thenec.co.uk",
        "necgroup.co.uk",
        "eventbrite",
        "kew.org",
        "bluewater.co.uk",
        "dreamland.co.uk",
        "goodwood.com",
        "visitlondon.com",
        "mcmcomiccon.com",
        "festivals",
        "gov.uk",
        "brighton",
        "harrogate",
        "ticketmaster",
    ]

    return any(domain in url.lower() for domain in trusted_domains)


# ----------------------------------------------------
# FILTERING: KEEP ONLY FUTURE EVENTS + VALIDATE LOGIC
# ----------------------------------------------------
def filter_future_and_valid(events):
    today = datetime.date.today()
    out = []

    for ev in events:
        try:
            raw_date = ev.get("date", "")
            first_day = raw_date.split(" ")[0]  # handle ranges
            parsed = datetime.date.fromisoformat(first_day)

            if parsed < today:
                continue

            # Soft verification:
            # allow:
            #  - events from seed list
            #  - recurring events
            #  - events with trusted URLs
            # reject:
            #  - expos at Olympia/Excel that don't actually exist
            title = ev.get("title", "").lower()

            # Hard block patterns known to be hallucinated
            banned_patterns = [
                "gaming expo",          # usually fake unless MCM includes it
                "tech & gaming",        # fake common hallucination
                "winter tech expo",
                "london comics expo",   # not real (only MCM or LFCC)
                "retro gaming expo"     # usually hallucinated
            ]

            if any(bp in title for bp in banned_patterns):
                continue

            # Trusted if URL looks legitimate
            url = ev.get("url", "")

            if not url_seems_real(url):
                # If it looks like a recurring event, allow:
                recurring_keywords = ["christmas", "festival", "market", "fair", "county show"]
                if not any(k in title for k in recurring_keywords):
                    continue

            out.append(ev)

        except:
            continue

    return out


# ----------------------------------------------------
# MAIN SEARCH ENGINE
# ----------------------------------------------------
def smart_event_search(region: str, keywords: str):

    rules_text = load_remote(RULES_URL)
    notes_text = load_remote(NOTES_URL)
    pins_json  = load_json_remote(PINS_URL)
    seeds_json = load_json_remote(SEED_URL)

    today = datetime.date.today().isoformat()

    prompt = f"""
You are PopFinder, the UK's vendor opportunity engine.
You must return ONLY verified, legitimate, upcoming or recurring events.

USER QUERY:
Region: {region}
Keywords: {keywords}
Today: {today}

CONTEXT FILES:
Rules: {rules_text}
Notes: {notes_text}
Pinned Events: {json.dumps(pins_json)}
Seed Events (verified): {json.dumps(seeds_json)}

CRITICAL RULES:
1. DO NOT invent expos or conventions that do not exist.
2. You MAY infer dates for recurring events (Christmas markets, seasonal fairs, county shows).
3. You MUST prioritise real venues (ExCeL, Olympia, NEC, Ally Pally, Kent Showground, Bluewater).
4. Only provide URLs that belong to real event websites.
5. If unsure about an event's legitimacy → DO NOT INCLUDE IT.
6. Use seed events as factual ground truth referencing patterns.
7. Provide 12–24 events total.
8. All dates must be future dates.

Event structure MUST be JSON only:
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
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=3000
    )

    try:
        raw = json.loads(response.output_text)
    except:
        return seeds_json  # fallback

    cleaned = filter_future_and_valid(raw)

    # Merge seed events (future only)
    future_seeds = filter_future_and_valid(seeds_json)

    return future_seeds + cleaned


