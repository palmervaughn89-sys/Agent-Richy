import os, sys, alpaca_trade_api as t
from alpaca_keys import *
from trading_router import RichyTradingEngine
os.environ["RICHY_DB_PATH"] = "data/richy.duckdb"
a = t.REST(API_KEY, SECRET_KEY, BASE_URL)
e = RichyTradingEngine()
mode = sys.argv[1] if len(sys.argv) > 1 else "help"
if mode == "sell":
    positions = a.list_positions()
    for p in positions:
        side = "sell" if p.side == "long" else "buy"
        a.submit_order(symbol=p.symbol, qty=p.qty, side=side, type="market", time_in_force="day")
        print(f"CLOSED {p.symbol}")
    print(f"Closed {len(positions)} positions")
elif mode == "buy":
    p = e.get_weekly_picks(5)
    print(f"Market: {p.market_regime}")
    for s in p.longs:
        try:
            qty = max(1, int(1000 / s.price))
            a.submit_order(symbol=s.ticker, qty=qty, side="buy", type="market", time_in_force="day")
            print(f"BUY {s.ticker} x{qty}")
        except Exception as ex:
            print(f"SKIP {s.ticker}: {ex}")
    for s in p.shorts:
        try:
            qty = max(1, int(1000 / s.price))
            a.submit_order(symbol=s.ticker, qty=qty, side="sell", type="market", time_in_force="day")
            print(f"SHORT {s.ticker} x{qty}")
        except Exception as ex:
            print(f"SKIP {s.ticker}: {ex}")
elif mode == "status":
    acct = a.get_account()
    print(f"Cash: ${acct.cash}")
    print(f"Portfolio: ${acct.portfolio_value}")
    positions = a.list_positions()
    for p in positions:
        print(f"  {p.side:5s} {p.symbol:8s} qty={p.qty} P/L=${p.unrealized_pl}")
else:
    print("Usage: python richy_trader.py buy|sell|status")
