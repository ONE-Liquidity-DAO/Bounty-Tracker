#!/bin/sh 
tmux new-session -d
tmux set -g mouse on
tmux send-keys "conda activate bountytracker" Enter "bin/start_connector.py" Enter
tmux split-window -v
tmux send-keys "conda activate bountytracker" Enter "bin/start_sync.py" Enter