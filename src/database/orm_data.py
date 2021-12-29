from sqlalchemy.orm import declarative_base
from sqlalchemy import Table, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import registry

Base = declarative_base()

class SQLBalance(Base):
    __tablename__ = 'Balances'
    timestamp = Column(Integer, primary_key=True)
    account_name = Column(String, primary_key=True)
    exchange_name = Column(String, primary_key=True)
    datetime = Column(String)
    asset = Column(String, primary_key=True)
    total = Column(Float)
    free = Column(Float)
    used = Column(Float)
    def __repr__(self):
        return f"SQLBalance({self.__dict__})"

class SQLTrade(Base):
    __tablename__ = "Trades"
    exchange_name = Column(String, primary_key=True)
    account_name = Column(String, primary_key=True)
    id = Column(String, primary_key=True)
    datetime = Column(String)
    timestamp = Column(Integer)
    symbol = Column(String)
    side = Column(String)
    takerOrMaker = Column(String, nullable=True)
    price = Column(Float)
    amount = Column(Float)
    cost = Column(Float)
    fee = Column(String, nullable=True)
    fees = Column(String, nullable=True)
    type = Column(String, nullable=True)
    order = Column(String, nullable=True)
    fee_currency = Column(String, nullable=True)
    fee_cost = Column(Float, nullable=True)
    fee_rate = Column(Float, nullable=True)

class SQLOrder(Base):
    __tablename__ = 'Orders'
    exchange_name = Column(String, primary_key=True)
    account_name = Column(String, primary_key=True)
    id = Column(String, primary_key=True)
    account_name = Column(String, primary_key=True)
    clientOrderId = Column(String, nullable=True)
    datetime = Column(String)
    timestamp = Column(Integer)
    status = Column(String)
    symbol = Column(String)
    type = Column(String)
    timeInForce = Column(String, nullable=True)
    side = Column(String)
    price = Column(Float)
    amount = Column(Float)
    filled = Column(Float)
    remaining = Column(Float)
    cost = Column(Float)
    cancel_timestamp = Column(Integer)  # non-unified params
    postOnly = Column(Boolean, nullable=True)
    fee = Column(String, nullable=True)
    average = Column(Float, nullable=True)
    stopPrice = Column(Float, nullable=True)
    trades = Column(String, nullable=True)
    fees = Column(String, nullable=True)
    lastTradeTimestamp = Column(Integer, nullable=True)

    def __repr__(self):
        return f"SQLOpenOrder({self.__dict__})"
