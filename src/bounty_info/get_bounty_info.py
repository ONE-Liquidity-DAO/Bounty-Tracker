'''Create the bounty info'''
# pylint: disable=[too-many-instance-attributes, invalid-name]
import logging
from dataclasses import dataclass

import pandas as pd
from src.core.gsheet import GSheet

logger = logging.getLogger(__name__)


@dataclass
class BountyInfo:
    '''bounty schema information'''
    exchange: str
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
    df = df.replace({pd.NA: None})
    for _, row in df.iterrows():
        if not row['active']:
            continue
        row_dict = row.to_dict()
        bounty_info = BountyInfo(**row_dict)
        bounty_infos.append(bounty_info)
    return bounty_infos

def test():
    sheet = GSheet.create()
    bounty_infos = get_active_bounty_infos(sheet)
    print(bounty_infos)

if __name__ == '__main__':
    test()