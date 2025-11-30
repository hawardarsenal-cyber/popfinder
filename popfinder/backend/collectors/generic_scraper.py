import requests
from bs4 import BeautifulSoup

def fetch_page(url):
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(" ", strip=True)
    except:
        return None
