'''Helper Class for database action'''
from dataclasses import dataclass
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.core.utils import load_yml
from src.database.orm_data import Base
import logging
logger = logging.getLogger(__name__)

DB_CONFIG_LOCATION = './config/database_config.yml'


@dataclass
class DBConfig:
    '''contains information required for setting up a database connection'''
    db_type: str
    db_location: str

    @classmethod
    def create(cls, config_file_location: str = DB_CONFIG_LOCATION) -> 'DBConfig':
        '''load config file and return a config dataclass'''
        config_dict = load_yml(config_file_location)
        return cls(**config_dict)


class DataBase:
    def __init__(self, db_config: DBConfig = DBConfig.create()):
        '''initialize database parameters'''
        db_type = db_config.db_type
        db_location = db_config.db_location
        self.engine = create_engine(
            f"{db_type}:///{db_location}", echo=False, future=True)
        self.Base = Base
        # this will create a table if it does not exists in the database
        # or load the table if it exists
        self.Base.metadata.create_all(self.engine)

    def commit_task_list_to_sql(self, task_list: list[Base]) -> None:
        '''commit list of task to database'''
        with Session(self.engine) as session:
            for task in task_list:
                session.merge(task)
            session.commit()
        logger.debug('commited: %s', task_list)

    def replace_table_with_task(self, task: Base, table: str) -> None:
        '''delete table then create a table in place of it with the task'''
        with Session(self.engine) as session:
            session.query(table).delete()
            for order in task:
                session.merge(order)
            session.commit()
        logger.debug('commited: %s', task)


if __name__ == "__main__":
    database = DataBase()