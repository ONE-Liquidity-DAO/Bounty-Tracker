'''defines all pagination method used for CCXT'''
# pylint: disable=too-many-arguments
import asyncio
import logging
from typing import Callable

from ccxt.base.errors import NetworkError, ExchangeNotAvailable
logger = logging.getLogger(__name__)


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
        except (ExchangeNotAvailable, NetworkError) as error:
            logger.warning('%s: network error encountered', error)
            await asyncio.sleep(60)
        except Exception as error:
            logger.exception(
                'Retry %s, Unknown Exception Encountered: %s', retry, error)
            if i == retry - 1:
                raise error
            await asyncio.sleep(60)


async def pagination_by_date_time(func: Callable,
                                  display_name: str,
                                  symbol: str,
                                  start_time: int,
                                  end_time: int,
                                  limit: int,
                                  params: dict = None) -> list[dict]:
    '''standard pagination method for ccxt'''
    all_results = []
    while start_time < end_time:
        results = await retry_func(func, symbol, start_time, limit, params)
        if results:
            logger.info('pagination len: %s, display_name: %s, market:%s ',
                        len(results),
                        display_name,
                        symbol)
            start_time = results[len(results) - 1]['timestamp']
            all_results += results
            await asyncio.sleep(1)
            continue
        break


async def pagination_by_end_time(func: Callable,
                                 display_name: str,
                                 symbol: str,
                                 start_time: int,
                                 end_time: int,
                                 limit: int,
                                 params: dict = None) -> list[dict]:
    '''pagination by end time method'''
    all_results = []
    while end_time > start_time:
        params = {'endTime': end_time}
        results = await retry_func(func, symbol, start_time, limit, params)
        if results:
            logger.info('pagination len: %s, display_name: %s, market:%s ',
                        len(results),
                        display_name,
                        symbol)
            if end_time == results[0]['timestamp']:
                break
            end_time = results[0]['timestamp']
            all_results += results
            await asyncio.sleep(1)
            continue
        break
    return all_results


async def pagination_by_earliest_id(func: Callable,
                                    display_name: str,
                                    symbol: str,
                                    start_time: int,
                                    end_time: int,
                                    limit: int,
                                    params: dict = None) -> list[dict]:
    '''pagination for okex exchange'''
    earliest_id = None
    all_results = []
    while end_time > start_time:
        params = {}
        if earliest_id:
            params = {'after': earliest_id}
        results = await retry_func(func, symbol, start_time, limit, params)
        # hacky: picking trade at 0 may skip some result whose order id are the same
        # sql table can handle duplicated entry
        if results:
            logger.info('pagination len: %s, display_name: %s, market:%s ',
                        len(results),
                        display_name,
                        symbol)
            all_results += results
            earliest_id = results[0]['order']
            if len(results) > 1:
                earliest_id = results[1]['order']
            end_time = results[0]['timestamp']
        else:
            break
        if earliest_id == -1:
            break

    return all_results

PAGINATION_METHODS = {
    "date_time": pagination_by_date_time,
    "end_time": pagination_by_end_time,
    "earliest_id": pagination_by_earliest_id
}


async def pagination(func: Callable,
                     method: str,
                     display_name: str,
                     symbol: str,
                     start_time: int,
                     end_time: int,
                     limit: int,
                     params: dict = None) -> list[dict]:
    pagination_method = PAGINATION_METHODS.get(
        method, pagination_by_date_time)
    results = await pagination_method(
        func, display_name, symbol, start_time,
        end_time, limit, params)
    return results