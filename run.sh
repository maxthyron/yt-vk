#!/bin/sh

log_file=logs.txt

nohup python3 -u ./api.py > logs.txt 2>&1 & echo $! > run.pid
cat run.pid | pgrep -P $!
