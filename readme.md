Sample reward format by filled order
# Usage
run pip install -r requirements.txt

set up bounty info and accounts

run main.py

refer to config.yml for adding bounty info

https://github.com/leastchaos/Tracker/blob/main/config/config.yml

refer to app_list.yml for adding account

https://github.com/leastchaos/Tracker/blob/main/credentials/api_list_template.yml

refer to analysis folder for sample output by filled percent order of multiple account

https://github.com/leastchaos/Tracker/blob/main/filled_order.ipynb

# Summary

it fetches data from exchange using ccxt as the connector and export the data to a sql database.
then data analysis can be performed using pandas or other library as required.
