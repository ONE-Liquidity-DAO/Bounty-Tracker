'''Create the bounty info'''
# pylint: disable=[too-many-instance-attributes, invalid-name]
import asyncio
from datetime import datetime
import logging
from dataclasses import dataclass

import pandas as pd
from src.core.gsheet import GSheet
from src.core.utils import get_utc_timestamp

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
    logger.info('active bounty: %s', df)
    df = df.replace({pd.NA: None})
    for _, row in df.iterrows():
        if not row['active']:
            continue
        row_dict = row.to_dict()
        bounty_info = BountyInfo(**row_dict)
        bounty_infos.append(bounty_info)
    return bounty_infos


class Bounty:
    '''a class to update new bounty hourly'''

    def __init__(self, g_sheet: GSheet) -> None:
        self.g_sheet = g_sheet
        self.info: list[BountyInfo] = self.get_active_bounty_infos()

    def get_active_bounty_infos(self):
        '''return active bounty from google sheet'''
        return get_active_bounty_infos(self.g_sheet)

    async def start(self) -> None:
        '''start a loop to check for new bounty hourly'''
        while True:
            try:
                self.get_active_bounty_infos()
                await asyncio.sleep(3600)
            except KeyboardInterrupt:
                break


def test() -> None:
    '''module test'''
    sheet = GSheet.create()
    bounty_infos = get_active_bounty_infos(sheet)


if __name__ == '__main__':
    test()
