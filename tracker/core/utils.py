'''utility functions'''
from datetime import datetime, timezone
import yaml


def load_yml(file_location: str) -> dict:
    '''opens a yml file and returns a dictionary'''
    with open(file_location) as file:
        api_keys = yaml.safe_load(file)
    return api_keys


def load_sql(file_location: str) -> str:
    '''opens a sql file and returns a string'''
    with open(file_location) as file:
        query = file.read()
    return query


def get_utc_timestamp(d_t: datetime = datetime.now(), unit: str = 'ms') -> int:
    '''get utc timestamp from datetime'''
    d_t = datetime.now(timezone.utc)
    utc_time = d_t.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()
    if unit == 'ms':
        return utc_timestamp * 1000
    return utc_timestamp
