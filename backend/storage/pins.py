import os, json

PIN_PATH = "backend/data/pinned.json"

def load_pins():
    if not os.path.exists(PIN_PATH):
        return []
    with open(PIN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_pin(event):
    pins = load_pins()
    pins.append(event)
    with open(PIN_PATH, "w", encoding="utf-8") as f:
        json.dump(pins, f, indent=2)

def delete_pin(event):
    pins = load_pins()
    pins = [p for p in pins if p != event]
    with open(PIN_PATH, "w", encoding="utf-8") as f:
        json.dump(pins, f, indent=2)
