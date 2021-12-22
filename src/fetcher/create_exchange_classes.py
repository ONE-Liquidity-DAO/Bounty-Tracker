from dataclasses import dataclass
from src.utils import load_yml
from ccxt.base.exchange import Exchange
import logging
import ccxt.async_support as ccxt

from src.constants import CREDENTIALS_LOCATION


logger = logging.getLogger(__name__)

@dataclass
class AccountInfo:
    exchange_name: str
    account_name: str
    api_key: str
    secret: str
    type: str
    password:str = None
    enableRateLimit: bool = True


def get_account_infos(api_keys=load_yml(CREDENTIALS_LOCATION)) -> list[AccountInfo]:
    account_infos = []
    for account_name, details in api_keys.items():
        details.update({"account_name": account_name})
        account_info = AccountInfo(**details)
        account_infos.append(account_info)
    return account_infos


@dataclass
class ExchangeClass:
    exchange: Exchange
    account_name: str
    exchange_name: str


def create_exchange_classes(cred_location=CREDENTIALS_LOCATION) -> list[ExchangeClass]:
    account_infos = get_account_infos(api_keys=load_yml(cred_location))
    exchange_classes = []
    for account_info in account_infos:
        exchange = getattr(ccxt, account_info.exchange_name)(
            {
                "enableRateLimit": account_info.enableRateLimit,
                "defaultType": account_info.type,
                "apiKey": account_info.api_key,
                "secret": account_info.secret,
                "password": account_info.password,
                "asyncio_loop": None,
            }
        )
        exchange_class = ExchangeClass(
            exchange=exchange,
            account_name=account_info.account_name,
            exchange_name=account_info.exchange_name,
        )
        exchange_classes.append(exchange_class)
    return exchange_classes
