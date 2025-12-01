# backend/ai/search_engine.py

import json
import requests
import datetime
import re
from typing import List, Dict, Any, Optional

# ----------------------------------------------------
# REMOTE FILE LOCATIONS (PUBLIC FTP URLs)
# ----------------------------------------------------
BASE_URL = "https://pos.kartingcentral.co.uk/home/download/pos2/pos2/popfinder/backend/data"

RULES_URL = f"{BASE_URL}/rules.txt"
NOTES_URL = f"{BASE_URL}/notes.txt"
PINS_URL  = f"{BASE_URL}/pins.json"
SEED_URL  = f"{BASE_URL}/seed_events.json"


# ----------------------------------------------------
# Helpers to load the remote files
# ----------------------------------------------------
def load_remote(url: str) -> str:
    """Fetch a remote text file, returning '' on error."""
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.text
    except Exception:
        return ""


def load_json_remote(url: str) -> Any:
    """Fetch a remote JSON file, returning [] on error."""
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


def _normalise(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()


def _tokenise(text: str) -> List[str]:
    return [t for t in _normalise(text).split() if t]


def _parse_date(raw: str) -> Optional[datetime.date]:
    """
    Take a date or date-range string like '2025-06-11 to 2025-06-15'
    and return the start date as a date object.
    """
    if not raw:
        return None
    m = re.search(r"\d{4}-\d{2}-\d{2}", raw)
    if not m:
        return None
    try:
        return datetime.date.fromisoformat(m.group(0))
    except ValueError:
        return None


# ----------------------------------------------------
# Region scoring
# ----------------------------------------------------
REGION_SYNONYMS = {
    "london": [
        "london", "excel", "olympia", "ally pally", "alexandra palace",
        "hyde park", "greenwich", "kensington", "islington",
        "truman brewery", "regent", "kew", "spitalfields", "westfield"
    ],
    "kent": [
        "kent", "canterbury", "faversham", "detling", "bluewater",
        "margate", "rochester", "folkestone", "medway", "tunbridge wells"
    ],
    "uk": [],  # match everything
}


def _region_score(location: str, region: str) -> float:
    """Score how well an event location matches the requested region."""
    loc = _normalise(location)
    reg = (region or "").lower()

    # UK / empty -> everything is allowed, mild boost
    if reg in ("uk", "all", ""):
        return 1.0

    synonyms = REGION_SYNONYMS.get(reg, [reg])
    for word in synonyms:
        if word and word in loc:
            return 2.0

    # weak match: still allow, but lower score
    return 0.5


# ----------------------------------------------------
# Keyword / notes / pins influence
# ----------------------------------------------------
VENDOR_KEYWORDS = [
    "market", "fair", "festival", "show", "expo", "comic", "convention",
    "craft", "artisan", "food", "drink", "street food", "gift",
    "trade", "wedding", "home", "design",
]

BIG_VENUE_KEYWORDS = [
    "excel", "olympia", "nec", "alexandra palace", "ally pally",
    "showground", "arena", "centre", "stadium", "hyde park"
]


def _keyword_score(ev: Dict[str, Any], keywords: str) -> float:
    """0–1 score based on overlap between user keywords and event text."""
    if not keywords:
        return 0.0
    kw_tokens = set(_tokenise(keywords))
    text = " ".join(str(ev.get(k, "")) for k in ("title", "description", "location"))
    text_tokens = set(_tokenise(text))
    if not text_tokens:
        return 0.0
    overlap = kw_tokens & text_tokens
    return float(len(overlap)) / max(len(kw_tokens), 1)


def _notes_boost(ev: Dict[str, Any], notes_text: str) -> float:
    """
    Light-touch boost if words from your notes appear in the event.
    Notes are *hints*, not hard filters.
    """
    if not notes_text:
        return 0.0
    text = " ".join(str(ev.get(k, "")) for k in ("title", "description", "location"))
    ev_tokens = set(_tokenise(text))
    notes_tokens = set(_tokenise(notes_text))
    overlap = ev_tokens & notes_tokens
    # very soft influence
    return min(len(overlap) * 0.1, 1.0)


def _pins_boost(ev: Dict[str, Any], pins: List[Dict[str, Any]]) -> float:
    """
    Boost events similar to things you've pinned before.
    """
    if not pins:
        return 0.0
    title = _normalise(str(ev.get("title", "")))
    loc = _normalise(str(ev.get("location", "")))
    for p in pins:
        pt = _normalise(str(p.get("title", "")))
        pl = _normalise(str(p.get("location", "")))
        if pt and pt in title:
            return 1.0
        if pl and pl in loc:
            return 0.8
    return 0.0


# ----------------------------------------------------
# Footfall & vendor-fit heuristics
# ----------------------------------------------------
def _footfall_score(ev: Dict[str, Any]) -> int:
    """
    1–10 guess at how big / busy the event is.
    Purely heuristic based on venue + keywords.
    """
    text = _normalise(ev.get("title", "") + " " + ev.get("location", ""))
    score = 4
    for kw in BIG_VENUE_KEYWORDS:
        if kw in text:
            score += 3
    for kw in ("festival", "comic con", "pride", "wonderland", "county show", "fair"):
        if kw.replace(" ", "") in text.replace(" ", ""):
            score += 2
    return max(1, min(score, 10))


def _vendor_fit_score(ev: Dict[str, Any]) -> int:
    """
    1–10 guess at how suitable the event is for traders / vendors.
    """
    text = _normalise(ev.get("title", "") + " " + ev.get("description", ""))
    score = 3
    for kw in VENDOR_KEYWORDS:
        if kw in text:
            score += 1
    return max(1, min(score, 10))


# ----------------------------------------------------
# Filter out past events
# ----------------------------------------------------
def filter_future_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    today = datetime.date.today()
    out: List[Dict[str, Any]] = []
    for ev in events:
        d = _parse_date(str(ev.get("date", "")))
        if d is None:
            continue
        if d >= today:
            out.append(ev)
    return out


# ----------------------------------------------------
# MAIN ENTRYPOINT
# ----------------------------------------------------
def smart_event_search(region: str, keywords: str) -> List[Dict[str, Any]]:
    """
    Deterministic, non-hallucinating search.

    - Uses ONLY the vetted seed_events.json file as ground truth.
    - Notes & pins influence ranking but never create new events.
    """
    # notes + pins: influence scoring only
    notes_text = load_remote(NOTES_URL)
    pins_json = load_json_remote(PINS_URL)
    if not isinstance(pins_json, list):
        pins_json = []

    # seed events: canonical list of real shows
    seeds_json = load_json_remote(SEED_URL)
    if not isinstance(seeds_json, list):
        seeds_json = []

    # only look at future-dated events
    candidates = filter_future_events(seeds_json)

    region = region or "UK"
    scored: List[Dict[str, Any]] = []

    for ev in candidates:
        base = 1.0
        rs = _region_score(ev.get("location", ""), region)
        ks = _keyword_score(ev, keywords)
        nb = _notes_boost(ev, notes_text)
        pb = _pins_boost(ev, pins_json)
        ff = _footfall_score(ev)
        vf = _vendor_fit_score(ev)

        total_score = base + rs * 1.5 + ks * 3.0 + nb + pb + ff * 0.3 + vf * 0.2

        ev_copy = dict(ev)  # don’t mutate original JSON
        ev_copy["footfall_score"] = ff
        ev_copy["vendor_fit_score"] = vf
        ev_copy["score"] = round(total_score, 2)
        scored.append(ev_copy)

    # Sort: best score first, then soonest date
    scored.sort(
        key=lambda e: (
            -e.get("score", 0),
            _parse_date(str(e.get("date", ""))) or datetime.date.max,
        )
    )

    # limit for UI – tweak if you want more / fewer
    return scored[:40]
