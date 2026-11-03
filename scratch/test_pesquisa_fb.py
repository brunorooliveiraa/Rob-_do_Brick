import time
import urllib.parse
from playwright.sync_api import sync_playwright

def test_fb_search():
    termo = "JBL PartyBox"
    cidade = "fortaleza"
    url = f"https://www.facebook.com/marketplace/{cidade}/search?query={urllib.parse.quote_plus(termo)}"
    print(f"Testando busca no Facebook: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=".chrome_profile",
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            viewport={"width": 1366, "height": 768}
        )
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=40000)
        time.sleep(3)
        page.keyboard.press("Escape")
        time.sleep(1)

        # Rola um pouco
        page.evaluate("window.scrollBy(0, 800);")
        time.sleep(1.5)

        items = page.locator('a[href*="/marketplace/item/"]').all()
        print(f"Total de itens encontrados na busca: {len(items)}")

        resultados = []
        for it in items[:10]:
            href = it.get_attribute("href") or ""
            text = it.inner_text().strip()
            linhas = [l.strip() for l in text.split("\n") if l.strip()]
            resultados.append({"href": href, "linhas": linhas})

        browser.close()

        for r in resultados:
            print("--- ITEM ---")
            print("Linhas:", r["linhas"])

if __name__ == "__main__":
    test_fb_search()
