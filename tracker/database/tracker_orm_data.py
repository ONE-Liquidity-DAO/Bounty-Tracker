'''Contains trade object relational mapper'''
from sqlalchemy import BigInteger, Column, Float, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

Base: DeclarativeMeta = declarative_base()


class SQLTrade(Base):
    '''sql trade schema'''
    # exchange_name + id + takerorMaker can be used to detect duplicated trade/wash trading
    __tablename__ = "trades"
    exchange_name = Column(String, primary_key=True)
    id = Column(String, primary_key=True)
    takerOrMaker = Column(String, primary_key=True)
    # identify campaign id
    campaign_id = Column(Integer, primary_key=True)

    # to identify the trade belong to which account for governors
    display_name = Column(String)
    email_address = Column(String)
    payout_address = Column(String)
    api_key: str = Column(String)

    # trade details
    datetime = Column(String)
    timestamp = Column(BigInteger)
    symbol = Column(String)
    side = Column(String)
    price = Column(Float)
    amount = Column(Float)
    cost = Column(Float)
