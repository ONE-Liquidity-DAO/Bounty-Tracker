'''runs the fetch trading program'''
from src.connector.ccxt.fetch_trades import TradeFetcher
from src.core.gsheet import GSheet
from src.core.logger import setup_logging
from src.database.database import DataBase
from src.account.account_validator import AccountValidator
from src.bounty.bounty import Bounty
from src.connector.ccxt.get_config import CCXTConfig


async def main() -> None:
    '''starts the ccxt fetcher'''
    setup_logging()
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
    import asyncio
    asyncio.run(main())
