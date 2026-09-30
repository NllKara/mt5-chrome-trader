import MetaTrader5 as mt5
from risk import calculate_lot, normalize_volume

MAGIC = 26093001

def initialize():
    if not mt5.initialize():
        raise RuntimeError(f"MT5 initialize failed: {mt5.last_error()}")
    if mt5.account_info() is None:
        raise RuntimeError(f"Cannot read MT5 account: {mt5.last_error()}")

def shutdown():
    mt5.shutdown()

def symbol_prepare(symbol):
    info = mt5.symbol_info(symbol)
    if info is None:
        raise ValueError(f"Symbol not found: {symbol}")
    if not info.visible and not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"Cannot select symbol {symbol}")
    return mt5.symbol_info(symbol)

def get_account():
    a = mt5.account_info()
    if a is None:
        raise RuntimeError(str(mt5.last_error()))
    return {"login":int(a.login),"server":a.server,"balance":float(a.balance),
            "equity":float(a.equity),"margin":float(a.margin),
            "free_margin":float(a.margin_free),"profit":float(a.profit),
            "currency":a.currency}

def get_quote(symbol):
    symbol_prepare(symbol)
    t = mt5.symbol_info_tick(symbol)
    if t is None:
        raise RuntimeError(f"No tick for {symbol}")
    return {"bid":float(t.bid),"ask":float(t.ask)}

def get_positions():
    ps = mt5.positions_get() or []
    return [{"ticket":int(p.ticket),"symbol":p.symbol,"type":int(p.type),
             "volume":float(p.volume),"price_open":float(p.price_open),
             "sl":float(p.sl),"tp":float(p.tp),
             "price_current":float(p.price_current),"profit":float(p.profit),
             "comment":p.comment} for p in ps]

def get_orders():
    os = mt5.orders_get() or []
    return [{"ticket":int(o.ticket),"symbol":o.symbol,"type":int(o.type),
             "volume":float(o.volume_current),"price":float(o.price_open),
             "sl":float(o.sl),"tp":float(o.tp),"comment":o.comment} for o in os]

def calculate_position(symbol, entry, sl, risk_percent=None, manual_lot=None):
    info = symbol_prepare(symbol)
    if manual_lot is not None:
        lot = normalize_volume(float(manual_lot), info)
        a = mt5.account_info()
        order_type = mt5.ORDER_TYPE_BUY if sl < entry else mt5.ORDER_TYPE_SELL
        profit = mt5.order_calc_profit(order_type, symbol, lot, entry, sl)
        risk_money = abs(float(profit)) if profit is not None else None
        return {"lot":lot,"risk_money":risk_money,
                "risk_percent":risk_money/float(a.balance)*100 if risk_money is not None else None}
    if risk_percent is None:
        raise ValueError("Provide risk_percent or manual_lot")
    r = calculate_lot(mt5, symbol, entry, sl, float(risk_percent))
    return {"lot":r["lot"],"risk_money":r["risk_money"],"risk_percent":float(risk_percent)}

def filling_mode(info):
    # Some brokers require a specific filling mode. Prefer the symbol's mode.
    return int(info.filling_mode)

def market_order(symbol, side, lot, sl=0.0, tp=0.0):
    info = symbol_prepare(symbol)
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        raise RuntimeError("No market tick")
    if side.upper()=="BUY":
        typ, price = mt5.ORDER_TYPE_BUY, tick.ask
    elif side.upper()=="SELL":
        typ, price = mt5.ORDER_TYPE_SELL, tick.bid
    else:
        raise ValueError("Side must be BUY or SELL")
    req={"action":mt5.TRADE_ACTION_DEAL,"symbol":symbol,"volume":float(lot),
         "type":typ,"price":price,"sl":float(sl or 0),"tp":float(tp or 0),
         "deviation":20,"magic":MAGIC,"comment":"FTC Chrome Trader",
         "type_time":mt5.ORDER_TIME_GTC,"type_filling":filling_mode(info)}
    check=mt5.order_check(req)
    if check is None: raise RuntimeError(f"order_check failed: {mt5.last_error()}")
    res=mt5.order_send(req)
    if res is None: raise RuntimeError(f"order_send failed: {mt5.last_error()}")
    return res

def limit_order(symbol, side, lot, entry, sl=0.0, tp=0.0):
    info=symbol_prepare(symbol)
    typ=mt5.ORDER_TYPE_BUY_LIMIT if side.upper()=="BUY" else mt5.ORDER_TYPE_SELL_LIMIT
    if side.upper() not in ("BUY","SELL"): raise ValueError("Side must be BUY or SELL")
    req={"action":mt5.TRADE_ACTION_PENDING,"symbol":symbol,"volume":float(lot),
         "type":typ,"price":float(entry),"sl":float(sl or 0),"tp":float(tp or 0),
         "magic":MAGIC,"comment":"FTC Chrome Trader","type_time":mt5.ORDER_TIME_GTC,
         "type_filling":filling_mode(info)}
    check=mt5.order_check(req)
    if check is None: raise RuntimeError(f"order_check failed: {mt5.last_error()}")
    res=mt5.order_send(req)
    if res is None: raise RuntimeError(f"order_send failed: {mt5.last_error()}")
    return res

def close_position(ticket):
    ps=mt5.positions_get(ticket=int(ticket))
    if not ps: raise ValueError("Position not found")
    p=ps[0]; tick=mt5.symbol_info_tick(p.symbol); info=mt5.symbol_info(p.symbol)
    if p.type==mt5.POSITION_TYPE_BUY:
        typ,price=mt5.ORDER_TYPE_SELL,tick.bid
    else:
        typ,price=mt5.ORDER_TYPE_BUY,tick.ask
    req={"action":mt5.TRADE_ACTION_DEAL,"symbol":p.symbol,"volume":float(p.volume),
         "type":typ,"position":int(ticket),"price":price,"deviation":20,
         "magic":MAGIC,"comment":"FTC Chrome Close","type_time":mt5.ORDER_TIME_GTC,
         "type_filling":filling_mode(info)}
    res=mt5.order_send(req)
    if res is None: raise RuntimeError(str(mt5.last_error()))
    return res
