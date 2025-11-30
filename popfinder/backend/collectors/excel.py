import requests
from bs4 import BeautifulSoup

def excel_events() -> list:
    url = "https://www.excel.london/whats-on"

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
        desc_el = c.select_one(".event-card__description")

        if not title_el or not link_el:
            continue

        events.append({
            "title": title_el.text.strip(),
            "url": "https://www.excel.london" + link_el["href"],
            "description": desc_el.text.strip() if desc_el else "",
            "source": "excel"
        })

    return events
