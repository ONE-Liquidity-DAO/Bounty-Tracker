import logging
DB_TYPE = 'sqlite+pysqlite'
DB_LOCATION = './data/database.sqlite'
BOUNTY_INFO_LOCATION = './config/bounty_info.yml'
CREDENTIALS_LOCATION = './credentials/api_list.yml'
CONFIG_LOCATION = './config/config.yml'
# logging info
LOG_LEVEL = logging.INFO
FILE_LOG_LEVEL = logging.WARNING
LOG_FILENAME = './logs/default.log'
# sql info
SQL_FOLDER = './src/sql/'
# google info
GOOGLE_LOGIN_LOCATION = f'./credentials/google_service_cred.json'
GOOGLE_WORKSHEET_NAME = 'DAO Tracker'
GOOGLE_BALANCES_NAME = 'Balances'
GOOGLE_TRADES_NAME = 'Trades'