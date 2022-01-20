'''defines all pagination method used for CCXT'''
# pylint: disable=too-many-arguments
import asyncio
import logging
from enum import Enum, auto

from validation.create_account_infos import AccountInfo

from ccxt.base.errors import NetworkError

logger = logging.getLogger(__name__)


class PaginationMethod(Enum):
    '''defines the method available'''
    DATETIME = auto()
    ENDTIME = auto()


exchange_pagination_method = {
    "end_time": PaginationMethod.ENDTIME
}


async def retry_func(func,
                     symbol: str,
                     start_time: int,
                     limit: int,
                     params: dict = None,
                     retry: int = 3) -> list[dict]:
    '''retry function call up to retry times and raise error if result is not returned'''
    for i in range(retry):
        try:
            return await func(symbol, start_time, limit, params)
        except NetworkError as error:
            logger.warning('%s: network error encountered', error)
            await asyncio.sleep(60)
        except Exception as error:
            logger.warning(
                'Retry %s, Unknown Exception Encountered: %s', retry, error)
            if i == retry - 1:
                raise error
            await asyncio.sleep(60)


async def pagination(account_info: AccountInfo,
                     func,
                     symbol: str,
                     start_time: int,
                     limit: int,
                     params: dict = None) -> list[dict]:

    '''select pagination method by exchange'''
    method = exchange_pagination_method.get(
        account_info.pagination, PaginationMethod.DATETIME)
    if method == PaginationMethod.DATETIME:
        return await pagination_by_date_time(
            func, account_info, symbol, start_time, limit, params)
    if method == PaginationMethod.ENDTIME:
        return await pagination_by_end_time(
            func, account_info, symbol, start_time, limit, params)
    raise NotImplementedError()


async def pagination_by_date_time(func,
                                  account_info: AccountInfo,
                                  symbol: str,
                                  start_time: int,
                                  limit: int) -> list[dict]:
    '''pagination by date time'''
    end_time = account_info.exchange.milliseconds()
    all_results = []
    while start_time < end_time:
        results = await retry_func(func, symbol, start_time, limit)
        if len(results):
            start_time = results[len(results) - 1]['timestamp']
            all_results += results
            await asyncio.sleep(1)
            continue
        break


async def pagination_by_end_time(func,
                                 account_info: AccountInfo,
                                 symbol: str,
                                 start_time: int,
                                 limit: int,
                                 params: dict = None) -> list[dict]:
    '''pagination by end time method'''
    end_time = account_info.exchange.milliseconds()
    all_results = []
    while end_time > start_time:
        params = {'endTime': end_time}
        results = await retry_func(func, symbol, start_time, limit, params)
        if results:
            logger.info('pagination len: %s, account_name: %s, market:%s ',
                        len(results),
                        account_info.account_name,
                        symbol)
            if end_time == results[0]['timestamp']:
                break
            end_time = results[0]['timestamp']
            all_results += results
            await asyncio.sleep(1)
            continue
        break
    return all_results


async def test():
    '''test'''
    from validation.create_account_infos import create_account_infos
    account_infos = create_account_infos()
    account_info = account_infos[0]
    print(account_info)
    func = account_info.exchange.fetch_closed_orders
    start_time = account_info.exchange.milliseconds() - 86400000
    symbol = 'MANA/USDT'
    result = await pagination(account_info, func, symbol, start_time, limit=500)
    print(result)
    await account_info.exchange.close()

if __name__ == '__main__':
    asyncio.run(test())
