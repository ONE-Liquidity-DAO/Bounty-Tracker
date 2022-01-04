from src.fetcher.fetcher import Fetcher
from src.fetcher.create_exchange_classes  import ExchangeClass, create_exchange_classes, get_account_infos
from src.fetcher.create_bounty_info import BountyInfo, create_bounty_info

from src.database.database import DataBase
import asyncio
from src.logger import setup_logging
from src.constants import (
    CREDENTIALS_LOCATION, BOUNTY_INFO_LOCATION, DB_TYPE, DB_LOCATION,
    LOG_LEVEL, FILE_LOG_LEVEL, LOG_FILENAME)


class Tracker:
    def __init__(self,
                 exchange_classes: list[ExchangeClass],
                 bounty_infos: list[BountyInfo],
                 db_location=DB_LOCATION,
                 db_type=DB_TYPE,
                 log_level=LOG_LEVEL,
                 file_log_level=FILE_LOG_LEVEL,
                 log_filename=LOG_FILENAME):

        self.logger = setup_logging(
            log_level=log_level,
            file_log_level=file_log_level,
            log_filename=log_filename
        )
        self._queue = asyncio.Queue()
        self._database = DataBase(
            db_location=db_location,
            db_type=db_type
        )
        self._fetcher = Fetcher(
            exchange_classes=exchange_classes,
            bounty_infos=bounty_infos,
            database=self._database
        )


    async def start(self):
        
        #await asyncio.create_task(self._database.start())
        #await asyncio.create_task(self._fetcher.start())
        await self._fetcher.fetch_all()
        await self._fetcher.close_all()


if __name__ == "__main__":
    account_infos = get_account_infos()
    exchange_classes = create_exchange_classes(account_infos)
    bounty_infos = create_bounty_info(config_location=BOUNTY_INFO_LOCATION)
    tracker = Tracker(exchange_classes, bounty_infos)
    asyncio.run(tracker.start())
