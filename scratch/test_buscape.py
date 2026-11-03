import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

r = requests.get('https://www.buscape.com.br/search?q=smart+tv+lg+55', headers=headers, timeout=10)
soup = BeautifulSoup(r.text, 'html.parser')

# Find product cards
products = []
for a in soup.find_all('a', href=re.compile(r'/tv/smart-tv-lg-')):
    title = a.get_text(strip=True)
    href = a.get('href')
    if len(title) > 15:
        # find price in parent container
        parent = a.find_parent('div')
        price = ""
        if parent:
            price_match = re.search(r'R\$\s*[\d\.,]+', parent.get_text())
            if price_match:
                price = price_match.group(0)
        full_url = f"https://www.buscape.com.br{href}" if href.startswith('/') else href
        products.append({"title": title, "price": price, "url": full_url})

print(f"ENCONTRADOS {len(products)} PRODUTOS ESPECÍFICOS NO BUSCAPÉ:")
for p in products[:4]:
    print(p)
