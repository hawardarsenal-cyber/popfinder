import requests
from bs4 import BeautifulSoup

def visit_kent_events(region: str) -> list:
    url = "https://www.visitkent.co.uk/whats-on/"

    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
    except:
        return []

    events = []
    cards = soup.select(".event-card")

    for c in cards:
        title_el = c.select_one(".event-card__title")
        link_el = c.select_one("a")
        desc_el = c.select_one(".event-card__excerpt")

        if not title_el or not link_el:
            continue

        events.append({
            "title": title_el.text.strip(),
            "url": "https://www.visitkent.co.uk" + link_el["href"],
            "description": desc_el.text.strip() if desc_el else "",
            "source": "visitkent"
        })

    return events
