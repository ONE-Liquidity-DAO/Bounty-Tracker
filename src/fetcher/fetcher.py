from src.fetcher.ccxt_data import CCXTTrade
from src.fetcher.create_exchange_classes import ExchangeClass
from src.fetcher.create_bounty_info import BountyInfo
from src.database.database import DataBase
import ccxt.async_support as ccxt
import logging
import asyncio

logger = logging.getLogger(__name__)


class Fetcher:
    def __init__(
        self,
        exchange_classes: list[ExchangeClass],
        bounty_infos: list[BountyInfo],
        database: DataBase,
        #queue: asyncio.Queue,
    ) -> None:

        self._exchange_classes = exchange_classes
        self._bounty_infos = bounty_infos
        self._database = database
        #self._queue = queue

    async def fetch_eligible_trades(
        self, exchange_class: ExchangeClass, bounty_info: BountyInfo
    ):
        symbol = bounty_info.symbol
        since = 0 #bounty_info.since
        page = 1
        to = bounty_info.to
        earliest_trade_id = None
        while to > since:
            try:
                params = {}
                if  earliest_trade_id:
                    params = {'after': earliest_trade_id}
                trades = await exchange_class.exchange.fetch_my_trades(
                    symbol, since=since, limit=None, params=params
                )
                if len(trades) == 0:
                    break
                # hacky: picking trade at 0 may skip some orders whose order id are the same
                # sql table can handle duplicated  entry 
                if len(trades) >1:
                    earliest_trade_id = trades[1]['order']
                else:
                    earliest_trade_id = trades[0]['order']
                to = trades[0]['timestamp']
                print([trade['order'] for trade in trades])
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
                #self._queue.put_nowait(orm_trades)
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
            self._database.commit_task_list_to_sql(orm_trades)
    async def loop(
        self, exchange_class: ExchangeClass, bounty_info: BountyInfo, method: str
    ):
        try:
            if method == "fetch_eligible_trades":
                await self.fetch_eligible_trades(exchange_class, bounty_info)
                return
        except Exception as exc:
            logger.exception(exc, exc_info=True)

    async def fetch_all(self):
        tasks = []
        try:
            logger.info("initiated fetching")
            methods = ["fetch_eligible_trades"]
            tasks = []
            for exchange_class in self._exchange_classes:
                for bounty_info in self._bounty_infos:
                    for method in methods:
                        tasks.append(self.loop(exchange_class, bounty_info, method))
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
