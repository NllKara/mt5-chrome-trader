# MT5 Chrome Trader V5

Chrome Extension + Python Native Messaging bridge for MetaTrader 5.

## V5 MVP
- Market BUY / SELL
- Buy Limit / Sell Limit
- SL / TP
- Auto position sizing by risk %
- Manual lot mode
- Account/equity/balance display
- Open positions
- Close position
- Pending orders
- No EA
- No cloud server required

## Requirements
- Windows
- Google Chrome
- MetaTrader 5 desktop
- Python 3.x
- A demo MT5 account for testing

## Install

1. Install Python.
2. Run:
   `py -m pip install -r bridge/requirements.txt`
3. Open MT5 and log in to a DEMO account.
4. Load `extension/` with Chrome -> chrome://extensions -> Developer mode -> Load unpacked.
5. Copy the extension ID.
6. Edit `native/com.ftc.mt5trader.json` and replace YOUR_EXTENSION_ID with that ID.
7. Edit paths in `native/launch.bat` and `native/install.bat` if the repository is not at C:\\MT5ChromeTrader.
8. Run `native/install.bat` as the Windows user that runs Chrome.
9. Reload the extension.
10. Open the extension and verify CONNECTED.

## Important
Test on DEMO first. This software can send real orders to MT5. Always verify symbol, lot, SL and TP before executing.

The bridge uses MT5's Python API and does not install an EA.
