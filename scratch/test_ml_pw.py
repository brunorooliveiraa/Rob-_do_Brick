from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context('.chrome_profile', headless=True)
    page = ctx.new_page()
    page.goto('https://lista.mercadolivre.com.br/smart-tv-lg-55-usada', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(2000)
    print("PAGE TITLE:", page.title())
    print("URL:", page.url)
    
    # Try finding any products
    titles = page.locator('h2, a[href*="mercadolivre.com.br"]').all_inner_texts()
    print("FOUND TEXTS:", [t for t in titles if len(t) > 10][:5])
    ctx.close()
