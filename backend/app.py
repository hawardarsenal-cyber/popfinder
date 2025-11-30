from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.ai.search_engine import smart_event_search

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class SearchPayload(BaseModel):
    region: str
    keywords: str = ""

@app.get("/")
def root():
    return {"status": "PopFinder Backend Running"}

@app.post("/search")
async def search(payload: SearchPayload):
    try:
        events = smart_event_search(payload.region, payload.keywords)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
