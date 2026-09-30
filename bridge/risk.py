import math

def normalize_volume(volume, info):
    step = float(info.volume_step)
    minimum = float(info.volume_min)
    maximum = float(info.volume_max)
    if step <= 0:
        return max(minimum, min(maximum, volume))
    volume = math.floor(volume / step + 1e-12) * step
    volume = max(minimum, min(maximum, volume))
    decimals = max(0, len(str(step).split(".")[-1].rstrip("0")))
    return round(volume, decimals)

def calculate_lot(mt5, symbol, entry, sl, risk_percent):
    account = mt5.account_info()
    info = mt5.symbol_info(symbol)
    if account is None:
        raise RuntimeError("Cannot read account information")
    if info is None:
        raise RuntimeError(f"Symbol not found: {symbol}")
    if risk_percent <= 0:
        raise ValueError("Risk must be greater than 0")
    if entry == sl:
        raise ValueError("Entry and SL cannot be the same")
    risk_money = float(account.balance) * risk_percent / 100.0
    order_type = mt5.ORDER_TYPE_BUY if sl < entry else mt5.ORDER_TYPE_SELL
    test_volume = float(info.volume_min)
    profit = mt5.order_calc_profit(order_type, symbol, test_volume, entry, sl)
    if profit is None:
        raise RuntimeError(f"order_calc_profit failed: {mt5.last_error()}")
    loss_per_min_lot = abs(float(profit))
    if loss_per_min_lot <= 0:
        raise RuntimeError("Unable to calculate SL loss")
    raw_lot = risk_money / loss_per_min_lot * test_volume
    return {
        "lot": normalize_volume(raw_lot, info),
        "risk_money": risk_money,
        "raw_lot": raw_lot,
        "balance": float(account.balance)
    }
