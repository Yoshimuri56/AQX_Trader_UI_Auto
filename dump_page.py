from playwright.sync_api import sync_playwright

def dump_login_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://aqxtrader.aquariux.com")
        page.wait_for_load_state("networkidle")
        print(page.content())
        browser.close()

if __name__ == "__main__":
    dump_login_page()


