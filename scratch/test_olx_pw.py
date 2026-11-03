from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context('.chrome_profile', headless=True)
    page = ctx.new_page()
    page.goto('https://www.olx.com.br/brasil?q=tv+lg+55', wait_until='domcontentloaded', timeout=30000)
    page.wait_for_timeout(3000)
    print("PAGE TITLE:", page.title())
    print("URL:", page.url)
    
    # Try finding items on OLX
    links = page.locator('a[data-ds-component="DS-NewAdCard-Link"], a[href*="/d/"]').all()
    print("TOTAL LINKS OLX:", len(links))
    for a in links[:4]:
        href = a.get_attribute("href")
        print("LINK:", href)
    
    # Also check if __NEXT_DATA__ exists
    next_data = page.evaluate("() => document.getElementById('__NEXT_DATA__') ? document.getElementById('__NEXT_DATA__').textContent.substring(0, 500) : null")
    if next_data:
        print("FOUND __NEXT_DATA__!")
    ctx.close()
