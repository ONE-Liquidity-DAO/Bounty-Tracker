'''create view for google governor to google sheet'''
import asyncio
import logging

import gspread
import pandas as pd
from src.core.gsheet import GSheet
from src.database.database import DataBase


logger = logging.getLogger(__name__)


class GoogleSyncTrade:
    '''sends full leaderboard for governor to view'''

    def __init__(self,
                 database: DataBase,
                 g_sheet: GSheet) -> None:
        self.database: DataBase = database
        self.g_sheet: GSheet = g_sheet
        self.governor_ss: gspread.Spreadsheet = g_sheet.governor_ss
        self.trades_ss: gspread.Spreadsheet = g_sheet.trades_ss
        self.update_interval = g_sheet.update_interval

    def set_sheets_by_campaign_id(self):
        '''group trade data by campaign_id and send to google sheet'''
        trades_df = self.get_trades_df()
        campaign_id_list = trades_df.campaign_id.unique()

        for campaign_id in campaign_id_list:
            id_df = trades_df[trades_df.campaign_id == campaign_id]
            try:
                id_ws = self.trades_ss.worksheet(str(campaign_id))
            except gspread.exceptions.WorksheetNotFound:
                id_ws = self.trades_ss.add_worksheet(str(campaign_id), 1, 1)
            self.g_sheet.set_sheet_with_df(id_ws, id_df)

    def get_trades_df(self) -> pd.DataFrame:
        '''gets trade data from database'''
        return self.database.query_table('trades')

    async def start(self):
        '''starts the application'''
        while True:
            try:
                logger.info('sleep for %s seconds', self.update_interval)
            except Exception as error:  #pylint: disable=broad-except
                logger.exception('%s: retry in 5min', error)
                await asyncio.sleep(300)
                continue
            await asyncio.sleep(self.update_interval)


async def test():
    '''test'''
    g_sheet = GSheet.create()
    database = DataBase()
    view = GoogleSyncTrade(database, g_sheet)
    view.set_sheets_by_campaign_id()


if __name__ == '__main__':
    asyncio.run(test())
