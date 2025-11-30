import os

DATA_PATH = "backend/data/rules.txt"

def load_rules():
    if not os.path.exists(DATA_PATH):
        return ""
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return f.read()
