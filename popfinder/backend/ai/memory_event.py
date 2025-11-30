import json
import os

def load_memory():
    pins_path = "../data/pins.json"
    notes_path = "../data/notes.json"
    memory = {"pins": [], "notes": []}

    if os.path.exists(pins_path):
        memory["pins"] = json.load(open(pins_path))

    if os.path.exists(notes_path):
        memory["notes"] = json.load(open(notes_path))

    return memory


def apply_memory_bias(event, memory):
    score = event["score"]

    # Boost based on pinned event patterns
    for pin in memory["pins"]:
        if pin["type"] == event.get("event_type"):
            score += 10

        if pin["region"] in event.get("location", ""):
            score += 10

    # Boost based on notes keywords
    for note in memory["notes"]:
        if note["text"].lower() in event.get("title", "").lower():
            score += 5
        if note["text"].lower() in event.get("reason", "").lower():
            score += 5

    event["score"] = min(score, 100)
    return event
