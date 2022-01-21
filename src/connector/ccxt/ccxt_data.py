'''Defines the data received from CCXT'''
# pylint: disable=[invalid-name, too-many-instance-attributes, too-few-public-methods]
import logging
from dataclasses import dataclass, asdict
from typing import Optional, Protocol

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
                     user_info: UserInfo,
                     bounty_info: BountyInfo,
                     SQL_class: DeclarativeMeta) -> DeclarativeMeta:
        '''convert data class to orm class'''
        sql_dict = asdict(self)
        sql_dict.update(asdict(user_info))
        sql_dict.update(asdict(bounty_info))
        orm_dict = {}
        keys = SQL_class.__table__.columns.keys()
        for key in sql_dict:
            if key in keys:
                orm_dict[key] = sql_dict[key]
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
