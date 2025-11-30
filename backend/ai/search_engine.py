import json
from openai import OpenAI

client = OpenAI()

def smart_event_search(user_prompt, region, rules, pins, notes):

    # Construct system instructions
    system_prompt = f"""
You are PopFinder, an intelligent event discovery agent.

Use the following RULES to guide your thinking:
---
{rules}
---

Pinned events (avoid duplicates):
---
{json.dumps(pins, indent=2)}
---

Field notes (use to improve interpretation):
---
{json.dumps(notes, indent=2)}
---

Your job:
- Perform a WEB SEARCH across diverse sources.
- Look for pop-up retail, markets, fairs, seasonal events, independent trade opportunities.
- Focus on UK, primarily London & Kent unless user overrides.
- Return structured JSON.

Output format:
[
  {{
    "title": "",
    "date": "",
    "location": "",
    "description": "",
    "links": [],
    "score": 0
  }}
]
"""

    user_query = f"User search: {user_prompt}. Region override: {region}"

    response = client.responses.create(
        model="gpt-4.1",
        reasoning={"effort": "medium"},
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        web_search={"enable": True}
    )

    # Extract structured content
    final_text = response.output_text
    try:
        data = json.loads(final_text)
        return data
    except:
        return {"error": "JSON_PARSE_FAILED", "raw": final_text}
