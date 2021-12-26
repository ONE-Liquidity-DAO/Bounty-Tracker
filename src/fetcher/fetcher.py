from src.fetcher.ccxt_data import CCXTOrder, CCXTTrade
from src.fetcher.create_exchange_classes import ExchangeClass
from src.fetcher.create_bounty_info import BountyInfo
from src.database.database import DataBase
import ccxt.async_support as ccxt
import logging
import asyncio
import pandas as pd

logger = logging.getLogger(__name__)


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

 
    async def fetch_my_okex_orders(
        self, exchange_class: ExchangeClass, bounty_info: BountyInfo
    ):
        '''fetch orders which have closed'''  
        symbol = bounty_info.symbol
        since = bounty_info.since
        to = bounty_info.to
        earliest_order_id = None
        # TODO: To only collect after latest order id in database
        
        latest_order_id = None
        while to > since:
            try:
                params = {}
                if earliest_order_id:
                    params = {'after': earliest_order_id}
                orders = await exchange_class.exchange.fetch_closed_orders(
                    symbol, since=since, limit=None, params=params
                )
                if len(orders) == 0:
                    break
                from pprint import pprint
                pprint(orders[0])
                # hacky: picking trade at 0 may skip some orders whose order id are the same
                # sql table can handle duplicated entry
                if len(orders) > 1:
                    earliest_trade_id = orders[1]['order']
                else:
                    earliest_trade_id = orders[0]['order']
                to = orders[0]['timestamp']
                print([order['order'] for order in orders])
                orm_orders = []
                logger.info(f'fetching {exchange_class}')
                for order in orders:
                    ccxt_order = CCXTOrder(**order)
                    account_name = exchange_class.account_name
                    exchange_name = exchange_class.exchange_name
                    orm_order = ccxt_order.to_orm_class(
                        exchange_name=exchange_name, account_name=account_name
                    )
                    orm_order.append(orm_order)
                # self._queue.put_nowait(orm_trades)
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
            self._database.commit_task_list_to_sql(orm_orders)

    async def okex_pagination(
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
                if method == 'fetch_okex_trades':
                    resp_list, earliest_id, to = await self.fetch_my_okex_trade(
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

    async def fetch_my_okex_trade(self,
                                  exchange_class: ExchangeClass,
                                  symbol: str,
                                  since: int,
                                  params: dict
    ):
            trades = await exchange_class.exchange.fetch_my_trades(
                symbol, since=since, limit=None, params=params
            )
            print('test trades', trades)
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

    async def loop(
        self, exchange_class: ExchangeClass, bounty_info: BountyInfo, method: str
    ):
        try:
            if 'okex' in method:
                await self.okex_pagination(method, exchange_class, bounty_info)
        except Exception as exc:
            logger.exception(exc, exc_info=True)

    async def fetch_all(self):
        tasks = []
        try:
            logger.info("initiated fetching")
            methods = ["fetch_okex_trades"]
            tasks = []
            for exchange_class in self._exchange_classes:
                await exchange_class.exchange.load_markets()
                for bounty_info in self._bounty_infos:
                    for method in methods:
                        tasks.append(
                            self.loop(exchange_class, bounty_info, method))
            return await asyncio.gather(*tasks)

        except Exception as exc:
            logger.exception(exc, exc_info=True)

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
