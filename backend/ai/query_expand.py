from backend.open_client import client
from backend.ai.json_utils import clean_json
import json

def generate_urls(keywords: str, region: str):
    prompt = f"""
    Generate 5 URLs related to events matching:
    - keywords: {keywords}
    - region: {region}

    Return ONLY a JSON array of strings.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content
    print("\n=== RAW GPT URL RESPONSE ===")
    print(raw)
    print("============================\n")

    cleaned = clean_json(raw)

    try:
        return json.loads(cleaned)
    except:
        print("JSON PARSE FAILED")
        return []
