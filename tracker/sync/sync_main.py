'''starts sync trades to google sheet'''
import asyncio
from tracker.core.gsheet import GSheet
from tracker.database.database import DataBase
from tracker.sync.sheet import GoogleSyncTrade
from tracker.core.logger import setup_logging


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
