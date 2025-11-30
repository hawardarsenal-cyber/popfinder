import hashlib

def score_event(event):
    """
    Simple ranking heuristic.
    Event must be a dict.
    """

    raw = event.get("raw", "") or ""
    title = event.get("title", "") or ""

    # crude scoring
    score = len(title) + len(raw)

    # fallback consistent hash if empty
    if score == 0:
        score = int(hashlib.md5(raw.encode()).hexdigest(), 16) % 100

    event["score"] = score
    return event
