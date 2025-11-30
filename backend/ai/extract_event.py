from backend.open_client import client
from backend.ai.json_utils import clean_json
import json

def extract_event(page_text: str, url: str):
    prompt = f"""
    Extract ALL event information from this webpage content.

    Return ONLY valid JSON.
    If multiple events exist, return:
    {{
        "events": [ ... ]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        ai_text = response.choices[0].message.content
        print("\n=== RAW GPT EVENT EXTRACT ===")
        print(ai_text)
        print("====================================\n")

        cleaned = clean_json(ai_text)

        # Parse JSON
        data = json.loads(cleaned)

        # Normalize to list
        if isinstance(data, dict) and "events" in data:
            return data["events"]
        elif isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return data
        else:
            return []

    except Exception as e:
        print("EXTRACT FAILED:", e)
        return []
