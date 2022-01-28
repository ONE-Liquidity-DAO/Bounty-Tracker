'''runs the fetch trading program'''
import asyncio

from tracker.account.account_validator import AccountValidator
from tracker.bounty.bounty import Bounty
from tracker.connector.ccxt.fetch_trades import TradeFetcher
from tracker.connector.ccxt.get_config import CCXTConfig
from tracker.core.gsheet import GSheet
from tracker.core.logger import setup_logging
from tracker.database.database import DataBase


async def main() -> None:
    '''starts the ccxt fetcher'''
    logger = setup_logging()
    logger.info('starting ccxt fetcher')

    database = DataBase()
    g_sheet = GSheet.create()

    account_validator = await AccountValidator.create(g_sheet)
    account_infos = account_validator.account_infos

    bounty = Bounty(g_sheet)
    bounty_infos = bounty.info

    config = CCXTConfig.create()
    fetcher = TradeFetcher(
        account_infos=account_infos,
        bounty_infos=bounty_infos,
        config=config,
        database=database,
    )
    await asyncio.gather(account_validator.start(),
                         bounty.start(),
                         fetcher.start())

if __name__ == '__main__':
    asyncio.run(main())
