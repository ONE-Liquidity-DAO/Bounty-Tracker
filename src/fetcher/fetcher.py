from src.fetcher.ccxt_data import CCXTBalance, CCXTBalances, CCXTOrder, CCXTTicker, CCXTTrade
from src.fetcher.create_exchange_classes import ExchangeClass
from src.fetcher.create_bounty_info import BountyInfo
from src.database.database import DataBase
import ccxt.async_support as ccxt
import logging
import asyncio
import pandas as pd
from enum import Enum, auto
logger = logging.getLogger(__name__)

class Methods(Enum):
    FETCH_OKEX_TRADES = auto()
    FETCH_OKEX_ORDERS = auto()
    FETCH_BALANCES = auto()

class Fetcher:
    def __init__(
        self,
        exchange_classes: list[ExchangeClass],
        bounty_infos: list[BountyInfo],
        database: DataBase,
        # queue: asyncio.Queue,
    ) -> None:

        self._exchange_classes = exchange_classes
        self._bounty_infos = bounty_infos
        self._database = database
        # self._queue = queue

    def commit_task_list_to_sql(self, result):
        self._database.commit_task_list_to_sql(result)


    async def fetch_balance(self, exchange_class: ExchangeClass):
        # update all balance to latest based on api every interval
        exchange = exchange_class.exchange
        balances = await exchange.fetch_balance()
        logger.debug(f'{balances}')
        if balances.get('timestamp') is None:
            balances['timestamp'] = exchange.milliseconds()
        ccxt_balances = CCXTBalances(balances)
        account_name = exchange_class.account_name
        exchange_name = exchange_class.exchange_name
        orm_balance_list = ccxt_balances.get_balance_orm_list(
                    exchange_name=exchange_name, account_name=account_name
                )
        self._database.commit_task_list_to_sql(orm_balance_list)
        
    async def fetch_my_okex_orders(self,
                                  exchange_class: ExchangeClass,
                                  symbol: str,
                                  since: int,
                                  params: dict
        ):
            print('fetching')
            orders = await exchange_class.exchange.fetch_closed_orders(
                symbol, since=since, limit=None, params=params
            )
            if len(orders) == 0:
                return [], -1, -1
            # hacky: picking trade at 0 may skip some orders whose order id are the same
            # sql table can handle duplicated entry
            if len(orders) > 1:
                earliest_order_id = orders[1]['id']
            else:
                earliest_order_id = orders[0]['id']
            to = orders[0]['timestamp']
            orm_orders = []
            logger.info(f'fetching {exchange_class}')
            for order in orders:
                order['cancel_timestamp'] = int(order['info']['uTime'])
                ccxt_order = CCXTOrder(**order)
                account_name = exchange_class.account_name
                exchange_name = exchange_class.exchange_name
                orm_order = ccxt_order.to_orm_class(
                    exchange_name=exchange_name, account_name=account_name
                )
                orm_orders.append(orm_order)
            # self._queue.put_nowait(orm_trades)
            return orm_orders, earliest_order_id, to

    async def fetch_my_okex_trades(self,
                                  exchange_class: ExchangeClass,
                                  symbol: str,
                                  since: int,
                                  params: dict
        ):
            trades = await exchange_class.exchange.fetch_my_trades(
                symbol, since=since, limit=None, params=params
            )
            if len(trades) == 0:
                return [], -1, -1
            # hacky: picking trade at 0 may skip some orders whose order id are the same
            # sql table can handle duplicated entry
            if len(trades) > 1:
                earliest_trade_id = trades[1]['order']
            else:
                earliest_trade_id = trades[0]['order']
            to = trades[0]['timestamp']
            orm_trades = []
            logger.info(f'fetching {exchange_class}')
            for trade in trades:
                ccxt_trade = CCXTTrade(**trade)
                account_name = exchange_class.account_name
                exchange_name = exchange_class.exchange_name
                orm_trade = ccxt_trade.to_orm_class(
                    exchange_name=exchange_name, account_name=account_name
                )
                orm_trades.append(orm_trade)
            # self._queue.put_nowait(orm_trades)
            return orm_trades, earliest_trade_id, to

    async def fetch_method_with_okex_pagination(
        self, method, exchange_class: ExchangeClass, bounty_info: BountyInfo
        ):
        # okex requires a different pagination method which is not unified under ccxt
        symbol = bounty_info.symbol
        since = bounty_info.since
        to = bounty_info.to
        earliest_id = None

        while to > since:
            try:
                params = {}
                if earliest_id:
                    params = {'after': earliest_id}
                if method == Methods.FETCH_OKEX_TRADES:
                    resp_list, earliest_id, to = await self.fetch_my_okex_trades(
                        exchange_class, symbol, since=since, params=params
                    )
                if method == Methods.FETCH_OKEX_ORDERS:
                    resp_list, earliest_id, to = await self.fetch_my_okex_orders(
                        exchange_class, symbol, since=since, params=params
                    )
                if earliest_id == -1:
                    break
                self._database.commit_task_list_to_sql(resp_list)
            except ccxt.ExchangeNotAvailable as exc:
                pass  # retry
            except ccxt.NetworkError as exc:
                logger.exception(f"{exc} retry in 60 sec", exc_info=False)
                await asyncio.sleep(60)
            except Exception as exc:
                logger.exception(
                    f"{exc} returning empty list for "
                    "{exchange_class.account_name} trades",
                    exc_info=True,
                )
                raise exc


    async def loop(
        self, exchange_class: ExchangeClass, bounty_info: BountyInfo, method: str
    ):
        try:
            if method == Methods.FETCH_OKEX_TRADES or method== Methods.FETCH_OKEX_ORDERS:
                await self.fetch_method_with_okex_pagination(method, exchange_class, bounty_info)
            if method == Methods.FETCH_BALANCES:
                await self.fetch_balance(exchange_class)
        except Exception as exc:
            logger.exception(exc, exc_info=True)

    async def fetch_all(self):
        tasks = []
        try:
            logger.info("initiated fetching")
            methods = [Methods.FETCH_OKEX_TRADES, Methods.FETCH_BALANCES]
            tasks = []
            exchange_names = []
            for exchange_class in self._exchange_classes:
                await exchange_class.exchange.load_markets()
                for bounty_info in self._bounty_infos:
                    for method in methods:
                        tasks.append(
                            self.loop(exchange_class, bounty_info, method))
                if exchange_class.exchange_name in exchange_names:
                    continue
                tasks.append(
                    self.fetch_tickers(exchange_class)
                )
                exchange_names.append(exchange_class.exchange_name)
            return await asyncio.gather(*tasks)

        except Exception as exc:
            logger.exception(exc, exc_info=True)

    async def fetch_tickers(self, exchange_class: ExchangeClass):
        tickers = await exchange_class.exchange.fetch_tickers()
        orm_tickers = []
        for ticker in tickers.values():
            ccxt_ticker = CCXTTicker(**ticker)
            orm_ticker = ccxt_ticker.to_orm_class(exchange_class.exchange_name)
            orm_tickers.append(orm_ticker)
        self._database.commit_task_list_to_sql(orm_tickers)

    async def start(self):
        while True:
            try:
                await self.fetch_all()
                await asyncio.sleep(60)
            except Exception as e:
                logger.exception(e, exc_info=True)
            except KeyboardInterrupt:
                await self.close_all()
                break

    async def close_all(self):
        for exchange_class in self._exchange_classes:
            logger.debug(f"close exchange {exchange_class}")
            await exchange_class.exchange.close()
