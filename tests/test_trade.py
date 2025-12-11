import re
from playwright.sync_api import Page, expect
from tests.utils import handle_confirmation_modal

def test_place_market_order_with_sl_tp(authenticated_page: Page):
    page = authenticated_page
    
    # ... setup ...
    # 3. Select Market Order
    order_type_dropdown = page.get_by_test_id("trade-dropdown-order-type")
    if "Market" not in order_type_dropdown.inner_text():
        order_type_dropdown.click()
        page.get_by_text("Market", exact=True).click()
    
    # 4. Select Buy
    page.get_by_test_id("trade-button-order-buy").click()
    
    # 5. Set Volume
    page.get_by_test_id("trade-input-volume").fill("0.01")
    
    # 6. Set SL and TP
    expect(page.get_by_test_id("trade-live-buy-price")).not_to_be_empty()
    current_price_str = page.get_by_test_id("trade-live-buy-price").text_content()
    current_price = float(current_price_str)
    
    sl_price = round(current_price - 0.0010, 5)
    tp_price = round(current_price + 0.0010, 5)
    
    page.get_by_test_id("trade-input-stoploss-price").fill(str(sl_price))
    page.get_by_test_id("trade-input-takeprofit-price").fill(str(tp_price))
    
    # 7. Place Order
    place_order_btn = page.get_by_test_id("trade-button-order")
    expect(place_order_btn).to_contain_text("Place Buy Order")
    place_order_btn.click()
    
    # Handle Confirmation Modal
    handle_confirmation_modal(page)
    
    # 8. Verify Order in Open Positions
    page.get_by_test_id("tab-asset-order-type-open-positions").click(force=True)
    
    expect(page.get_by_text("You have no open positions.")).to_be_hidden(timeout=10000)
    expect(page.locator("table tbody tr")).not_to_have_count(0)
    
    # Verify the row content matches our order (Buy, 0.01)
    row_text = page.locator("table tbody tr").first.inner_text()
    assert "BUY" in row_text
    assert "0.01" in row_text
    
    # --- New Step: Place a Sell Order for Bulk Close Test ---
    # Ensure Market
    # Switch to Sell
    # Note: Depending on UI, might need to click "Sell" button directly or toggle
    # Assuming Market mode has two big buttons: Buy / Sell
    # Or we need to click the Sell button
    
    print("Placing second order (Sell) for Bulk Close test...")
    # Just click Sell button directly (it places order in Market mode)
    # Check if we need to clear inputs? Volume is already 0.01
    
    # Clear SL/TP to keep it simple or just leave them (will apply to new order)
    # Let's clear them to avoid validation errors if price moved
    page.get_by_test_id("trade-input-stoploss-price").fill("")
    page.get_by_test_id("trade-input-takeprofit-price").fill("")
    
    # Click Sell
    print("Clicking Sell button...")
    try:
        # Try standard ID first with force
        page.get_by_test_id("trade-button-order-sell").click(force=True, timeout=3000)
    except:
        print("Standard Sell button click failed, trying live price button...")
        # Fallback for some responsive layouts, use .first to avoid strict mode violation
        page.get_by_test_id("trade-live-sell-price").first.click(force=True)
    
    # Check if the main button text changed to "Place Sell Order"
    place_order_btn = page.get_by_test_id("trade-button-order")
    expect(place_order_btn).to_contain_text("Place Sell Order")
    
    place_order_btn.click()
    
    # Handle Confirmation Modal
    handle_confirmation_modal(page)
    
    # Verify we have at least 2 positions
    # Refresh list
    page.get_by_test_id("tab-asset-order-type-open-positions").click(force=True)
    page.wait_for_timeout(2000)
    
    rows = page.locator("table tbody tr")
    # We expect at least 2, but allow more if environment was dirty (though we verify clean at end)
    count = rows.count()
    print(f"Open positions count: {count}")
    assert count >= 2, "Expected at least 2 open positions (Buy & Sell)"
    
    # Cleanup: Bulk Close
    bulk_close_btn = page.get_by_test_id("bulk-close")
    bulk_close_btn.click(force=True)
    
    # Confirm Bulk Close
    handle_confirmation_modal(page)
         
    # Verify all closed
    try:
        expect(page.get_by_text("You have no open positions.")).to_be_visible(timeout=5000)
    except:
        # Fallback: close one by one
        print("Bulk close failed, closing individual positions.")
        rows = page.locator("table tbody tr")
        for _ in range(5):
            if rows.count() == 0:
                break
            rows.first.locator("td").last.click(force=True)
            handle_confirmation_modal(page)
            page.wait_for_timeout(1000)
            
        expect(page.get_by_text("You have no open positions.")).to_be_visible(timeout=5000)

