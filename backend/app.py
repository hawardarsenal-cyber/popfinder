from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from backend.ai.query_expand import generate_urls
from backend.collectors.generic_scraper import fetch_page
from backend.ai.extract_event import extract_event
from backend.ai.score_event import score_event


# --------------------------------------------------------
# 1) Create FastAPI app FIRST
# --------------------------------------------------------
app = FastAPI()

# --------------------------------------------------------
# 2) Add CORS middleware AFTER app exists
# --------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow everything or restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------
# 3) Models
# --------------------------------------------------------
class SearchPayload(BaseModel):
    keywords: str
    region: str


# --------------------------------------------------------
# 4) Simple home route to confirm backend is alive
# --------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head><title>PopFinder API</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h2>PopFinder Backend is running ✔</h2>
        <p>Visit <a href='/docs'>/docs</a> for the API explorer.</p>
    </body>
    </html>
    """


# --------------------------------------------------------
# 5) Search endpoint
# --------------------------------------------------------
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

    # Sort events by score
    results.sort(key=lambda x: x.get("score", 0), reverse=True)

    return results
