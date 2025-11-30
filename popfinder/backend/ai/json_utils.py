import re

def clean_json(text: str) -> str:
    """
    Remove markdown ```json fences and return pure JSON.
    """
    if not text:
        return text

    text = text.strip()

    # Remove ```json or ```anything at TOP
    if text.startswith("```"):
        text = re.sub(r"^```[\w-]*\n?", "", text)

    # Remove trailing ```
    if text.endswith("```"):
        text = text[:text.rfind("```")]

    return text.strip()