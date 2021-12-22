# define inputs
from dataclasses import dataclass
from typing import Optional
from src.database.orm_data import SQLTrade
import logging

logger = logging.getLogger(__name__)


# loading into this data class may be something like
@dataclass
class CCXTOpenOrder:
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
    current_page: Optional[int] = None # non-unified params
    endTime: Optional[int] = None# non-unified params
    before: Optional[int] = None# non-unified params
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = self.lastTradeTimestamp

    def to_sql_dict(self):
        self_dict = {
            k: v
            for k, v in self.__dict__.items()
            if "__" not in k and k not in ["info", "current_page", "endTime", "before"]
        }

        for key in ["trades", "fees", "fee"]:
            if not self_dict[key]:
                self_dict[key] = None
                continue
            self_dict[key] = str(self_dict[key])

        return self_dict

    def to_orm_class(self, account_name):
        sql_dict = self.to_sql_dict()
        sql_dict["account_name"] = account_name
        return SQLTrade(**sql_dict)


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
    current_page: Optional[int] = None# non-unified params
    endTime: Optional[int] = None# non-unified params
    fee: Optional[dict] = None
    fees: Optional[dict] = None
    fee_currency: Optional[str] = None
    fee_cost: Optional[float] = None
    fee_rate: Optional[float] = None
    before: Optional[str] = None# non-unified params
    after: Optional[str] = None# non-unified params
    
    def __post_init__(self):
        if self.fee:
            self.fee_currency = self.fee.get("currency")
            self.fee_cost = self.fee.get("cost")
            self.fee_rate = self.fee.get("rate")
            return
        if len(self.fees) > 1:
            logger.warning("more than one fees")
            return

    def to_sql_dict(self):
        # get all attributes except those containing __ and info
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

    def to_orm_class(self, account_name, exchange_name):
        sql_dict = self.to_sql_dict()
        sql_dict["account_name"] = account_name
        sql_dict["exchange_name"] = exchange_name
        return SQLTrade(**sql_dict)
