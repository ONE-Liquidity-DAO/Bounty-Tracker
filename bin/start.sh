#!/bin/sh 
tmux new-session

tmux send-keys "conda activate bountytrack" Enter "bin/start_connector.py" 
tmux split-window -v
tmux send-keys "conda activate bountytrack" Enter "bin/start_sync.py" 