from playwright.sync_api import sync_playwright
import urllib.parse
import re

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context('.chrome_profile', headless=True)
    page = ctx.new_page()
    q = urllib.parse.quote('site:olx.com.br "tv lg 55"')
    page.goto(f'https://www.google.com/search?q={q}', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(2000)
    
    results = page.locator('div.g').all()
    print("TOTAL GOOGLE RESULTS:", len(results))
    for r in results[:4]:
        title = r.locator('h3').first.inner_text()
        link = r.locator('a').first.get_attribute('href')
        snippet = r.inner_text()
        print("TITULO:", title)
        print("LINK:", link)
        # find price in snippet
        price_match = re.search(r"R\$\s*([\d\.,]+)", snippet)
        print("PRECO:", price_match.group(0) if price_match else "Sem preco")
        print("-" * 40)
    ctx.close()
