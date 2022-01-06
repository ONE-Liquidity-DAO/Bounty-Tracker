
from typing import Any
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.database.orm_data import Base, SQLTrade
from src.constants import DB_LOCATION, DB_TYPE
import logging
logger = logging.getLogger(__name__)


class DataBase:
    def __init__(self, db_type: str = DB_TYPE, db_location: str = DB_LOCATION):
        '''initialize database parameters'''
        self.engine = create_engine(
            f"{db_type}:///{db_location}", echo=False, future=True)
        self.Base = Base
        # this will create a table if it does not exists in the database
        # or load the table if it exists
        self.Base.metadata.create_all(self.engine)

    def commit_task_to_sql(self, task: Base) -> None:
        '''commit task to database'''
        with Session(self.engine) as session:
            session.merge(task)
            session.commit()
        logger.debug(f'commited: {task}')

    def commit_task_list_to_sql(self, task_list: list[Base]) -> None:
        '''commit list of task to database'''
        with Session(self.engine) as session:
            for task in task_list:
                session.merge(task)
            session.commit()
        logger.debug(f'commited: {task_list}')

    def replace_table_with_task(self, task: Base, table: str) -> None:
        '''delete table then create a table in place of it with the task'''
        with Session(self.engine) as session:
            session.query(table).delete()
            for order in task:
                session.merge(order)
            session.commit()
        logger.debug(f'commited: {task}')

    def process_task(self, task: Any) -> None:
        '''process task'''
        if type(task) == list:
            if len(task) == 0:
                return 'no task in list'
            if type(task[0]) == SQLTrade:
                self.commit_task_list_to_sql(task)
                return 'process SQLTrade'
            raise AttributeError(f'tasks type: {type(task[0])} not found')
        raise AttributeError(f'task type: {type(task)} not found')