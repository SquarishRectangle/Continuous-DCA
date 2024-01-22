import random
import time
from datetime import datetime, timedelta

from alpaca.common import APIError
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import OrderRequest
from ratelimit import limits, sleep_and_retry
from rich import print

from config import CFG


tradeAPI = TradingClient(**CFG.alpaca_auth)
dataAPI = StockHistoricalDataClient(**CFG.alpaca_auth)

with open('sp500.txt') as f:
    TICKERS = f.read().split('\n')

def set_target():
    global TARGET, MIN_DELTA
    eq = float(tradeAPI.get_account().equity) 
    num = len(TICKERS)
    TARGET = round(eq/num, 2)
    MIN_DELTA = max(1, round(TARGET/100, 2))
    print(f'Equity: ${eq} | Tickers: {num} | Target: ${TARGET} | Min Delta: ${MIN_DELTA}')

@sleep_and_retry
@limits(10, 9)
def set_orders(ticker: str):
    try:
        value = float(tradeAPI.get_open_position(ticker).market_value)
    except APIError:
        value = 0
    
    delta = TARGET - value
    if abs(delta) > MIN_DELTA:
        tradeAPI.submit_order(OrderRequest(
            symbol=ticker,
            notional=round(abs(delta), 2),
            side='buy' if delta > 0 else 'sell',
            type='market',
            time_in_force='day'
        ))


def main():
    print('Starting')
    set_target()
    tickers = random.sample(TICKERS, k=len(TICKERS))
    while True:
        set_target()
        for ticker in tickers:
            clock = tradeAPI.get_clock()
            if not clock.is_open:
                nt = clock.next_open.timestamp()
                t = nt - datetime.now().timestamp()
                print(f'Sleeping {timedelta(seconds=int(t))} until {datetime.fromtimestamp(nt)}')
                time.sleep(t)
                set_target()
                tickers = random.sample(TICKERS, k=len(TICKERS))
            set_orders(ticker)
    

if __name__ == '__main__':
    main()
        