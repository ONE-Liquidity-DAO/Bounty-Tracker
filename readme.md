# Summary

This fetches data from exchange using ccxt as the connector and export the data to a sql database.
# Installation

## 1) Install dependencies
sudo apt-get update
sudo apt-get install -y build-essential


## 2) Install Miniconda3
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh


## 3) Create Conda Environment
conda create -n bountytracker python=3.10


## 4) Activate Conda Environment
conda activate bountytracker


## 5) Install requirements
pip install -r requirements.txt


## 6) Clone the github repository
git clone https://github.com/ONE-Liquidity-DAO/Bounty-Tracker.git tracker


# Usage
## cd to the cloned repository
cd tracker

## run the script
there are 2 ways defined here to run the script (or whichever method you prefer)

### open tmux and run the script inside tmux to be reattached next time
run the following line while in the main folder and a tmux terminal will open.

chmod +x bin/start.sh

./bin/start.sh

you can leave the tmux by detaching with the following command
Crtl+b -> d
to reattach and view the running logs, use the following command 
(replace "1" with the session the log is running in )

e.g tmux attach -t "1"

### to run the script in background and set the output log to a file to be opened
the log can be viewed in output.log


chmod +x bin/start_connector.py
nohup bin/start_connector.py > output.log &
chmod +x bin/start_sync.py
nohup bin/start_sync.py > output.log &
