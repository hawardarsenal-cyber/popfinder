import requests
from bs4 import BeautifulSoup

def mall_events() -> list:
    malls = {
        "Bluewater": "https://bluewater.co.uk/events",
        "Westfield London": "https://uk.westfield.com/london/events",
        "Westfield Stratford": "https://uk.westfield.com/stratfordcity/events",
        "Lakeside": "https://lakeside-shopping.com/events"
    }

    results = []

    for name, url in malls.items():
        try:
            html = requests.get(url, timeout=10).text
            soup = BeautifulSoup(html, "html.parser")
        except:
            continue

        cards = soup.select("article, .event, .card")  # generic

        for c in cards:
            title = c.get_text(strip=True)
            if len(title) < 4:
                continue
            results.append({
                "title": f"{name}: {title}",
                "url": url,
                "description": title,
                "source": name.lower().replace(" ", "")
            })

    return results
