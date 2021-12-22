import yaml
from datetime import datetime, timezone

def load_yml(file_location):
    with open(file_location) as f:
        api_keys = yaml.safe_load(f)
    return api_keys
def load_sql(file_location):
    with open(file_location) as f:
        query = f.read()
    return query
def get_utc_timestamp(dt=datetime.now(), unit='ms'):
    dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()
    return utc_timestamp * 1000