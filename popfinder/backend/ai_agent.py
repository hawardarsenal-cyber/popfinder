from fastapi import FastAPI
import uvicorn
from collectors.google_search import google_collect
from collectors.basic_scraper import extract_event_details
import json

app = FastAPI()

@app.post("/search")
async def search(payload: dict):
    query = payload.get("query")
    location = payload.get("location")

    # Expand query using simple AI rules (Phase 1 placeholder)
    expanded = f"{query} events shows fairs exhibitions markets {location}"

    # Stage 1: Collect Google results
    urls = google_collect(expanded)

    # Stage 2: Scrape + extract details
    events = []
    for url in urls:
        info = extract_event_details(url)
        if info:
            events.append(info)

    # Stage 3: Sort by score
    sorted_events = sorted(events, key=lambda x: x["score"], reverse=True)

    return {"results": sorted_events}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5001)
