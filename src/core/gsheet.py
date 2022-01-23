'''Initialize google connection'''
import logging
from dataclasses import dataclass

import gspread
import gspread_dataframe as gd
import pandas as pd
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
    trades_spreadsheet_name: str

    @classmethod
    def create(cls, config_file_location: str = CONFIG_LOCATION) -> 'GoogleConfig':
        '''create a google config'''
        config_dict = load_yml(config_file_location)
        gsc = gspread.service_account(
            filename=config_dict['credentials_location'])
        config_dict['client'] = gsc
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
        self.governor_ss = self.get_spreadsheet(
            config.governor_spreadsheet_name)
        self.campaigns_ws = self.governor_ss.worksheet(config.campaigns_name)
        self.trades_ss = self.get_spreadsheet(config.trades_spreadsheet_name)

    @classmethod
    def create(cls, config_file_location: str = CONFIG_LOCATION) -> 'GSheet':
        '''provides a default method of creating the google sheet class'''
        config = GoogleConfig.create(config_file_location)
        return cls(config)

    @staticmethod
    def get_worksheet_as_dataframe(worksheet: gspread.Worksheet,
                                   evaluate_formulas: bool = True,
                                   **kwargs) -> pd.DataFrame:
        '''get all values in worksheet and returns a pandas dataframe'''
        dataframe = gd.get_as_dataframe(
            worksheet, evaluate_formulas=evaluate_formulas, **kwargs)
        dataframe = dataframe.dropna(axis=0, how='all')
        dataframe = dataframe.dropna(axis=1, how='all')
        return dataframe

    @staticmethod
    def set_sheet_with_df(worksheet: gspread.Worksheet,
                          dataframe: pd.DataFrame,
                          include_index: bool = False) -> None:
        '''replace worksheet data with specified dataframe'''
        worksheet.clear()
        gd.set_with_dataframe(worksheet, dataframe,
                              include_index=include_index)

    def get_spreadsheet(self, sheet_name: str) -> gspread.Spreadsheet:
        '''connect to the service account and return the main worksheet'''
        try:
            return self.client.open(sheet_name)
        except gspread.exceptions.SpreadsheetNotFound as error:
            logger.exception('%s: Please check if you have created the spreadsheet %s'
                             ' and shared the spread sheet with the service account. ',
                             error, sheet_name)
