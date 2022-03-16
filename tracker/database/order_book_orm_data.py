'''Contains trade object relational mapper'''
from sqlalchemy import BigInteger, Column, String, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

Base: DeclarativeMeta = declarative_base()


class SQLOrderBook(Base):
    '''sql orderbook schema'''
    __tablename__ = "order_book"
    timestamp = Column(BigInteger, primary_key=True, nullable=False)
    exchange_id = Column(String(100), primary_key=True, nullable=False)
    symbol = Column(String(100), primary_key=True, nullable=False)
    bids = Column(Text(4294000000))
    asks = Column(Text(4294000000))
