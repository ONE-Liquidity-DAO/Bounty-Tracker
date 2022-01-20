'''Defines the data received from CCXT'''
# pylint: disable=[invalid-name, too-many-instance-attributes]
import logging
from dataclasses import dataclass
from typing import Optional, Protocol

from sqlalchemy.orm.decl_api import DeclarativeMeta

logger = logging.getLogger(__name__)


@dataclass
class AccountInfo(Protocol):
    '''defines the attributes required for each account info'''
    exchange_name: str
    account_name: str


@dataclass
class CCXTBase:
    '''Base implementation for all CCXT Data Class'''

    def to_sql_dict(self) -> dict:
        '''convert data class to dict format'''
        self_dict = {
            k: v
            for k, v in self.__dict__.items()
            if "__" not in k
            and k not in ["info", "current_page", "endTime", "before", "after"]
        }
        return self_dict

    def to_orm_class(self,
                     account_info: AccountInfo,
                     SQL_class: DeclarativeMeta) -> DeclarativeMeta:
        '''convert data class to orm class'''
        sql_dict = self.to_sql_dict()
        sql_dict["exchange_name"] = account_info.exchange_name
        sql_dict["account_name"] = account_info.account_name
        
        return SQL_class(**sql_dict)


@dataclass
class CCXTOrder(CCXTBase):
    '''defines the order data attributes obtained from CCXT'''
    id: str
    clientOrderId: Optional[str]
    datetime: Optional[str]
    timestamp: Optional[int]
    status: str
    symbol: str
    type: str
    timeInForce: Optional[str]
    side: str
    price: float
    amount: float
    filled: float
    remaining: float
    cost: float
    postOnly: Optional[bool]
    info: dict  # to convert to string
    lastTradeTimestamp: Optional[int]
    average: Optional[float]
    stopPrice: Optional[float]
    trades: Optional[list]  # to convert to string
    fees: Optional[list]  # to convert to string
    fee: Optional[dict]  # to convert to string
    cancel_timestamp: Optional[int] = None
    current_page: Optional[int] = None  # non-unified params
    endTime: Optional[int] = None  # non-unified params
    before: Optional[str] = None  # non-unified params
    after: Optional[str] = None  # non-unified params

    def __post_init__(self) -> None:
        '''set timestamp to last trade timestamp if there is not timestamp'''
        if self.timestamp is None:
            self.timestamp = self.lastTradeTimestamp


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
    current_page: Optional[int] = None  # non-unified params
    endTime: Optional[int] = None  # non-unified params
    fee: Optional[dict] = None
    fees: Optional[dict] = None
    fee_currency: Optional[str] = None
    fee_cost: Optional[float] = None
    fee_rate: Optional[float] = None
    before: Optional[str] = None  # non-unified params
    after: Optional[str] = None  # non-unified params

    def __post_init__(self) -> None:
        '''expand fees into attributes'''
        if self.fee:
            self.fee_currency = self.fee.get("currency")
            self.fee_cost = self.fee.get("cost")
            self.fee_rate = self.fee.get("rate")
            return
        if len(self.fees) > 1:
            logger.warning("more than one fees")
            return


@dataclass
class CCXTBalance(CCXTBase):
    '''defines the individual balance data attributes obtained from CCXT'''
    timestamp: int
    datetime: str
    asset: str
    free: float
    used: float
    total: float


@dataclass
class CCXTTicker(CCXTBase):
    '''defines the ticker data attributes obtained from CCXT'''
    symbol:        str
    info:          dict
    timestamp:     int
    datetime:      str
    high:          float
    low:           float
    bid:           float
    bidVolume:     float
    ask:           float
    askVolume:     float
    vwap:          float
    open:          float
    close:         float
    last:          float
    previousClose: float
    change:        float
    percentage:    float
    average:       float
    baseVolume:    float
    quoteVolume:   float

    def to_orm_class(self,
                     exchange_name: str,
                     SQL_class: DeclarativeMeta) -> DeclarativeMeta:
        '''convert data class to SQLTicker'''
        sql_dict = self.to_sql_dict()
        sql_dict["exchange_name"] = exchange_name
        return SQL_class(**sql_dict)
