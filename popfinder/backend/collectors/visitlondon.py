import requests
from bs4 import BeautifulSoup

def visit_london_events() -> list:
    url = "https://www.visitlondon.com/things-to-do/whats-on/event/"

    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
    except:
        return []

    events = []
    cards = soup.select(".search-result")

    for c in cards:
        title_el = c.select_one(".search-result-title")
        link_el = c.select_one("a")
        desc_el = c.select_one(".search-result-description")

        if not title_el or not link_el:
            continue

        events.append({
            "title": title_el.text.strip(),
            "url": "https://www.visitlondon.com" + link_el["href"],
            "description": desc_el.text.strip() if desc_el else "",
            "source": "visitlondon"
        })

    return events
