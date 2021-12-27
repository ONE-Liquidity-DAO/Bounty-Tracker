# import packages and get relevant data from sql
from src.utils import get_utc_timestamp
import pandas as pd
from src.constants import DB_TYPE, DB_LOCATION

connector = f"{DB_TYPE}:///{DB_LOCATION}"
trades_df = pd.read_sql_table("Trades", connector)

symbol = "SAND/USDT"
exchange_name = "okex"
start_time = 0
end_time = get_utc_timestamp()

check_symbol = trades_df.symbol == symbol
check_exchange = trades_df.exchange_name == exchange_name
check_start_time = trades_df.timestamp > start_time
check_end_time = trades_df.timestamp < end_time
print(trades_df[check_symbol & check_exchange & check_start_time & check_end_time])
