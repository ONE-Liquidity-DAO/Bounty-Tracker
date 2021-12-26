# define inputs
from dataclasses import dataclass
from typing import Optional
from src.database.orm_data import SQLOrder, SQLTrade
import logging

logger = logging.getLogger(__name__)


# loading into this data class may be something like
'''
{
    'id':                '12345-67890:09876/54321', // string
    'clientOrderId':     'abcdef-ghijklmnop-qrstuvwxyz', // a user-defined clientOrderId, if any
    'datetime':          '2017-08-17 12:42:48.000', // ISO8601 datetime of 'timestamp' with milliseconds
    'timestamp':          1502962946216, // order placing/opening Unix timestamp in milliseconds
    'lastTradeTimestamp': 1502962956216, // Unix timestamp of the most recent trade on this order
    'status':      'open',        // 'open', 'closed', 'canceled', 'expired'
    'symbol':      'ETH/BTC',     // symbol
    'type':        'limit',       // 'market', 'limit'
    'timeInForce': 'GTC',         // 'GTC', 'IOC', 'FOK', 'PO'
    'side':        'buy',         // 'buy', 'sell'
    'price':        0.06917684,   // float price in quote currency (may be empty for market orders)
    'average':      0.06917684,   // float average filling price
    'amount':       1.5,          // ordered amount of base currency
    'filled':       1.1,          // filled amount of base currency
    'remaining':    0.4,          // remaining amount to fill
    'cost':         0.076094524,  // 'filled' * 'price' (filling price used where available)
    'trades':     [ ... ],        // a list of order trades/executions
    'fee': {                      // fee info, if available
        'currency': 'BTC',        // which currency the fee is (usually quote)
        'cost': 0.0009,           // the fee amount in that currency
        'rate': 0.002,            // the fee rate (if available)
    },
    'info': { ... },              // the original unparsed order structure as is
}
'''
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

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = self.lastTradeTimestamp

    def to_sql_dict(self):
        self_dict = {
            k: v
            for k, v in self.__dict__.items()
            if "__" not in k 
            and k not in ["info", "current_page", "endTime", "before"]
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
