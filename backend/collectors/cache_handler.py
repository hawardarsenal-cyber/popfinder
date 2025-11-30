import json, os, time

CACHE_FILE = os.path.join(os.path.dirname(__file__), "../storage/collector_cache.json")
TTL = 60 * 60 * 6  # 6 hours

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    return json.load(open(CACHE_FILE))

def save_cache(cache):
    json.dump(cache, open(CACHE_FILE, "w"), indent=2)

def get_from_cache(key):
    cache = load_cache()
    if key in cache:
        entry = cache[key]
        if time.time() - entry["timestamp"] < TTL:
            return entry["data"]
        else:
            del cache[key]
            save_cache(cache)
    return None

def write_cache(key, data):
    cache = load_cache()
    cache[key] = {
        "timestamp": time.time(),
        "data": data
    }
    save_cache(cache)
