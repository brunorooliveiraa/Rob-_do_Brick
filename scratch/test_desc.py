
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context('.chrome_profile', headless=True)
    page = ctx.new_page()
    page.goto('https://www.facebook.com/marketplace/item/973879062432616/', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(3000)
    lines = [l.strip() for l in page.inner_text('body').split('\n') if l.strip()]
    for i in range(30, len(lines)):
        print(f'{i}: {lines[i]}')
    ctx.close()
