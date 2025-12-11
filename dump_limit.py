from playwright.sync_api import sync_playwright
import time

def dump_limit_order_page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://aqxtrader.aquariux.com")
        
        # Login
        page.get_by_test_id("tab-login-account-type-demo").click()
        page.get_by_test_id("login-user-id").fill("1000369")
        page.get_by_test_id("login-password").fill("e3!Rb9y6Vn!r")
        page.get_by_test_id("login-submit").click()
        
        page.wait_for_url("**/web/trade")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Select Limit
        order_type_dropdown = page.get_by_test_id("trade-dropdown-order-type")
        order_type_dropdown.click()
        page.get_by_text("Limit", exact=True).click()
        
        time.sleep(2)
        print(page.content())
        browser.close()

if __name__ == "__main__":
    dump_limit_order_page()


