'''Helper Class for database action'''
import logging
from dataclasses import dataclass

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.orm import Session
from tracker.core.utils import load_yml
from tracker.database import tracker_orm_data, order_book_orm_data

logger = logging.getLogger(__name__)

DB_TRACKER_CREDENTIAL_LOCATION = './credentials/database_config.yml'
DB_PUBLIC_CREDENTIAL_LOCATION = './credentials/public_database_config.yml'


@dataclass
class DBConfig:
    '''contains information required for setting up a database connection'''
    db_type: str
    host: str
    user: str = None
    database: str | None = None
    port: str | None = None
    ssl: bool = False
    sslrootcert: str | None = None
    password: str | None = None
    #TODO: seperate orm_base for different database (tracker and public)
    base: str = 'tracker'

    @classmethod
    def create(cls, config_file_location: str = DB_TRACKER_CREDENTIAL_LOCATION) -> 'DBConfig':
        '''load config file and return a config dataclass'''
        config_dict = load_yml(config_file_location)
        return cls(**config_dict)

    def get_connector(self) -> str:
        '''get connector string'''
        if self.db_type == 'sqlite+pysqlite':
            return f"{self.db_type}:///{self.host}"
        if self.db_type == 'postgresql':
            return (f'{self.db_type}://{self.user}:{self.password}'
                    f'@{self.host}/{self.database}'
                    f'?sslmode=require&sslrootcert={self.sslrootcert}')
        if self.db_type == 'mysql+pymysql':
            return (f'{self.db_type}://{self.user}:{self.password}'
                    f'@{self.host}/{self.database}'
                    f'?ssl_ca={self.sslrootcert}')


class DataBase:
    '''helper interface for other script'''

    def __init__(self, db_config: DBConfig = DBConfig.create()):
        '''initialize database parameters'''
        self.connector = db_config.get_connector()
        self.engine = create_engine(
            self.connector, echo=False, future=True)
        # temporarily split
        if db_config.base == 'tracker':
            self.base = tracker_orm_data.Base
            # this will create a table if it does not exists in the database
            # or load the table if it exists
            self.base.metadata.create_all(self.engine)
        # temporarily split
        if db_config.base == 'public':
            self.base = order_book_orm_data.Base
            # this will create a table if it does not exists in the database
            # or load the table if it exists
            self.base.metadata.create_all(self.engine)

    def commit_task_list_to_sql(self, task_list: list[DeclarativeMeta]) -> None:
        '''commit list of task to database'''
        with Session(self.engine) as session:
            for task in task_list:
                session.merge(task)
            session.commit()
        logger.debug('commited: %s', task_list)

    def replace_table_with_task(self, task: DeclarativeMeta, table: str) -> None:
        '''delete table then create a table in place of it with the task'''
        with Session(self.engine) as session:
            session.query(table).delete()
            for order in task:
                session.merge(order)
            session.commit()
        logger.debug('commited: %s', task)

    def query_sql(self, sql_query: str, **kwargs) -> pd.DataFrame:
        '''
        get sql query and return a dataframe
        kwargs: additional parameters for pd.read_sql_query
        '''
        return pd.read_sql_query(sql_query, self.connector, **kwargs)

    def query_table(self, table_name: str, **kwargs) -> pd.DataFrame:
        '''
        get entire table from database
        kwargs: additional parameters for pd.read_sql_table
        '''
        return pd.read_sql_table(table_name, self.connector, **kwargs)


if __name__ == "__main__":
    database = DataBase(db_config=DBConfig.create(DB_PUBLIC_CREDENTIAL_LOCATION))
