import time
import re
import urllib.parse
from playwright.sync_api import sync_playwright
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.scraper import sanitizar_preco, normalizar_url_item, descartar_modais

def test_func():
    termo_busca = "JBL PartyBox"
    cidade = "fortaleza"
    preco_referencia = 1400.0

    cidade_slug = cidade.lower().strip().replace(" ", "")
    q_query = urllib.parse.quote_plus(termo_busca.strip())
    url_busca = f"https://www.facebook.com/marketplace/{cidade_slug}/search?query={q_query}"

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=".chrome_profile",
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            viewport={"width": 1366, "height": 768}
        )
        page = ctx.new_page()
        page.goto(url_busca, wait_until="domcontentloaded", timeout=35000)
        time.sleep(2.5)
        descartar_modais(page)
        page.evaluate("window.scrollBy(0, 800);")
        time.sleep(1.5)
        descartar_modais(page)

        elementos = page.locator('a[href*="/marketplace/item/"]').all()
        concorrentes = []
        urls_vistas = set()

        for elem in elementos[:20]:
            if len(concorrentes) >= 8:
                break
            href = elem.get_attribute("href")
            if not href:
                continue
            url_limpa = normalizar_url_item(href)
            if url_limpa in urls_vistas:
                continue
            urls_vistas.add(url_limpa)

            texto = elem.inner_text().strip()
            linhas = [l.strip() for l in texto.split("\n") if l.strip()]
            tags_ignoradas = {"acabou de ser anunciado", "novo", "em alta", "patrocinado", "destaque"}
            linhas_uteis = [l for l in linhas if l.lower() not in tags_ignoradas]
            if not linhas_uteis:
                continue

            preco_num = 0.0
            idx_ultimo_preco = -1
            for i, linha in enumerate(linhas_uteis):
                l_lower = linha.lower()
                if any(kw in l_lower for kw in ["r$", "us$", "grátis", "gratuito", "free"]):
                    if preco_num == 0.0:
                        precos = re.findall(r"(?:r\$|us\$)\s*[\d\.,]+|grátis|gratuito|free", l_lower)
                        if precos:
                            preco_num = sanitizar_preco(precos[0])
                        else:
                            preco_num = sanitizar_preco(linha)
                    idx_ultimo_preco = i
                elif idx_ultimo_preco != -1:
                    # Encontrou a primeira linha de texto após todos os preços
                    break

            if preco_num <= 1.0:
                continue

            if preco_referencia and preco_referencia > 60:
                if preco_num < (preco_referencia * 0.35) or preco_num > (preco_referencia * 3.5):
                    continue

            titulo_concorrente = ""
            if idx_ultimo_preco != -1 and len(linhas_uteis) > idx_ultimo_preco + 1:
                titulo_concorrente = linhas_uteis[idx_ultimo_preco + 1]
            else:
                titulo_concorrente = linhas_uteis[0]

            concorrentes.append({
                "titulo": titulo_concorrente,
                "preco": preco_num,
                "url": url_limpa
            })

        ctx.close()

    print("Concorrentes coletados:", len(concorrentes))
    for c in concorrentes:
        print(f"-> R$ {c['preco']:.2f} | {c['titulo']} | {c['url']}")

    if concorrentes:
        precos = [c["preco"] for c in concorrentes]
        print(f"Preço Médio: R$ {sum(precos)/len(precos):.2f}")
        print(f"Preço Mínimo: R$ {min(precos):.2f}")
        print(f"Preço Máximo: R$ {max(precos):.2f}")

if __name__ == "__main__":
    test_func()
