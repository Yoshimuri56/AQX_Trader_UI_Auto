from playwright.sync_api import sync_playwright
import time

def dump_trade_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://aqxtrader.aquariux.com")
        
        # Login
        page.get_by_test_id("tab-login-account-type-demo").click()
        page.get_by_test_id("login-user-id").fill("1000369")
        page.get_by_test_id("login-password").fill("e3!Rb9y6Vn!r")
        page.get_by_test_id("login-submit").click()
        
        # Wait for trade page
        page.wait_for_url("**/web/trade")
        page.wait_for_load_state("networkidle")
        
        # Wait a bit more for dynamic content
        time.sleep(5)
        
        print(page.content())
        browser.close()

if __name__ == "__main__":
    dump_trade_page()


