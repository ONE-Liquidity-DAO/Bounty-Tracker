'''Contains trade object relational mapper'''
from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

Base: DeclarativeMeta = declarative_base()
print(type(Base))


class SQLTrade(Base):
    '''sql trade schema'''
    # exchange_name + id + takerorMaker can be used to detect duplicated trade/wash trading
    # the other primary keys are identifier for governor
    __tablename__ = "Trades"
    exchange_name = Column(String, primary_key=True)
    id = Column(String, primary_key=True)
    takerOrMaker = Column(String, primary_key=True)
    # identify campaign id
    campaign_id: Column(Integer, primary_key=True)
    # to identify the trade belong to which account for governors
    # all of below may be removed primary key
    # but may result in random assignment of trade to account for duplicated trades
    # need to decide how should we deal with duplicated trade information
    # or we just remove the primary key and allow random assignment so
    # we do not need to check
    display_name = Column(String, primary_key=True)
    email_address = Column(String, primary_key=True)
    payout_address = Column(String, primary_key=True)
    api_key: str = Column(String, primary_key=True)

    # trade details
    datetime = Column(String)
    timestamp = Column(Integer)
    symbol = Column(String)
    side = Column(String)
    type = Column(String, nullable=True)
    price = Column(Float)
    amount = Column(Float)
    cost = Column(Float)
