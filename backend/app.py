from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow all origins (or replace with your domain)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from backend.ai.query_expand import generate_urls
from backend.collectors.generic_scraper import fetch_page
from backend.ai.extract_event import extract_event
from backend.ai.score_event import score_event


class SearchPayload(BaseModel):
    keywords: str
    region: str


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head><title>Popfinder API</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h2>Popfinder Backend is running ✔</h2>
        <p>This is the backend API. To explore endpoints, visit:</p>
        <a href="/docs"><strong>/docs</strong></a>
    </body>
    </html>
    """


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

