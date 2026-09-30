import sys,json,struct,traceback
import mt5_engine

def read_message():
    b=sys.stdin.buffer.read(4)
    if not b: return None
    n=struct.unpack("<I",b)[0]
    return json.loads(sys.stdin.buffer.read(n).decode("utf-8"))

def send_message(obj):
    b=json.dumps(obj,separators=(",",":")).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("<I",len(b)))
    sys.stdout.buffer.write(b); sys.stdout.buffer.flush()

def result_dict(r):
    if r is None: return None
    out={}
    for k,v in r._asdict().items():
        out[k]=v._asdict() if hasattr(v,"_asdict") else v
    return out

def handle(req):
    a=req.get("action")
    if a=="ping": return {"ok":True,"message":"MT5 Chrome Trader connected"}
    if a=="account": return {"ok":True,"account":mt5_engine.get_account()}
    if a=="quote": return {"ok":True,"quote":mt5_engine.get_quote(req["symbol"])}
    if a=="positions": return {"ok":True,"positions":mt5_engine.get_positions()}
    if a=="orders": return {"ok":True,"orders":mt5_engine.get_orders()}
    if a=="calculate":
        return {"ok":True,"calculation":mt5_engine.calculate_position(
            req["symbol"],float(req["entry"]),float(req["sl"]),
            req.get("risk_percent"),req.get("manual_lot"))}
    if a=="market":
        r=mt5_engine.market_order(req["symbol"],req["side"],float(req["lot"]),
                                  float(req.get("sl",0)),float(req.get("tp",0)))
        return {"ok":r.retcode==mt5_engine.mt5.TRADE_RETCODE_DONE,"result":result_dict(r)}
    if a=="limit":
        r=mt5_engine.limit_order(req["symbol"],req["side"],float(req["lot"]),
                                 float(req["entry"]),float(req.get("sl",0)),float(req.get("tp",0)))
        return {"ok":r.retcode in (mt5_engine.mt5.TRADE_RETCODE_DONE,
                                   mt5_engine.mt5.TRADE_RETCODE_PLACED),"result":result_dict(r)}
    if a=="close":
        r=mt5_engine.close_position(int(req["ticket"]))
        return {"ok":r.retcode==mt5_engine.mt5.TRADE_RETCODE_DONE,"result":result_dict(r)}
    raise ValueError(f"Unknown action: {a}")

def main():
    try:
        mt5_engine.initialize()
        while True:
            req=read_message()
            if req is None: break
            try: res=handle(req)
            except Exception as e: res={"ok":False,"error":str(e),"trace":traceback.format_exc()}
            send_message(res)
    finally:
        mt5_engine.shutdown()

if __name__=="__main__": main()
