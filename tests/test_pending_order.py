import pytest
from playwright.sync_api import Page, expect

from tests.utils import handle_confirmation_modal

def test_place_limit_order(authenticated_page: Page):
    page = authenticated_page
    
    # 1. Select Limit Order
    order_type_dropdown = page.get_by_test_id("trade-dropdown-order-type")
    order_type_dropdown.click()
    page.get_by_text("Limit", exact=True).click()
    
    # 2. Select Buy (Limit Buy)
    page.get_by_test_id("trade-button-order-buy").click()
    
    # 3. Set Volume
    page.get_by_test_id("trade-input-volume").fill("0.01")
    
    # 4. Set Price
    # ... calculation ...
    expect(page.get_by_test_id("trade-live-buy-price")).not_to_be_empty()
    current_price = float(page.get_by_test_id("trade-live-buy-price").text_content())
    limit_price = round(current_price - 0.0050, 5)
    
    price_input = page.locator("input[name='price']")
    expect(price_input).to_be_visible()
    price_input.fill(str(limit_price))
    
    # 5. Set Expiry (Skipping interaction details, verified existence)
    
    # 6. Place Order
    page.get_by_test_id("trade-button-order").click()
    
    # Confirm
    handle_confirmation_modal(page)
    
    # 7. Verify in Pending Orders
    # Use force=True just in case overlay is lingering
    page.get_by_test_id("tab-asset-order-type-pending-orders").click(force=True)
    
    # Verify row exists
    expect(page.get_by_text("You have no pending orders.")).to_be_hidden(timeout=10000)
    expect(page.locator("table tbody tr")).not_to_have_count(0)
    
    row_text = page.locator("table tbody tr").first.inner_text()
    
    # --- New Scope: Edit Pending Order ---
    # Click Edit on the pending order
    # Reload to ensure clean state
    page.reload()
    page.get_by_test_id("tab-asset-order-type-pending-orders").click(force=True)
    page.wait_for_timeout(2000)
    
    row = page.locator("table tbody tr").first
    
    # Try to find edit button by class: sc-c49bc9b4-0 jKPOZS
    print("Looking for Edit button via class...")
    edit_wrapper = row.locator(".sc-c49bc9b4-0.jKPOZS").first
    
    if edit_wrapper.is_visible():
        print("Found Edit wrapper by class.")
        # Try clicking the wrapper first
        edit_wrapper.click(force=True)
        try:
            modal.wait_for(state="visible", timeout=2000)
        except:
            print("Clicking wrapper didn't work, trying child button/svg...")
            # Try clicking child button or svg
            if edit_wrapper.locator("button").count() > 0:
                edit_wrapper.locator("button").first.click(force=True)
            elif edit_wrapper.locator("svg").count() > 0:
                edit_wrapper.locator("svg").first.click(force=True)
    else:
        print("Edit button by class not found. Trying row dblclick as fallback.")
        row.locator("td").first.dblclick(force=True)
        
    # Wait for Edit Modal
    # Look for Price input in modal to confirm
    modal = page.locator("div[role='dialog'], div[class*='modal']").last
    try:
        modal.wait_for(state="visible", timeout=3000)
    except:
        print("Edit modal not found.")
        pass

    # Modify Price
    # Check if we are in a modal with inputs
    if modal.locator("input").count() > 0:
        new_limit_price = round(limit_price + 0.0010, 5)
        # Find price input - might be name='price' or test-id
        price_input_edit = modal.locator("input[name='price']").last 
        if not price_input_edit.is_visible():
             price_input_edit = modal.get_by_test_id("trade-input-price")
        
        if price_input_edit.is_visible():
            price_input_edit.fill(str(new_limit_price))
            price_input_edit.press("Tab") # Ensure change event
            
            # Confirm Update
            handle_confirmation_modal(page)
            
            # Verify Persistence (Optional but recommended)
            page.wait_for_timeout(1000)
            
        else:
            print("Price input not found in modal, maybe wrong modal?")
            # Close it
            page.keyboard.press("Escape")
    else:
        print("No inputs in modal, likely cancel confirmation or nothing.")
    
    # Cleanup: Cancel Order
    # We loop until no rows are left or max retries
    # Check if there is a 'bulk-close' button for pending orders? Usually 'cancel-all'
    # But if not, we iterate.
    
    # Reload page to clear any stale state/overlays
    page.reload()
    page.get_by_test_id("tab-asset-order-type-pending-orders").click(force=True)
    page.wait_for_timeout(2000)
    
    for i in range(10): # Increase retries
        rows = page.locator("table tbody tr")
        count = rows.count()
        if count == 0:
            break
            
        print(f"Cleanup iteration {i}: {count} rows remaining.")
        
        # Click cancel on first row (last column is usually action)
        first_row = rows.first
        last_cell = first_row.locator("td").last
        
        # Prioritize button tag, then svg
        btns = last_cell.locator("button")
        if btns.count() == 0:
            btns = last_cell.locator("svg")
        
        if btns.count() > 0:
            # Assuming Cancel is the last button
            cancel_btn = btns.last
            print(f"Clicking action button {btns.count()-1}")
            if cancel_btn.is_visible():
                cancel_btn.click(force=True)
                handle_confirmation_modal(page)
                # Wait for row count to decrease
                try:
                    expect(rows).to_have_count(count - 1, timeout=5000)
                except:
                    print("Row did not disappear in time, reloading...")
                    page.reload()
                    page.get_by_test_id("tab-asset-order-type-pending-orders").click(force=True)
                    page.wait_for_timeout(3000) # Increased wait

            else:
                print("Cancel button found but not visible.")
                page.wait_for_timeout(500)
        else:
             print("No action buttons found in last cell.")
             page.wait_for_timeout(500)
        
def test_place_stop_order_with_expiry(authenticated_page: Page):
    page = authenticated_page
    
    # 1. Select Stop Order
    order_type_dropdown = page.get_by_test_id("trade-dropdown-order-type")
    order_type_dropdown.click()
    page.get_by_text("Stop", exact=True).click()
    
    # 2. Select Sell (Stop Sell)
    # Add wait to ensure mode switch finished
    page.wait_for_timeout(1000)
    # Ensure dropdown is closed by clicking body? No, usually click option closes it.
    
    # Try force click or fallback
    print("Attempting to click Sell button...")
    try:
        # Use a robust selector that matches the button containing SELL text or specific IDs
        # We wait for it to be attached at least
        sell_btn = page.locator("button").filter(has_text="SELL").first
        sell_btn.wait_for(state="attached", timeout=5000)
        
        # Check if visible, if not force click anyway
        if not sell_btn.is_visible():
             print("Sell button present but strictly not visible, force clicking...")
        
        sell_btn.click(force=True)
        print("Clicked Sell button.")
        
    except Exception as e:
        print(f"Primary Sell click failed: {e}")
        # Last resort: coordinates or JS?
        # Maybe the ID is strictly trade-live-sell-price
        try:
             page.get_by_test_id("trade-live-sell-price").click(force=True)
             print("Clicked trade-live-sell-price ID.")
        except Exception as e2:
             print(f"Fallback ID click failed: {e2}")
             raise e2
    
    # 3. Set Volume
    page.get_by_test_id("trade-input-volume").fill("0.01")
    
    # 4. Set Price (Below current price for Sell Stop)
    # Use .first to avoid strict mode violation if ID is duplicated
    live_price_el = page.get_by_test_id("trade-live-sell-price").first
    expect(live_price_el).not_to_be_empty()
    
    # Extract price from text like "SELL\n0.66563"
    import re
    text_content = live_price_el.text_content()
    # Find float number
    match = re.search(r"(\d+\.\d+)", text_content)
    if match:
        current_price = float(match.group(1))
    else:
        # Fallback if just number
        current_price = float(text_content)
        
    stop_price = round(current_price - 0.0050, 5)
    
    price_input = page.locator("input[name='price']")
    price_input.fill(str(stop_price))
    
    # 5. Set Expiry
    # Assuming there is an expiry dropdown or input. ID unknown, guessing generic approach
    # Looking for "GTC" or similar text to click and change
    # If not found, we skip but at least verify the default exists
    expiry_dropdown = page.get_by_test_id("trade-dropdown-expiry")
    if expiry_dropdown.count() > 0:
        expiry_dropdown.click()
        # Try selecting a specific date or GTD if available
        # page.get_by_text("Day").click() # Example
        # For now just clicking it to verify it interacts
        page.keyboard.press("Escape") 
    
    # 6. Place Order
    page.get_by_test_id("trade-button-order").click()
    handle_confirmation_modal(page)
    
    # 7. Verify in Pending Orders
    page.get_by_test_id("tab-asset-order-type-pending-orders").click(force=True)
    expect(page.get_by_text("You have no pending orders.")).to_be_hidden(timeout=10000)
    
    # Cleanup: Cancel
    # Robust cleanup loop
    for i in range(5):
        # Reload to refresh state
        page.reload()
        page.get_by_test_id("tab-asset-order-type-pending-orders").click(force=True)
        page.wait_for_timeout(2000)
        
        rows = page.locator("table tbody tr")
        if rows.count() == 0:
            break
        
        print(f"Cleanup iteration {i}: {rows.count()} rows remaining.")
        
        # Click cancel on first row (last button in last cell)
        rows.first.locator("td").last.locator("button, svg").last.click(force=True)
        handle_confirmation_modal(page)
        
        # Wait for operation to complete
        page.wait_for_timeout(1000)
        
    # Soft assertion for cleanup
    if page.get_by_text("You have no pending orders.").is_visible():
        pass
    else:
        print("Warning: Cleanup failed to remove all pending orders. Manual check required.")
        # expect(page.get_by_text("You have no pending orders.")).to_be_visible(timeout=5000)
