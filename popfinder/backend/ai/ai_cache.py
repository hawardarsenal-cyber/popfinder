import json, os, time

CACHE_FILE = os.path.join(os.path.dirname(__file__), "../storage/ai_cache.json")
TTL = 60 * 60 * 48  # 48 hours

def load_ai_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    return json.load(open(CACHE_FILE))

def save_ai_cache(cache):
    json.dump(cache, open(CACHE_FILE, "w"), indent=2)

def get_event_from_cache(url):
    cache = load_ai_cache()
    if url in cache:
        entry = cache[url]
        if time.time() - entry["timestamp"] < TTL:
            return entry["event"]
        else:
            del cache[url]
            save_ai_cache(cache)
    return None

def write_event_cache(url, event_obj):
    cache = load_ai_cache()
    cache[url] = {
        "timestamp": time.time(),
        "event": event_obj
    }
    save_ai_cache(cache)
