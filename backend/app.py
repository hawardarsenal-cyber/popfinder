from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from backend.ai.search_engine import smart_event_search
from backend.storage.rules import load_rules
from backend.storage.pins import load_pins, save_pin, delete_pin
from backend.storage.notes import load_notes, add_note

app = FastAPI()

# -------------------------------------------------------
# CORS CONFIG
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# MODELS
# -------------------------------------------------------
class SearchPayload(BaseModel):
    prompt: str
    region: str | None = None


class PinPayload(BaseModel):
    event: dict


class NotePayload(BaseModel):
    text: str


# -------------------------------------------------------
# HOME ROUTE
# -------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html><body style="font-family:Arial;padding:20px">
        <h2>PopFinder Backend Running ✔</h2>
        <p>Visit <a href='/docs'>/docs</a></p>
    </body></html>
    """


# -------------------------------------------------------
# MAIN SEARCH
# -------------------------------------------------------
@app.post("/search")
async def search(payload: SearchPayload):

    rules = load_rules()
    pins = load_pins()
    notes = load_notes()

    results = smart_event_search(
        user_prompt=payload.prompt,
        region=payload.region,
        rules=rules,
        pins=pins,
        notes=notes
    )

    return results


# -------------------------------------------------------
# PINNED EVENTS
# -------------------------------------------------------
@app.get("/pins")
async def get_pins():
    return load_pins()


@app.post("/pin")
async def pin_event(data: PinPayload):
    save_pin(data.event)
    return {"status": "pinned"}


@app.delete("/pin")
async def remove_pin(data: PinPayload):
    delete_pin(data.event)
    return {"status": "removed"}


# -------------------------------------------------------
# NOTES
# -------------------------------------------------------
@app.get("/notes")
async def get_notes():
    return load_notes()


@app.post("/notes")
async def add_new_note(data: NotePayload):
    add_note(data.text)
    return {"status": "saved"}


# -------------------------------------------------------
# OPTIONAL: VIEW RULES.TXT
# -------------------------------------------------------
@app.get("/rules")
async def get_rules():
    return {"rules": load_rules()}
