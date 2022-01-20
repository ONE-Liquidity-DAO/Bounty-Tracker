'''gets and validate account info from google sheet'''
# pylint: disable=invalid-name
import logging
from dataclasses import dataclass
import ccxt.async_support as ccxt
from ccxt.base.exchange import Exchange
from src.account.get_user_info import UserInfo
logger = logging.getLogger(__name__)


@dataclass
class AccountInfo:
    user_info: UserInfo
    exchange: Exchange


def create_account_infos(user_infos: list[UserInfo]) -> list[AccountInfo]:
    '''create a list of exchange class from credentials'''
    account_infos = []
    for user_info in user_infos:
        try:
            exchange = getattr(ccxt, user_info.exchange_name)(
                {
                    "enableRateLimit": user_info.enableRateLimit,
                    "defaultType": user_info.type,
                    "apiKey": user_info.api_key,
                    "secret": user_info.secret,
                    "password": user_info.passphrase,
                }
            )
        except AttributeError as error:
            user_info.valid = False
            user_info.reason = 'AttributeError'
            logger.warning('%s: %s, skipping account',
                           user_info.account_name, error)
            continue

        account_info = AccountInfo(
            exchange=exchange,
            user_info=user_info
        )
        account_infos.append(account_info)
    return account_infos


