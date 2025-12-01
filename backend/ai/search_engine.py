import json, datetime, re

def extract_events_from_rules(path):
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()

    # Extract JSON after [data]
    match = re.search(r"\[data\](.*)", txt, re.S)
    if not match:
        return []

    raw = match.group(1).strip()

    try:
        events = json.loads(raw)
        return events
    except:
        return []

def search_events(events, region, keywords):
    today = datetime.date.today()

    def future(e):
        try:
            d = e["date"].split(" ")[0]
            return datetime.date.fromisoformat(d) >= today
        except:
            return False

    def match_region(e):
        return region.lower() in e["location"].lower() or region.lower() == "uk"

    def match_keywords(e):
        if not keywords:
            return True
        return any(k.lower() in json.dumps(e).lower() for k in keywords.split())

    filtered = [e for e in events if future(e) and match_region(e) and match_keywords(e)]
    return filtered
