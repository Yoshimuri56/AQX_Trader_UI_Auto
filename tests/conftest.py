import pytest
from playwright.sync_api import Page, expect

@pytest.fixture(scope="function")
def authenticated_page(page: Page):
    page.goto("/")
    
    # Check if already logged in (optional, but good for speed if we reused state)
    # For now, just log in every time as it's safer without persistent context setup
    
    # Wait for login page or dashboard
    # If we are on login page:
    if "login" in page.url or page.locator("data-testid=login-submit").is_visible():
        page.get_by_test_id("tab-login-account-type-demo").click()
        page.get_by_test_id("login-user-id").fill("1000369")
        page.get_by_test_id("login-password").fill("e3!Rb9y6Vn!r")
        
        # Wait for button to be enabled
        submit_btn = page.get_by_test_id("login-submit")
        expect(submit_btn).to_be_enabled(timeout=10000)
        submit_btn.click()
        
        # Wait for navigation to trade page
        # Increase timeout
        page.wait_for_url("**/web/trade", timeout=60000)
        page.wait_for_load_state("networkidle")
        
        # Close any welcome modals if they exist (heuristic)
        # page.keyboard.press("Escape")
        
    return page

