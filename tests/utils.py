from playwright.sync_api import Page, expect

import re

def handle_confirmation_modal(page: Page):
    """
    Handles the order confirmation modal or any generic confirmation modal.
    Waits for the Confirm button to appear, clicks it, and waits for the overlay to disappear.
    """
    print("Handling confirmation modal...")
    try:
        # 1. Try generic Confirm button ID
        # Try both "trade-confirmation-button-confirm" AND "trade-confirmation-button-update"
        confirm_btn = page.get_by_test_id("trade-confirmation-button-confirm")
        update_btn = page.get_by_test_id("trade-confirmation-button-update")
        
        target_btn = None
        if confirm_btn.is_visible():
            target_btn = confirm_btn
        elif update_btn.is_visible():
            target_btn = update_btn
        
        # Check if visible immediately or within short timeout
        try:
            if not target_btn:
                # Wait for either
                 try:
                     confirm_btn.wait_for(state="visible", timeout=1500)
                     target_btn = confirm_btn
                 except:
                     update_btn.wait_for(state="visible", timeout=1500)
                     target_btn = update_btn
            
            if target_btn:
                print(f"Found confirm/update button by ID: {target_btn}")
                target_btn.click(force=True)
                
                # Wait for overlay to disappear if present
                overlay = page.locator("#overlay-aqx-trader").first
                try:
                    if overlay.is_visible(timeout=1000):
                        overlay.wait_for(state="hidden", timeout=5000)
                except:
                    pass # Overlay handling optional
                return
        except:
            print("Confirm/Update button ID not found or visible.")
            pass

        # 2. Fallback: Find by text
        action_words = "confirm|update|delete|yes|cancel order|close position|close|ok" # Added update
        try:
            # Look for button in a dialog/modal container first
            # If overlay is visible, the modal is likely inside it or related
            overlay = page.locator("#overlay-aqx-trader").first
            modal_context = None
            
            if overlay.is_visible():
                print("Overlay is visible, searching inside overlay for buttons...")
                modal_context = overlay
            else:
                print("Overlay not visible, searching for generic modal containers...")
                modal_context = page.locator("div[role='dialog'], div[class*='modal']").last
            
            if modal_context and modal_context.is_visible():
                print("Scanning buttons in modal context...")
                # Debug: print all button texts
                all_btns = modal_context.locator("button").all()
                btn_texts = [b.inner_text().strip() for b in all_btns if b.is_visible()]
                print(f"Visible buttons: {btn_texts}")

                # Try regex match
                btn = modal_context.locator("button").filter(has_text=re.compile(action_words, re.IGNORECASE)).first
                if btn.is_visible():
                     print(f"Clicking fallback button by text: {btn.inner_text()}")
                     btn.click(force=True)
                     return
                
                # If no text match, try the last button (heuristic)
                # Usually: [Cancel] [Confirm]
                btns = modal_context.locator("button")
                if btns.count() > 0:
                    last_btn = btns.last
                    last_text = last_btn.inner_text().strip().upper()
                    print(f"Checking last button: {last_text}")
                    
                    if "CANCEL" not in last_text:
                        print(f"Clicking last button: {last_text}")
                        last_btn.click(force=True)
                        return
                    else:
                        # If last is Cancel, try previous
                        if btns.count() > 1:
                            prev_btn = btns.nth(btns.count() - 2)
                            print(f"Last was Cancel. Clicking previous: {prev_btn.inner_text()}")
                            prev_btn.click(force=True)
                            return
            else:
                print("No visible modal context found.")
                
        except Exception as ex:
            print(f"Fallback search failed: {ex}")

        # 3. Handle stuck overlay (if we didn't return yet)
        overlay = page.locator("#overlay-aqx-trader").first
        if overlay.is_visible():
            print("Overlay still visible, waiting for it to hide...")
            overlay.wait_for(state="hidden", timeout=3000)

    except Exception as e:
        print(f"Modal handling warning: {e}")


