'''Defines the data received from CCXT'''
# pylint: disable=[invalid-name, too-many-instance-attributes, too-few-public-methods]
import logging
import json
from dataclasses import dataclass, asdict
import time
from typing import Optional, Protocol, Tuple

from sqlalchemy.orm.decl_api import DeclarativeMeta

logger = logging.getLogger(__name__)


@dataclass
class UserInfo(Protocol):
    '''defines the attributes required for each account info'''
    exchange_name: str
    email_address: str  # for easy to find communication
    payout_address: str  # for easy to find payout address
    display_name: str  # to display on leaderboard
    api_key: str    # second identifier as we cannot ensure unique in display name


class BountyInfo(Protocol):
    '''defines the attribute required from bounty info'''
    campaign_id: int


@dataclass
class CCXTBase:
    '''Base implementation for all CCXT Data Class'''

    def to_orm_class(self,
                     SQL_class: DeclarativeMeta,
                     user_info: UserInfo = None,
                     bounty_info: BountyInfo = None,
                     serialize_list: bool = False,
                     ) -> DeclarativeMeta:
        '''convert data class to orm class'''
        sql_dict = {}
        if user_info:
            sql_dict.update(asdict(user_info))
        if bounty_info:
            sql_dict.update(asdict(bounty_info))
        sql_dict.update(asdict(self))
        orm_dict = {}
        keys = SQL_class.__table__.columns.keys()
        for key, value in sql_dict.items():
            if key in keys:
                if serialize_list and isinstance(value, list):
                    orm_dict[key] = json.dumps(value)
                    continue
                orm_dict[key] = value
        return SQL_class(**orm_dict)


@dataclass
class CCXTTrade(CCXTBase):
    '''defines the trade data attributes obtained from CCXT'''
    id: str
    order: Optional[str]
    datetime: str
    timestamp: int
    symbol: str
    type: Optional[str]
    side: str
    takerOrMaker: str
    price: float
    amount: float
    cost: float
    info: dict
    fee: Optional[dict] = None
    fees: Optional[dict] = None
    before: Optional[str] = None  # non-unified params
    after: Optional[str] = None  # non-unified params
    current_page: Optional[int] = None  # non-unified params
    endTime: Optional[int] = None  # non-unified params


@dataclass
class CCXTOrderBook(CCXTBase):
    '''defines the order book data obtained from CCXT'''
    symbol: str
    bids: list[Tuple[float, float]]
    asks: list[Tuple[float, float]]
    timestamp: int
    datetime: str = None
    nonce: int = None
    exchange_id: str = None  # parameter not included

    @classmethod
    def create_with_exchange_id(cls, order_book: dict, exchange_id: str) -> "CCXTOrderBook":
        '''helper function to include exchange id'''
        if order_book.get('timestamp') is None:
            order_book['timestamp'] = int(time.time() * 1000)
        self = cls(**order_book)
        self.exchange_id = exchange_id
        return self
