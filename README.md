# AQX Trader Automation Test Suite

This project contains automated tests for the AQX Trader web application using **Playwright** with **Python** and **pytest**.

## Project Structure

```
AQX_Auto/
├── tests/
│   ├── conftest.py             # Pytest fixtures (setup, login, authenticated_page)
│   ├── utils.py                # Shared utility functions (e.g., handle_confirmation_modal)
│   ├── test_login.py           # Login functionality tests
│   ├── test_trade.py           # Market order tests (Buy/Sell, SL/TP, Bulk Close)
│   ├── test_manage_orders.py   # Open Position management (Edit SL/TP, Partial Close, Close)
│   ├── test_pending_order.py   # Pending Order tests (Limit/Stop, Edit Price, Cancel)
│   └── test_history.py         # Order History and Notifications verification
├── pytest.ini                  # Pytest configuration (base URL, browser settings)
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## Prerequisites

- Python 3.8+
- Playwright

## Installation

1.  **Clone the repository** (if applicable) or navigate to the project directory.

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Playwright browsers**:
    ```bash
    playwright install chromium
    ```

## Running Tests

### Run All Tests
To run the full test suite with a headed browser (visible UI) and slow-motion enabled (for easier observation):
```bash
pytest
```

### Run Specific Test Files
```bash
pytest tests/test_trade.py
pytest tests/test_manage_orders.py
```

### Run in Headless Mode (Faster, no UI)
Override the `pytest.ini` default settings:
```bash
pytest --headless
```

### View Live Execution Logs
To see `print` statements and detailed execution steps in the console:
```bash
pytest -s
```

## Test Coverage

The automation suite covers the following functional scopes:

1.  **Authentication**:
    *   Successful login with Demo account credentials.

2.  **Market Orders (`test_trade.py`)**:
    *   Place Market **Buy** orders with Stop Loss (SL) and Take Profit (TP).
    *   Place Market **Sell** orders.
    *   Verify orders in the "Open Positions" tab.
    *   **Bulk Close**: Verify ability to close multiple positions at once.

3.  **Manage Open Positions (`test_manage_orders.py`)**:
    *   **Edit Position**: Modify Stop Loss/Take Profit for an existing open position.
    *   **Partial Close**: Close a specific volume (e.g., 0.01 lot) of an open position.
    *   **Close Position**: Close the remaining volume of a position.

4.  **Pending Orders (`test_pending_order.py`)**:
    *   **Limit Orders**: Place a Buy Limit order.
    *   **Stop Orders**: Place a Sell Stop order with Expiry settings.
    *   **Edit Pending Order**: Modify the Price of an active pending order.
    *   **Cancel Order**: Cancel pending orders and verify cleanup.

5.  **History & Notifications (`test_history.py`)**:
    *   Verify that closed orders correctly appear in the **Order History** tab.
    *   (Optional) Check for system notifications upon order execution.

## Configuration

You can adjust test settings in `pytest.ini`:
*   `base_url`: Target environment URL.
*   `addopts`: Default flags (e.g., `--headed`, `--slowmo 1000`).

## Troubleshooting

*   **Selector Issues**: If tests fail due to "Element not found", checks `tests/utils.py` logic for modal handling or updated CSS classes (e.g., for Edit buttons).
*   **Timeout**: Increase timeouts in `expect(locator).to_be_visible(timeout=10000)` if the network is slow.
*   **Login**: Credentials are hardcoded in `tests/conftest.py` for the Demo environment. Update them if expired.
