import json
import requests
import datetime
from openai import OpenAI

client = OpenAI()

# ------------------------------------------------------------------
# Remote data locations (same as before)
# ------------------------------------------------------------------
BASE_URL = "https://pos.kartingcentral.co.uk/home/download/pos2/pos2/popfinder/backend/data"

RULES_URL = f"{BASE_URL}/rules.txt"
NOTES_URL = f"{BASE_URL}/notes.txt"
PINS_URL  = f"{BASE_URL}/pins.json"
SEED_URL  = f"{BASE_URL}/seed_events.json"


# ------------------------------------------------------------------
# Helpers to read remote files
# ------------------------------------------------------------------
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


# ------------------------------------------------------------------
# Safety filters for dates / URLs
# ------------------------------------------------------------------
def url_seems_real(url: str) -> bool:
    """
    Very conservative URL sanity check.
    """
    if not isinstance(url, str) or len(url) < 10:
        return False

    trusted = [
        # big venues & organisers
        "excel.london",
        "olympia.london",
        "thenec.co.uk",
        "necgroup.co.uk",
        "eventbrite",
        "ticketmaster",
        "see.tickets",
        "kew.org",
        "goodwood.com",
        "bluewater.co.uk",
        "dreamland.co.uk",
        "alexandrapalace.com",
        "visitlondon.com",
        "hydeparkwinterwonderland.com",
        "winterlandbluewater.com",
        "lovefairs.com",
        "kenteventcentre.co.uk",
        "harrogateconventioncentre.co.uk",
        "brighton",
        "harrogate",
    ]
    u = url.lower()
    return any(t in u for t in trusted)


def filter_future_and_valid(events):
    """
    Keep only future-dated, plausible events.
    """
    today = datetime.date.today()
    out = []

    for ev in events or []:
        try:
            raw_date = ev.get("date", "") or ""
            first = raw_date.split(" ")[0]
            event_date = datetime.date.fromisoformat(first)

            # ignore past events
            if event_date < today:
                continue

            # very rough anti-hallucination guard:
            title = (ev.get("title") or "").lower()

            banned_titles = [
                "gaming expo",
                "tech & gaming",
                "winter tech expo",
                "london comics expo",
                "retro gaming expo",
            ]
            if any(b in title for b in banned_titles):
                continue

            url = ev.get("url", "") or ""

            # If URL looks bad and the title doesn't clearly mention
            # real-world style events, drop it.
            if url and not url_seems_real(url):
                recur = ["festival", "market", "fair", "christmas", "county show"]
                if not any(r in title for r in recur):
                    continue

            out.append(ev)
        except Exception:
            # any parsing failure → drop the event
            continue

    return out


# ------------------------------------------------------------------
# Main search entry point used by the FastAPI backend
# ------------------------------------------------------------------
def smart_event_search(region: str, keywords: str):
    """
    Core search function called by the FastAPI API.

    NEW BEHAVIOUR:
    - Treats rules.txt as a curated text catalogue of REAL events.
    - GPT is explicitly forbidden from inventing any events.
    - Only events that appear in rules.txt (Event Data section),
      pins.json or seed_events.json may be returned.
    """

    # Load remote configuration / data
    full_rules = load_remote(RULES_URL)
event_data = extract_event_data(full_rules)
   # contains SYSTEM RULES + EVENT DATA
    notes_text = load_remote(NOTES_URL)   # still available if you want to use it later
    pins_json  = load_json_remote(PINS_URL)
    seeds_json = load_json_remote(SEED_URL)

    today = datetime.date.today().isoformat()

    # ------------------------------------------------------------------
    # Prompt: tell GPT that rules.txt is the ground-truth event list
    # ------------------------------------------------------------------
    prompt = f"""
You are PopFinder, the UK's vendor opportunity engine.

You are given two data sources:
1. rules.txt — containing:
   • SYSTEM RULES (instructions)
   • EVENT DATA (a raw text dump that *contains the real events*)
2. PINNED_EVENTS_JSON — already-validated events

Your job:

============================================================
CRITICAL: EVENT EXTRACTION RULE
============================================================

The EVENT DATA section of rules.txt *IS* the authoritative list of
REAL events. The formatting may be:
- Bullet lists
- Markdown-style lists
- Sections like "FinTech Connect – 2–3 Dec 2025"
- Paragraphs describing events
- Mixed prose containing event names, dates, venues, and URLs

You MUST parse **every event explicitly mentioned** in the EVENT DATA
section. An event is valid if:
- It has a real title (clearly mentioned in the text)
- It has a date or date range (e.g. “2–3 Dec 2025”, “18–22 Dec 2025”)
- It has a location OR a venue section (e.g. “ExCeL London”, “Olympia”)
- A URL is present anywhere in the section (or within the block of
  that venue); you MUST attach the correct URL from the text.

If the text presents multiple events under a venue (e.g. ExCeL London),
you MUST treat each bullet line as a separate event.

Patterns to extract:
- “TITLE – DATE”
- “• TITLE — DATE”
- “* TITLE — DATE”
- “TITLE (DATE)”
- Section headers followed by lists
- Dates written as ranges (e.g. “11–14 Jan 2026”)
- Bullet lists with descriptions

Region and keywords only FILTER extracted events.

============================================================
ABSOLUTE RESTRICTIONS
============================================================
You MUST NOT invent any event that is not present in EVENT DATA.
If EVENT DATA contains 9 real events and the others are noise,
you must output exactly those 9.

Pinned events must also be included.

============================================================
OUTPUT FORMAT
============================================================

OUTPUT ONLY a JSON array:
[
  {
    "title": "",
    "date": "",
    "location": "",
    "description": "",
    "url": "",
    "category": "",
    "footfall_score": 0,
    "vendor_fit_score": 0
  }
]
No markdown. No commentary. JSON only.

============================================================
DATA YOU MUST READ
============================================================

rules.txt (SYSTEM RULES + EVENT DATA):
<<<RULES_TXT_START
{event_data}
RULES_TXT_END>>>

Pinned Events (JSON):
{json.dumps(pins_json, ensure_ascii=False)}

============================================================
USER QUERY
============================================================
Region: {region}
Keywords: {keywords}
Today: {today}
"""


    # ------------------------------------------------------------------
    # Call OpenAI
    # ------------------------------------------------------------------
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=3000,
    )

    # ------------------------------------------------------------------
    # Parse JSON; on failure, fall back to seeds only
    # ------------------------------------------------------------------
    try:
        llm_events = json.loads(response.output_text)
        if not isinstance(llm_events, list):
            raise ValueError("LLM output was not a JSON array")
    except Exception:
        # If GPT output isn't valid JSON, just fall back to curated seeds
        return filter_future_and_valid(seeds_json)

    # ------------------------------------------------------------------
    # Clean & merge with seeds (as extra, low-priority events)
    # ------------------------------------------------------------------
    cleaned_llm   = filter_future_and_valid(llm_events)
    future_seeds  = filter_future_and_valid(seeds_json)

    # Order of priority:
    #   1) Events parsed from rules.txt (cleaned_llm)
    #   2) Seed events (future_seeds) as backup / extras
    merged = cleaned_llm + future_seeds

    # De-duplicate by (title, date, location)
    unique = []
    seen = set()

    for ev in merged:
        title = (ev.get("title") or "").strip().lower()
        date  = (ev.get("date") or "").strip().lower()
        loc   = (ev.get("location") or "").strip().lower()
        key = (title, date, loc)

        if not title:
            # discard totally empty shells
            continue

        if key in seen:
            continue

        seen.add(key)
        unique.append(ev)

    return unique


