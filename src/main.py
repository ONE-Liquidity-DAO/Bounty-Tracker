from src.fetcher.fetcher import Fetcher
from src.fetcher.create_exchange_classes import ExchangeClass, create_exchange_classes, get_account_infos
from src.fetcher.create_bounty_info import BountyInfo, create_bounty_info

from src.database.database import DataBase
import asyncio
from src.logger import setup_logging
from view.google.sheet import Sheet

from src.constants import (
    CREDENTIALS_LOCATION, BOUNTY_INFO_LOCATION, DB_TYPE, DB_LOCATION,
    LOG_LEVEL, FILE_LOG_LEVEL, LOG_FILENAME)
from utils import load_yml
import logging
logger = logging.getLogger(__name__)
async def main(
    db_location=DB_LOCATION,
    db_type=DB_TYPE,
    log_level=LOG_LEVEL,
    file_log_level=FILE_LOG_LEVEL,
    log_filename=LOG_FILENAME,
    credentials_location=CREDENTIALS_LOCATION,
    bounty_location=BOUNTY_INFO_LOCATION
):
    credentials = load_yml(credentials_location)
    account_infos = get_account_infos(credentials)
    exchange_classes = create_exchange_classes(account_infos)
    bounty_infos = create_bounty_info(bounty_location)
    setup_logging(
        log_level=log_level,
        file_log_level=file_log_level,
        log_filename=log_filename
    )
    database = DataBase(
        db_location=db_location,
        db_type=db_type
    )
    fetcher = Fetcher(
        exchange_classes=exchange_classes,
        bounty_infos=bounty_infos,
        database=database
    )
    sheet = Sheet(
        
    )
    while True:
        try:
            await fetcher.fetch_all()
            await sheet.loop()
            await asyncio.sleep(600)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.exception(e, exc_info=True)
            await asyncio.sleep(600)
    await fetcher.close_all()
if __name__ == "__main__":
    asyncio.run(main())

    