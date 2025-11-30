import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import json
import os

client = OpenAI()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RULES_FILE = os.path.join(DATA_DIR, "rules.txt")
NOTES_FILE = os.path.join(DATA_DIR, "notes.txt")
PINS_FILE = os.path.join(DATA_DIR, "pins.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def load_context():
    with open(RULES_FILE, "r") as f:
        rules = f.read()

    with open(NOTES_FILE, "r") as f:
        notes = f.read()

    try:
        with open(PINS_FILE, "r") as f:
            pins = json.load(f)
    except:
        pins = []

    return rules, notes, pins


def smart_event_search(query, region):
    rules, notes, pins = load_context()

    effective_query = query if query.strip() else "default"

system_prompt = f"""
You are PopFinder AI.
Use the following permanent business rules, operator notes, and pinned events
to guide your event/opportunity search.

### RULES
{rules}

### NOTES
{notes}

### PINS
{json.dumps(pins, indent=2)}

Your task:
- Search for ANY relevant pop-up opportunities, events, markets, fairs, festivals,
  footfall hotspots, brand activation locations, councils, landlords, retail spaces, etc.
- Focus the search on **{region}** unless the query asks otherwise.
- Use the search query: "{effective_query}"
If query is 'default', generate a full search based entirely on the rules + notes + pins.
- Return JSON list of objects with:
  title, date, location, description, url (optional), score
"""

    response = client.responses.create(
        model="gpt-4.1",
        input=system_prompt,
        max_output_tokens=4000
    )

    raw = response.output_text
    try:
        return json.loads(raw)
    except:
        return [{"title": "Parsing error", "raw": raw}]
