'''
Fetch Trades from Exchange using CCXT
'''
import asyncio
import logging
from ccxt.base.errors import ArgumentsRequired
from src.connector.ccxt.base_fetcher import BaseFetcher
from src.connector.ccxt.ccxt_data import CCXTTrade
from validation.create_account_infos import AccountInfo
from src.connector.ccxt.pagination import pagination
from src.database.orm_data import SQLTrade

logger = logging.getLogger(__name__)

HOUR_MS = 60 * 60 * 1000
MAX_LOOKBACK_FOR_TRADES_IN_MS = 1 * HOUR_MS


def convert_order_dict_to_trade_dict(order: dict) -> dict:
    trade_dict = {
        'id': order['id'],
        'order': order['id'],
        'datetime': order['datetime'],
        'timestamp': order['timestamp'],
        'symbol': order['symbol'],
        'type': order['type'],
        'side': order['side'],
        'takerOrMaker': 'unset',
        'price': order['price'],
        'amount': order['filled'],
        'cost': order['price'] * order['filled'],
        'info': order['info'],
        'fee': order.get('fee'),
        'fees': order.get('fees')
    }
    return trade_dict


class TradeFetcher(BaseFetcher):
    '''
    provides the implementation to fetch tradesusing CCXT
    '''

    def get_trade_timestamp(self, account_name: str) -> int:
        if account_name in self.latest_trade_timestamp_df.index:
            return self.latest_trade_timestamp_df.loc[account_name, 'max']
        return 0

    async def fetch(self, account_info: AccountInfo) -> None:
        '''update all latest trades based on api every interval'''
        exchange = account_info.exchange
        if exchange.has['fetchMyTrades']:
            trades = await self.fetch_trades(account_info)
        elif exchange.has['fetchClosedOrders']:
            trades = await self.fetch_closed_orders(account_info)
        else:
            raise NotImplementedError()
        orm_list = []
        if not trades:
            return

        for trade in trades:
            ccxt_trade = CCXTTrade(**trade)
            orm = ccxt_trade.to_orm_class(account_info, SQLTrade)
            orm_list.append(orm)

        logger.debug('orm_trade_list \n %s', orm_list)
        logger.info('orm_trade_list len: %s, account_name: %s',
                    len(orm_list),
                    account_info.account_name)
        self.commit_task_list_to_sql(orm_list)

    async def fetch_trades(self, account_info: AccountInfo) -> list[dict]:
        '''fetch trades if arguments required, fetch open orders by symbol'''
        trades = []
        try:
            trades = await account_info.exchange.fetch_my_trades(limit=account_info.limit)
            logger.info('%s fetch trades completed: %s',
                        account_info.account_name, len(trades))
            return trades
        except ArgumentsRequired:
            pass
        trades = await self.fetch_my_trades_by_symbol(account_info)
        return trades

    async def fetch_my_trades_by_symbol(self, account_info: AccountInfo) -> list[dict]:
        '''fetch trades by symbol'''
        all_results = []
        for market in account_info.markets:
            results = await account_info.exchange.fetch_my_trades(
                market, limit=account_info.limit)
            all_results += results
            logger.info('%s %s: fetch trades by symbol: %s',
                        account_info.account_name, market, len(results))
        logger.info('%s fetch trades by symbol completed: %s',
                    account_info.account_name, len(all_results))
        return all_results

    async def fetch_closed_orders(
            self, account_info: AccountInfo) -> list[dict]:
        '''
        all fetching are done asynchronously among account but synchronously within account markets
        This is done to prevent rate limits exceeded
        '''
        if not account_info.latest_trade_timestamp:
            account_info.latest_trade_timestamp = max(
                account_info.exchange.milliseconds()-MAX_LOOKBACK_FOR_TRADES_IN_MS,
                self.get_trade_timestamp(account_info.account_name))

        start_time = int(account_info.latest_trade_timestamp - 0.5*HOUR_MS)
        end_time = account_info.exchange.milliseconds()
        all_results = []
        for market in account_info.markets:
            func = account_info.exchange.fetch_closed_orders
            limit = account_info.limit
            results = await pagination(
                account_info, func, market, start_time, limit)
            all_results += results
            logger.info('%s %s: fetch closed order pagination: %s',
                        account_info.account_name, market, len(results))
        logger.info('%s fetch closed order completed: %s',
                    account_info.account_name, len(all_results))
        account_info.latest_trade_timestamp = end_time
        return [convert_order_dict_to_trade_dict(order)
                for order in all_results if order['filled'] > 0]


async def test():
    '''test module code'''
    from validation.create_account_infos import create_account_infos
    from src.database.database import DataBase
    from src.connector.ccxt.update_markets import update_markets
    from src.core.google import GSheet
    from src.core.logger import setup_logging
    logger = setup_logging()
    account_infos = create_account_infos()
    database = DataBase()
    gsheet = GSheet.create()
    await update_markets(gsheet, account_infos)
    fetcher = TradeFetcher(
        account_infos,
        database
    )
    await fetcher.start()

if __name__ == '__main__':
    asyncio.run(test())
