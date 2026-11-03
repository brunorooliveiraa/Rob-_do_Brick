import requests
import urllib.parse
from bs4 import BeautifulSoup
import re
import base64

def buscar_anuncios_reais(termo: str):
    q = urllib.parse.quote_plus(f'site:olx.com.br "{termo}"')
    url = f"https://www.bing.com/search?q={q}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    
    anuncios = []
    for item in soup.select("li.b_algo"):
        t_elem = item.select_one("h2 a")
        snip_elem = item.select_one(".b_caption p")
        if not t_elem:
            continue
            
        titulo = t_elem.get_text(strip=True)
        raw_href = t_elem.get("href", "")
        snippet = snip_elem.get_text(strip=True) if snip_elem else ""
        
        # Bing tracking url decodes to actual destination in 'u' param
        real_url = raw_href
        if "bing.com/ck/a" in raw_href:
            match = re.search(r"u=a1([a-zA-Z0-9_\-]+)", raw_href)
            if match:
                try:
                    padding = 4 - (len(match.group(1)) % 4)
                    b64 = match.group(1) + ("=" * (padding % 4))
                    real_url = base64.b64decode(b64).decode("utf-8", errors="ignore")
                except:
                    pass

        # Procura preço no título ou snippet (ex: R$ 1.500)
        preco_match = re.search(r"R\$\s*([\d\.,]+)", f"{titulo} {snippet}")
        preco = preco_match.group(0) if preco_match else "Consulte"
        
        if "olx.com.br" in real_url and "/d/" in real_url or "/item/" in real_url or "olx.com.br" in real_url:
            anuncios.append({
                "titulo": titulo,
                "preco": preco,
                "url": real_url,
                "snippet": snippet[:100]
            })
            
    return anuncios

res = buscar_anuncios_reais("tv lg 55")
print(f"ENCONTRADOS {len(res)} RESULTADOS REAIS:")
for r in res[:4]:
    print("TÍTULO:", r["titulo"])
    print("PREÇO:", r["preco"])
    print("URL:", r["url"])
    print("-" * 40)
