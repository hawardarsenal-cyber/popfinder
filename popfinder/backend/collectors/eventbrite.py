import requests
from bs4 import BeautifulSoup

def eventbrite_search(query: str, region: str) -> list:
    url = (
        "https://www.eventbrite.co.uk/d/uk--"
        + region.lower().replace(" ", "-")
        + "/" 
        + query.lower().replace(" ", "-")
        + "/"
    )

    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
    except:
        return []

    events = []
    cards = soup.select(".search-event-card-wrapper")

    for c in cards:
        title_el = c.select_one(".eds-event-card-content__title")
        date_el = c.select_one(".eds-event-card-content__sub-title")
        link_el = c.select_one("a")

        if not title_el or not link_el:
            continue

        events.append({
            "title": title_el.text.strip(),
            "url": link_el["href"],
            "description": date_el.text.strip() if date_el else "",
            "source": "eventbrite"
        })

    return events
