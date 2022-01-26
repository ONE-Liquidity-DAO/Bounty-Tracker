'''gets and validate account info from google sheet'''

import logging
from dataclasses import dataclass, field
import pandas as pd
from tracker.core.gsheet import GSheet

logger = logging.getLogger(__name__)


@dataclass
class UserInfo:  # pylint: disable=[too-many-instance-attributes, invalid-name]
    '''User Info Google Sheet schema'''
    Timestamp: str
    email_address: str
    payout_address: str
    display_name: str
    exchange_name: str
    api_key: str
    secret: str = field(repr=False)
    uid: str = field(default=None, repr=False)
    passphrase: str = field(default=None, repr=False)
    valid: bool = None
    reason: str = None
    enable_rate_limit: bool = True
    type: str = 'spot'


def get_user_infos(sheet: GSheet) -> list[UserInfo]:
    '''get all account infos from api keys'''
    user_infos = []
    worksheet = sheet.user_info_ws
    dataframe = sheet.get_worksheet_as_dataframe(worksheet)
    # replace nan with none to convert to dictionary
    dataframe = dataframe.replace({pd.NA: None})
    for _, row in dataframe.iterrows():
        row_dict = row.to_dict()
        user_info = UserInfo(**row_dict)
        user_infos.append(user_info)
    return user_infos


def test() -> None:
    '''test'''
    sheet = GSheet.create()
    print(sheet)


if __name__ == '__main__':
    test()
