import requests

def fetch_page(url: str) -> str:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        r = requests.get(url, timeout=10, headers=headers)
        if r.status_code == 200:
            return r.text
    except:
        pass
    return ""
