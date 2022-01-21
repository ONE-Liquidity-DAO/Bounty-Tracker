
from src.connector.ccxt.fetch_trades import TradeFetcher
from src.core.gsheet import GSheet
from src.core.logger import setup_logging
from src.database.database import DataBase
from src.account.main import get_validated_account_infos
from src.bounty_info.get_bounty_info import get_active_bounty_infos
from src.connector.ccxt.get_config import CCXTConfig

async def main() -> None:
    '''starts the ccxt fetcher'''
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
    import asyncio
    asyncio.run(main())
