import requests
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

url = "https://lista.mercadolivre.com.br/smart-tv-lg-55"
res = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(res.text, "html.parser")

# Find any links to /p/ or /MLB-
links = soup.find_all("a", href=re.compile(r"MLB|/p/MLB"))
print(f"Total links encontrados: {len(links)}")

seen = set()
for a in links:
    href = a.get("href")
    title = a.get("title") or a.get_text(strip=True)
    if href and "MLB" in href and href.split("?")[0] not in seen and len(title) > 10:
        seen.add(href.split("?")[0])
        # Find price near this element or in container
        parent = a.find_parent("div", class_=re.compile("poly|ui-search|item"))
        price = ""
        if parent:
            price_elem = parent.select_one(".andes-money-amount__fraction")
            if price_elem:
                price = price_elem.get_text(strip=True)
        print(f"PRODUTO: {title[:50]} | PREÇO: R$ {price} | URL: {href.split('?')[0]}")
        if len(seen) >= 3:
            break
