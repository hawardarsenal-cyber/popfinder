import os, json

NOTES_PATH = "backend/data/notes.json"

def load_notes():
    if not os.path.exists(NOTES_PATH):
        return {"notes": []}
    with open(NOTES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def add_note(text):
    data = load_notes()
    data["notes"].append(text)
    with open(NOTES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
