'''starts sync trades to google sheet'''
import asyncio
from src.core.gsheet import GSheet
from src.database.database import DataBase
from src.sync.sheet import GoogleSyncTrade
from src.core.logger import setup_logging


async def main():
    '''starts the sync to google sheet'''
    logger = setup_logging()
    logger.info('starting sync')
    g_sheet = GSheet.create()
    database = DataBase()
    view = GoogleSyncTrade(database, g_sheet)
    await view.start()

if __name__ == '__main__':
    asyncio.run(main())
