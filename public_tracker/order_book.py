# -*- coding: utf-8 -*-

import asyncio
from async_timeout import Any
import ccxt.async_support as ccxt  # noqa: E402


async def loop(exchange_id: str, symbol: str, interval: float) -> None:
    '''fetch order book every interval'''
    exchange_class: ccxt.Exchange = getattr(ccxt, exchange_id)
    exchange: ccxt.Exchange = exchange_class({'enableRateLimit': True})
    orderbook = {}

    await exchange.load_markets()
    while True:
        try:
            orderbook = await exchange.fetch_order_book(symbol)
            push_to_database(orderbook)
            await asyncio.sleep(interval)
        except KeyboardInterrupt:
            break
        except Exception as e:  # pylint: disable=all
            print(type(e).__name__, str(e))
    await exchange.close()


async def main_loop(markets: dict[str, list[str]], interval: float = 300):
    '''main loop'''
    loops = [loop(exchange_id, symbol, interval)
             for exchange_id, symbols in markets.items()
             for symbol in symbols]
    return await asyncio.gather(*loops)


def push_to_database(order_book: dict[str, Any]):
    '''push results to database'''
    print(order_book)


markets_symbol = {
    'binance': ['ONE/USDT'],
    'okex': ['ONE/USDT']
}
results = asyncio.run(main_loop(markets_symbol, 300))
