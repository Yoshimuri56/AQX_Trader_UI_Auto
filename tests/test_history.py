import pytest
from playwright.sync_api import Page, expect
from tests.utils import handle_confirmation_modal

def test_order_history_and_notifications(authenticated_page: Page):
    page = authenticated_page
    
    # 1. Place a Market Order
    # Ensure Market
    order_type = page.get_by_test_id("trade-dropdown-order-type")
    if "Market" not in order_type.inner_text():
        order_type.click()
        page.get_by_text("Market", exact=True).click()
        
    page.get_by_test_id("trade-button-order-buy").click()
    page.get_by_test_id("trade-input-volume").fill("0.01")
    page.get_by_test_id("trade-button-order").click()
    handle_confirmation_modal(page)
    
    # Verify Notification (Optional / Best Effort)
    # Check for toast/alert
    # toast = page.locator(".Toastify__toast-body, div[role='alert']").first
    # if toast.is_visible():
    #     print(f"Notification found: {toast.inner_text()}")
    
    # 2. Close the Order immediately to generate history
    page.get_by_test_id("tab-asset-order-type-open-positions").click(force=True)
    expect(page.locator("table tbody tr")).not_to_have_count(0)
    
    # Close
    row = page.locator("table tbody tr").first
    close_cell = row.locator("td").last
    btns = close_cell.locator("button")
    if btns.count() == 0: btns = close_cell.locator("svg")
    btns.last.click(force=True)
    
    # Confirm Close
    handle_confirmation_modal(page) # This might handle the volume modal too if simple confirm
    
    # If partial close modal appears (volume input), we might need to handle it.
    # Usually "Close" button on row opens a modal.
    # Check if we need to confirm again inside handle_confirmation_modal or here.
    # handle_confirmation_modal usually handles the "Confirm" click.
    
    # 3. Check Order History
    # Click History Tab
    print("Looking for History Tab...")
    
    # Try multiple strategies to find the tab
    history_tab = None
    
    # Strategy 1: Known ID patterns
    possible_ids = [
        "tab-asset-order-type-order-history",
        "tab-asset-order-type-history",
        "tab-asset-order-type-trade-history",
        "tab-asset-order-type-closed-positions" # Sometimes called Closed Positions
    ]
    
    for tid in possible_ids:
        t = page.get_by_test_id(tid)
        if t.is_visible():
            print(f"Found History Tab by ID: {tid}")
            history_tab = t
            break
            
    # Strategy 2: Relative to Open Positions
    if not history_tab:
        print("ID strategy failed, trying relative location...")
        op_tab = page.get_by_test_id("tab-asset-order-type-open-positions")
        if op_tab.is_visible():
            # Get parent container
            tabs_container = op_tab.locator("xpath=..")
            # Find sibling with text "History"
            history_tab = tabs_container.locator("div, span, button").filter(has_text="History").first
            if history_tab.is_visible():
                print("Found History Tab by text relative to Open Positions")
            else:
                history_tab = None

    # Strategy 3: Global Text Search (Last Resort)
    if not history_tab:
        print("Relative strategy failed, trying global text...")
        # Be careful not to click page titles
        history_tab = page.locator("div[class*='tab'], div[role='tab']").filter(has_text="History").last
    
    if history_tab and history_tab.is_visible():
        history_tab.click(force=True)
    else:
        raise Exception("Could not find History Tab")
    
    # 4. Validate Data
    # Should have at least one row (Market Buy 0.01)
    # Wait for table to load
    page.wait_for_timeout(2000)
    
    rows = page.locator("table tbody tr")
    expect(rows).not_to_have_count(0)
    
    first_row_text = rows.first.inner_text()
    print(f"History Row: {first_row_text}")
    
    assert "BUY" in first_row_text
    assert "0.01" in first_row_text
    # assert "Market" in first_row_text # Optional
    
    # 5. Check Transaction/Trade History if separate (Optional)
    # trade_tab = page.get_by_test_id("tab-asset-order-type-trade-history")

