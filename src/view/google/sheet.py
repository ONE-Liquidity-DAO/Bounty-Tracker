import pandas as pd
import asyncio
import gspread
import gspread_dataframe as gd
from src.utils import load_yml
from src.constants import (
    DB_TYPE, DB_LOCATION, SQL_FOLDER, GOOGLE_LOGIN_LOCATION,
    GOOGLE_WORKSHEET_NAME, GOOGLE_BALANCES_NAME, CONFIG_LOCATION,
    GOOGLE_TRADES_NAME)
import logging
from src.logger import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

class DBQuery:
    def __init__(self,
                 db_type=DB_TYPE,
                 db_location=DB_LOCATION,
                 sql_folder=SQL_FOLDER):
        self.connector = f"{db_type}:///{db_location}"
        self._sql_folder = sql_folder

    def load_sql(self, filename):
        file_location = self._sql_folder + filename + '.sql'
        with open(file_location) as f:
            query = f.read()
        return query

    # to maintain same table view across all interface
    def query_latest_balance(self) -> pd.DataFrame:
        sql_query = self.load_sql('query_latest_balance')
        return pd.read_sql_query(sql_query, self.connector)
    
    def query_my_trades(self) -> pd.DataFrame:
        sql_query = self.load_sql('query_trades')
        return pd.read_sql_query(sql_query, self.connector)

class Sheet:
    def __init__(self,
                 db_type=DB_TYPE,
                 db_location=DB_LOCATION,
                 sql_folder=SQL_FOLDER,
                 cred_location=GOOGLE_LOGIN_LOCATION,
                 sheet_name=GOOGLE_WORKSHEET_NAME,
                 balances_sheet_name=GOOGLE_BALANCES_NAME,
                 trades_sheet_name=GOOGLE_TRADES_NAME,
                 config=load_yml(CONFIG_LOCATION)['google']):

        logger.info(f'loading {sheet_name} in google')
        self._ws = self.get_worksheet(
            cred_location=cred_location, sheet_name=sheet_name)
        logger.info(f'loaded {sheet_name} in gooogle')
        self._query = DBQuery(
            db_type=db_type, db_location=db_location, sql_folder=sql_folder)
        self._balances_ws = self._ws.worksheet(balances_sheet_name)
        self._trades_ws = self._ws.worksheet(trades_sheet_name)
        self._config = config
        self._update_interval = config['update_interval']

    def get_worksheet(self, cred_location, sheet_name):
        gc = gspread.service_account(filename=cred_location)
        return gc.open(sheet_name)

    def read_sheet(self, ws):
        return ws.get_all_values()

    def set_sheet_with_df(self, ws, df, include_index=False):
        ws.clear()
        gd.set_with_dataframe(ws, df, include_index=include_index)

    def sync_balances(self):
        logger.info('sync balance')
        df = self._query.query_latest_balance()
        self.set_sheet_with_df(self._balances_ws, df)
        logger.info('sync balance done')

    def sync_trades(self):
        logger.info('sync trades')
        df = self._query.query_my_trades()
        self.set_sheet_with_df(self._trades_ws, df)
        logger.info('sync trades done')

    async def loop(self):
        while True:
            try:
                self.sync_balances()
                self.sync_trades()
                logger.info(f'sleep for {self._config["update_interval"]} seconds')
                
            except Exception as e:
                logger.exception(f'{e} retry in 5min')
                await asyncio.sleep(300)
                continue
            break
            await asyncio.sleep(self._update_interval)

    def start(self):
        asyncio.run(self.loop())


if __name__ == '__main__':
    sheet = Sheet()
    sheet.start()