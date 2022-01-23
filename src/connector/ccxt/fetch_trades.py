'''
Fetch Trades from Exchange using CCXT
'''
import asyncio
import logging

from src.account.create_account_infos import AccountInfo
from src.bounty.bounty import BountyInfo
from src.connector.ccxt.base_fetcher import BaseFetcher
from src.connector.ccxt.ccxt_data import CCXTTrade
from src.connector.ccxt.pagination import pagination
from src.database.orm_data import SQLTrade

logger = logging.getLogger(__name__)

HOUR_MS = 60 * 60 * 1000
MAX_LOOKBACK_FOR_TRADES_IN_MS = 1 * HOUR_MS


class TradeFetcher(BaseFetcher):
    '''
    provides the implementation to fetch trades using CCXT
    '''
    async def fetch(self, account_info: AccountInfo, bounty_info: BountyInfo) -> None:
        '''update all latest trades based on api every interval'''
        exchange = account_info.exchange
        if exchange.has['fetchMyTrades']:
            trades = await self.fetch_my_trades_by_symbol(account_info, bounty_info)
        else:
            raise NotImplementedError()
        orm_list = []
        if not trades:
            return

        for trade in trades:
            ccxt_trade = CCXTTrade(**trade)
            orm = ccxt_trade.to_orm_class(
                account_info.user_info, bounty_info, SQLTrade)
            orm_list.append(orm)

        logger.debug('orm_trade_list \n %s', orm_list)
        logger.info('orm_trade_list len: %s, display_name: %s',
                    len(orm_list),
                    account_info.user_info.display_name)
        self.commit_task_list_to_sql(orm_list)


    async def fetch_my_trades_by_symbol(self,
                                        account_info: AccountInfo,
                                        bounty_info: BountyInfo) -> list[dict]:
        '''fetch trades by symbol and returns a list of trade json by ccxt'''
        limit = self._config.limits[account_info.user_info.exchange_name]
        method = self._config.pagination.get(account_info.user_info.exchange_name)
        display_name = account_info.user_info.display_name
        market = bounty_info.market
        start_time = bounty_info.start_timestamp
        end_time = bounty_info.end_timestamp
        func = account_info.exchange.fetch_my_trades

        results = await pagination(func=func,
                                   method=method,
                                   display_name=display_name,
                                   symbol=market,
                                   start_time=start_time,
                                   end_time=end_time,
                                   limit=limit)
        return results


async def test() -> None:
    '''test module code'''
    from src.core.gsheet import GSheet
    from src.core.logger import setup_logging
    from src.database.database import DataBase
    from src.account.account_validator import get_validated_account_infos
    from src.bounty.bounty import get_active_bounty_infos
    from src.connector.ccxt.get_config import CCXTConfig
    
    setup_logging()
    database = DataBase()
    gsheet = GSheet.create()
    account_infos = await get_validated_account_infos(gsheet)
    bounty_infos = get_active_bounty_infos(gsheet)
    config = CCXTConfig.create()
    fetcher = TradeFetcher(
        account_infos=account_infos,
        bounty_infos=bounty_infos,
        config=config,
        database=database,
    )
    await fetcher.start()

if __name__ == '__main__':
    asyncio.run(test())
