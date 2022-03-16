# -*- coding: utf-8 -*-
import json
import asyncio
from typing import Awaitable
from async_timeout import Any
import ccxt.async_support as ccxt
from tracker.connector.ccxt.ccxt_data import CCXTOrderBook
from tracker.database.database import DB_PUBLIC_CREDENTIAL_LOCATION, DBConfig, DataBase

from tracker.database.order_book_orm_data import SQLOrderBook  # noqa: E402

queue = []


async def loop(exchange_id: str, symbol: str, interval: float) -> None:
    '''fetch order book every interval'''
    exchange_class: ccxt.Exchange = getattr(ccxt, exchange_id)
    exchange: ccxt.Exchange = exchange_class({'enableRateLimit': True})
    orderbook = {}

    await exchange.load_markets()
    while True:
        try:
            orderbook = await exchange.fetch_order_book(symbol)
            ccxt_orderbook = CCXTOrderBook.create_with_exchange_id(
                orderbook, exchange_id)
            push_to_database(ccxt_orderbook)
            await asyncio.sleep(interval)
        except KeyboardInterrupt:
            break
        except Exception as e:  # pylint: disable=all
            print(type(e).__name__, str(e))
    await exchange.close()


async def main_loop(
        markets: dict[str, list[str]],
        interval: float = 300) -> Awaitable[None]:
    '''main loop'''
    loops = [loop(exchange_id, symbol, interval)
             for exchange_id, symbols in markets.items()
             for symbol in symbols]
    await asyncio.gather(*loops)

db_config = DBConfig.create(DB_PUBLIC_CREDENTIAL_LOCATION)
database = DataBase(db_config)


def push_to_database(order_book: CCXTOrderBook) -> None:
    '''push results to database'''
    sql_order_book = order_book.to_orm_class(SQLOrderBook, serialize_list=True)
    database.commit_task_list_to_sql([sql_order_book])


markets_symbol = {
    'binance': ['ONE/USDT'],
    'okex': ['ONE/USDT']
}

results = asyncio.run(main_loop(markets_symbol, 60))
