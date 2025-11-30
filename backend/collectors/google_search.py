import requests
import os

API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

def google_search(query: str):
    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        "key": API_KEY,
        "cx": SEARCH_ID,
        "q": query
    }

    r = requests.get(url, params=params).json()

    urls = []
    if "items" in r:
        for item in r["items"]:
            urls.append(item["link"])

    return urls
