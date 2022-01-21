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
from src.account.create_account_infos import AccountInfo
from src.bounty_info.get_bounty_info import BountyInfo
from src.connector.ccxt.get_config import CCXTConfig
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
            bounty_infos: list[BountyInfo],
            config: CCXTConfig,
            database: DataBase) -> None:
        self._account_infos = account_infos
        self._bounty_infos = bounty_infos
        self._config = config
        self._database = database

    def commit_task_list_to_sql(self, task: list[DeclarativeMeta]):
        '''commit list of tasks to database'''
        self._database.commit_task_list_to_sql(task)

    def query_sql(self, sql_query: str, **kwargs) -> pd.DataFrame:
        '''query sql from database'''
        return self._database.query_sql(sql_query, **kwargs)

    @abstractmethod
    async def fetch(self, account_info: AccountInfo, bounty_info: BountyInfo) -> None:
        '''fetch method for ccxt defines here'''


    async def loop(self, account_info: AccountInfo, bounty_info: BountyInfo) -> asyncio.Future:
        '''starts looping the fetch method for account info indefinitely'''
        while True:
            try:
                await self.fetch(account_info, bounty_info)
                await asyncio.sleep(self._config.update_interval)
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
            # except Exception as error:
            #     logger.exception('Unexpected error encountered %s', error)
            #     await self.close_all()
            #     raise error

    async def start(self) -> None:
        '''start the loop for all account info'''
        tasks = []
        for account_info in self._account_infos:
            for bounty_info in self._bounty_infos:
                tasks.append(asyncio.create_task(self.loop(account_info, bounty_info)))
        await asyncio.gather(*tasks)

    async def close_all(self) -> None:
        '''close connections to all accountexchange'''
        for account_info in self._account_infos:
            logger.debug("close exchange %s", account_info.user_info.exchange_name)
            await account_info.exchange.close()
