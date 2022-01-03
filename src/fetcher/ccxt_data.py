# define inputs
from dataclasses import dataclass
from typing import Optional
from src.database.orm_data import SQLBalance, SQLOrder, SQLTicker, SQLTrade
import logging

logger = logging.getLogger(__name__)


# TODO: Possible refactor class

@dataclass
class CCXTOrder:
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
    cancel_timestamp: int
    lastTradeTimestamp: Optional[int]
    average: Optional[float]
    stopPrice: Optional[float]
    trades: Optional[list]  # to convert to string
    fees: Optional[list]  # to convert to string
    fee: Optional[dict]  # to convert to string
    current_page: Optional[int] = None  # non-unified params
    endTime: Optional[int] = None  # non-unified params
    before: Optional[str] = None  # non-unified params
    after: Optional[str] = None  # non-unified params

    def __post_init__(self) -> None:
        '''set timestamp to last trade timestamp if there is not timestamp'''
        if self.timestamp is None:
            self.timestamp = self.lastTradeTimestamp

    def to_sql_dict(self) -> dict:
        '''convert data class to dict format'''
        self_dict = {
            k: v
            for k, v in self.__dict__.items()
            if "__" not in k
            and k not in ["info", "current_page", "endTime", "before", "after"]
        }

        for key in ["trades", "fees", "fee"]:
            if not self_dict[key]:
                self_dict[key] = None
                continue
            self_dict[key] = str(self_dict[key])

        return self_dict

    def to_orm_class(self, exchange_name, account_name) -> SQLOrder:
        '''convert data class to orm class'''
        sql_dict = self.to_sql_dict()
        sql_dict["exchange_name"] = exchange_name
        sql_dict["account_name"] = account_name
        return SQLOrder(**sql_dict)


@dataclass
class CCXTTrade:
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

    def to_sql_dict(self) -> dict:
        '''get all attributes except those containing __ and info into dict'''
        self_dict = {
            k: v
            for k, v in self.__dict__.items()
            if "__" not in k and k not in ["info", "current_page", "endTime", "before", "after"]
        }
        # convert list and dict to str
        for key in ["fee", "fees"]:
            if not self_dict[key]:
                self_dict[key] = None
                continue
            self_dict[key] = str(self_dict[key])
        return self_dict

    def to_orm_class(self, account_name, exchange_name) -> SQLTrade:
        '''convert data class to SQL Trade'''
        sql_dict = self.to_sql_dict()
        sql_dict["account_name"] = account_name
        sql_dict["exchange_name"] = exchange_name
        return SQLTrade(**sql_dict)


@dataclass
class CCXTBalance:
    timestamp: int
    datetime: str
    asset: str
    free: dict
    used: dict
    total: dict

    def to_sql_dict(self) -> dict:
        '''get all attributes except those containing __ and unused info into dict'''
        self_dict = {
            k: v
            for k, v in self.__dict__.items()
            if "__" not in k
            and k not in ["info", "current_page", "endTime", "before", "after"]
        }
        return self_dict

    def to_orm_class(self, exchange_name, account_name) -> SQLBalance:
        '''convert data class to SQLBalance'''
        sql_dict = self.to_sql_dict()
        sql_dict["exchange_name"] = exchange_name
        sql_dict["account_name"] = account_name
        return SQLBalance(**sql_dict)


@dataclass
class CCXTBalances:
    info: dict
    timestamp: int
    datetime: str
    free: dict
    used: dict
    total: dict

    def __init__(self, data) -> None:
        '''convert raw balance data from ccxt into dataclass'''
        self.info = data.get('info')
        self.timestamp = data.get('timestamp')
        self.datetime = data.get('datetime')
        self.free = data.get('free')
        self.used = data.get('used')
        self.total = data.get('total')

    def get_balance_row(self) -> list[CCXTBalance]:
        '''convert each asset into individual CCXT Balance'''
        ccxt_balances = []
        for asset in self.total:
            ccxt_balance = CCXTBalance(
                timestamp=self.timestamp,
                datetime=self.datetime,
                asset=asset,
                free=self.free.get(asset, 0),
                used=self.used.get(asset, 0),
                total=self.total.get(asset, 0)
            )
            ccxt_balances.append(ccxt_balance)
        return ccxt_balances

    def get_balance_orm_list(self, exchange_name, account_name) -> list[SQLBalance]:
        '''convert all CCXTBalance to SQLBalance'''
        ccxt_balances = self.get_balance_row()
        return [balance.to_orm_class(exchange_name, account_name)
                for balance in ccxt_balances]

@dataclass
class CCXTTicker:
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

    def to_sql_dict(self) -> dict:
        '''get all attributes except those containing __ and unused info into dict'''
        self_dict = {
            k: v
            for k, v in self.__dict__.items()
            if "__" not in k
            and k not in ["info", "current_page", "endTime", "before", "after"]
        }
        return self_dict

    def to_orm_class(self, exchange_name):
        '''convert data class to SQLTicker'''
        sql_dict = self.to_sql_dict()
        sql_dict["exchange_name"] = exchange_name
        return SQLTicker(**sql_dict)