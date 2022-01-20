'''Initialize google connection'''
# pylint: disable=[invalid-name, too-many-instance-attributes]

from dataclasses import dataclass
import gspread
import pandas as pd
import gspread_dataframe as gd
import logging

from src.core.utils import load_yml
logger = logging.getLogger(__name__)

CONFIG_LOCATION = './config/google_config.yml'


@dataclass
class GoogleConfig:
    '''google config schema'''
    client: gspread.Client
    update_interval: int
    user_spreadsheet_name: str
    user_info_name: str
    governor_spreadsheet_name: str
    campaigns_name: str
    

    @classmethod
    def create(cls, config_file_location: str = CONFIG_LOCATION) -> 'GoogleConfig':
        '''create a google config'''
        config_dict = load_yml(config_file_location)
        gc = gspread.service_account(filename=config_dict['credentials_location'])
        config_dict['client'] = gc
        config_dict.pop('credentials_location')
        return cls(**config_dict)


class GSheet:
    '''Provides the interface to google sheet'''
    def __init__(self, config: GoogleConfig) -> None:
        '''initialize the google sheet connections to the standard worksheet used'''
        self.client = config.client
        self.update_interval = config.update_interval
        self.user_ss = self.get_spreadsheet(config.user_spreadsheet_name)        
        self.user_info_ws = self.user_ss.worksheet(config.user_info_name)
        self.governor_ss = self.get_spreadsheet(config.governor_spreadsheet_name)
        self.campaigns_ws = self.governor_ss.worksheet(config.campaigns_name)

    @classmethod
    def create(cls, config_file_location: str = CONFIG_LOCATION) -> 'GSheet':
        '''provides a default method of creating the google sheet class'''
        config = GoogleConfig.create(config_file_location)
        return cls(config)

    @staticmethod
    def get_worksheet_as_dataframe(ws: gspread.Worksheet) -> pd.DataFrame:
        '''get all values in worksheet and returns a pandas dataframe'''
        df = gd.get_as_dataframe(ws)
        df = df.dropna(axis=0, how='all')
        df = df.dropna(axis=1, how='all')
        return df

    @staticmethod
    def set_sheet_with_df(ws: gspread.Worksheet,
                          df: pd.DataFrame,
                          include_index: bool=False) -> None:
        '''replace worksheet data with specified dataframe'''
        ws.clear()
        gd.set_with_dataframe(ws, df, include_index=include_index)

    def get_spreadsheet(self, sheet_name: str) -> gspread.Spreadsheet:
        '''connect to the service account and return the main worksheet'''
        return self.client.open(sheet_name)
    