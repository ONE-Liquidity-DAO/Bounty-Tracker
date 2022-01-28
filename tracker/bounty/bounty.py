'''Create the bounty info'''
# pylint: disable=[too-many-instance-attributes, invalid-name]
import asyncio
import logging
from dataclasses import dataclass

import pandas as pd
from tracker.core.gsheet import GSheet

logger = logging.getLogger(__name__)


@dataclass
class BountyInfo:
    '''bounty schema information'''
    exchange_name: str
    market: str
    start_date: str
    end_date: str
    total_reward: float
    reward_currency: str
    campaign_id: int
    start_timestamp: int
    end_timestamp: int
    active: bool


def get_active_bounty_infos(sheet: GSheet) -> list[BountyInfo]:
    '''get active bounty infos from campaign setup'''
    bounty_infos = []
    ws = sheet.campaigns_ws
    df = sheet.get_worksheet_as_dataframe(ws)
    # replace nan with none to convert to dictionary
    logger.debug('bounty df: %s', df)
    df = df.replace({pd.NA: None})
    for _, row in df.iterrows():
        if not row['active']:
            continue
        row_dict = row.to_dict()
        bounty_info = BountyInfo(**row_dict)
        bounty_infos.append(bounty_info)
    return bounty_infos


def get_bounty_info_from_campaign_id(sheet: GSheet, campaign_id: int) -> BountyInfo:
    '''get bounty info from campaign id from campaign worksheet'''
    ws = sheet.campaigns_ws
    df = sheet.get_worksheet_as_dataframe(ws)
    # replace nan with none to convert to dictionary
    logger.debug('bounty df: %s', df)
    df = df.replace({pd.NA: None})
    # TODO: To vectorize
    for _, row in df.iterrows():
        if row['campaign_id'] == campaign_id:
            row_dict = row.to_dict()
            bounty_info = BountyInfo(**row_dict)
            return bounty_info
    raise KeyError('Value not found')


class Bounty:
    '''a class to update new bounty hourly'''

    def __init__(self, g_sheet: GSheet) -> None:
        self.g_sheet = g_sheet
        self.info: list[BountyInfo] = self.get_active_bounty_infos()

    def get_active_bounty_infos(self):
        '''return active bounty from google sheet'''
        return get_active_bounty_infos(self.g_sheet)

    async def start(self) -> None:
        '''start a loop to check for new bounty every 10 minutes'''
        while True:
            try:
                self.get_active_bounty_infos()
                await asyncio.sleep(600)
            except KeyboardInterrupt:
                break


def test() -> None:
    '''module test'''
    sheet = GSheet.create()
    bounty_infos = get_active_bounty_infos(sheet)
    print(bounty_infos)


if __name__ == '__main__':
    test()
