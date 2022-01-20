'''gets and validate account info from google sheet'''
# pylint: disable=[invalid-name, too-many-instance-attributes]
import logging
from dataclasses import dataclass, field
from src.core.gsheet import GSheet

logger = logging.getLogger(__name__)


@dataclass
class UserInfo:
    '''User Info Google Sheet schema'''
    timestamp: str
    email_address: str
    payout_address: str
    account_name: str
    exchange_name: str
    api_key: str
    secret: str = field(repr=False)
    valid: bool
    reason: str = None
    passphrase: str = field(default=None, repr=False)
    enableRateLimit: bool = True
    type: str = 'spot'


def get_user_infos(sheet: GSheet) -> list[UserInfo]:
    '''get all account infos from api keys'''
    user_infos = []
    ws = sheet.user_info_ws
    df = sheet.get_worksheet_as_dataframe(ws)
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        user_info = UserInfo(**row_dict)
        user_infos.append(user_info)
    return user_infos