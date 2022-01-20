'''
Provides the base implementation that will fetch data from CCXT
and commits to database as a standalone service
'''

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Protocol

from ccxt.base.errors import RateLimitExceeded, ExchangeError, InvalidNonce, RequestTimeout, OnMaintenance
import pandas as pd
from sqlalchemy.orm.decl_api import DeclarativeMeta
from account.create_account_infos import AccountInfo

logger = logging.getLogger(__name__)


class DataBase(Protocol):
    '''function used in database for fetcher class'''

    def commit_task_list_to_sql(self, task: list[DeclarativeMeta]) -> None:
        '''commit list of tasks to database'''

    def query_sql(self, sql_query: str, **kwargs) -> pd.DataFrame:
        '''get query from database'''


class BaseFetcher(ABC):
    '''Defines the base methods required to fetch data from server using CCXT'''

    def __init__(
            self,
            account_infos: list[AccountInfo],
            database: DataBase) -> None:
        self._account_infos = account_infos
        self._database = database
        self.latest_trade_timestamp_df = self.get_latest_trade_timestamp()
        self._exchange_infos = self.get_exchange_infos()

    def commit_task_to_sql(self, task: DeclarativeMeta):
        '''commit tasks to database'''
        self._database.commit_task_to_sql(task)

    def commit_task_list_to_sql(self, task: list[DeclarativeMeta]):
        '''commit list of tasks to database'''
        self._database.commit_task_list_to_sql(task)

    def replace_table_with_task(self, task: DeclarativeMeta, table: str):
        '''replace database table with task'''
        self._database.replace_table_with_task(task, table)

    def query_sql(self, sql_query: str, **kwargs) -> pd.DataFrame:
        '''query sql from database'''
        return self._database.query_sql(sql_query, **kwargs)

    def get_latest_trade_timestamp(self) -> pd.DataFrame:
        '''update latest trade timestamp of all account'''
        sql_query = ('SELECT account_name, MAX(timestamp) '
                     'FROM "trades" GROUP BY account_name ')
        return self.query_sql(sql_query, index_col='account_name')

    def get_exchange_infos(self) -> list[AccountInfo]:
        '''to compile all unique exchange info for use in tickers'''
        exchanges = {}
        for account_info in self._account_infos:
            exchanges.update(
                {account_info.exchange_name: account_info})
        return exchanges.values()

    @abstractmethod
    async def fetch(self, account_info: AccountInfo) -> None:
        '''fetch method for ccxt defines here'''

    async def loop(self, account_info: AccountInfo) -> asyncio.Future:
        '''starts looping the fetch method for account info indefinitely'''
        while True:
            try:
                await self.fetch(account_info)
                await asyncio.sleep(account_info.update_interval)
            except OnMaintenance as error:
                logger.warning(
                    '%s server on maintainence, retrying after 10mins', error
                )
                await asyncio.sleep(600)
            except RateLimitExceeded as error:
                logger.warning(
                    '%s rate limit exceeded waiting additional 5min', error)
                await asyncio.sleep(300)
            except (ExchangeError, InvalidNonce, RequestTimeout) as error:
                logger.warning(
                    '%s waiting additional 1min', error)
                await asyncio.sleep(60)
            except KeyboardInterrupt as error:
                logger.info('closing fetcher due to user end %s', error)
                await self.close_all()
                raise error
            except Exception as error:
                logger.exception('Unexpected error encountered %s', error)
                await self.close_all()
                raise error
                

    async def start(self) -> None:
        '''start the loop for all account info'''
        tasks = []
        for account_info in self._account_infos:
            tasks.append(asyncio.create_task(self.loop(account_info)))
        await asyncio.gather(*tasks)

    async def close_all(self) -> None:
        '''close connections to all accountexchange'''
        for account_info in self._account_infos:
            logger.debug("close exchange %s", account_info.exchange_name)
            await account_info.exchange.close()
