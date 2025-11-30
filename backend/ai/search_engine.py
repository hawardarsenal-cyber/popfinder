import json
import os
from openai import OpenAI

client = OpenAI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_FILE = os.path.join(BASE_DIR, "rules.txt")
PINS_FILE = os.path.join(BASE_DIR, "pinned.json")
NOTES_FILE = os.path.join(BASE_DIR, "notes.txt")
SEED_FILE = os.path.join(BASE_DIR, "seed_events.json")


def load_json(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def load_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def smart_event_search(region: str, keywords: str):
    # Load context files
    rules_text = load_text(RULES_FILE)
    notes_text = load_text(NOTES_FILE)
    pins_text = json.dumps(load_json(PINS_FILE))
    seeds = load_json(SEED_FILE)

    # Inject seeds directly into prompt so GPT integrates & expands them
    seed_text = json.dumps(seeds, indent=2)

    prompt = f"""
You are PopFinder, an event discovery specialist for UK markets, pop-ups, expos,
fairs, and high-footfall commercial opportunities.

USER QUERY:
- Region: {region}
- Keywords: {keywords}

CONTEXT:
- Rules: {rules_text}
- Notes: {notes_text}
- Pinned Events: {pins_text}

BASE DATA (guaranteed real events you MUST include when relevant):
{seed_text}

TASK:
1. Start with the seed events.
2. Filter them to match region or keywords (if relevant).
3. Add NEW events you infer based on patterns, trends, seasonality, footfall,
   market demand, and real UK event structures.
4. Only include events from TODAY forward.
5. All output MUST be a JSON array of objects:

[
  {{
    "title": "",
    "date": "",
    "location": "",
    "description": "",
    "url": ""
  }}
]

Return ONLY JSON.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=2000
    )

    try:
        return json.loads(response.output_text)
    except:
        return seeds   # safety fallback
