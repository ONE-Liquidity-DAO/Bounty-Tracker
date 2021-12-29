# Summary

it fetches data from exchange using ccxt as the connector and export the data to a sql database.
then data analysis can be performed using pandas or other library as required.

refer to analysis folder for sample output by filled percent order of multiple account

https://github.com/leastchaos/Tracker/blob/main/filled_order.ipynb


# Installation
run pip install -r requirements.txt

# Usage

set up bounty info and accounts

refer to bounty_info.yml for adding bounty info

https://github.com/leastchaos/Tracker/blob/main/config/bounty_info.yml

refer to app_list_template.yml for adding account

rename to app_list and  add  required api keys

https://github.com/leastchaos/Tracker/blob/main/credentials/api_list_template.yml


run main.py
