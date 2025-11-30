from fastapi import FastAPI
from pydantic import BaseModel

from backend.ai.query_expand import generate_urls
from backend.collectors.generic_scraper import fetch_page
from backend.ai.extract_event import extract_event
from backend.ai.score_event import score_event


class SearchPayload(BaseModel):
    keywords: str
    region: str


app = FastAPI()


@app.post("/search")
async def search(payload: SearchPayload):
    keywords = payload.keywords
    region = payload.region

    urls = generate_urls(keywords, region)
    results = []

    for url in urls:
        text = fetch_page(url)
        if not text:
            continue

        extracted_events = extract_event(text, url)
        if not extracted_events:
            continue

        for ev in extracted_events:
            ev["url"] = url
            results.append(score_event(ev))

    # Sort by score
    results.sort(key=lambda x: x.get("score", 0), reverse=True)

    return results
