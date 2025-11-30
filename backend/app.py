from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os

from backend.ai.search_engine import smart_event_search

# -----------------------------------------------------------
# FILE PATHS
# -----------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RULES_FILE = os.path.join(DATA_DIR, "rules.txt")
NOTES_FILE = os.path.join(DATA_DIR, "notes.txt")
PINS_FILE = os.path.join(DATA_DIR, "pins.json")

# -----------------------------------------------------------
# FASTAPI APP
# -----------------------------------------------------------
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------
# MODELS
# -----------------------------------------------------------
class SearchPayload(BaseModel):
    region: str
    keywords: str = ""

class PinPayload(BaseModel):
    content: dict

class NotesPayload(BaseModel):
    text: str

class RulesUpdatePayload(BaseModel):
    text: str


# -----------------------------------------------------------
# ROUTES
# -----------------------------------------------------------

@app.get("/")
def home():
    return {"status": "PopFinder Backend Running"}


@app.post("/search")
async def search(payload: SearchPayload):
    try:
        events = smart_event_search(payload.region, payload.keywords)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rules")
def get_rules():
    with open(RULES_FILE, "r", encoding="utf-8") as f:
        return {"rules": f.read()}


@app.post("/rules/update")
def update_rules(payload: RulesUpdatePayload):
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        f.write(payload.text)
    return {"status": "updated"}


@app.post("/notes")
def save_notes(payload: NotesPayload):
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(payload.text + "\n\n")
    return {"status": "saved"}


@app.get("/notes")
def read_notes():
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        return {"notes": f.read()}


@app.post("/pin")
def save_pin(payload: PinPayload):
    try:
        with open(PINS_FILE, "r", encoding="utf-8") as f:
            pins = json.load(f)
    except:
        pins = []

    pins.append(payload.content)

    with open(PINS_FILE, "w", encoding="utf-8") as f:
        json.dump(pins, f, indent=4)

    return {"status": "pinned"}


@app.get("/pins")
def get_pins():
    try:
        with open(PINS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []
