#!/bin/sh

log_file=logs.txt

nohup python3 -u ./api.py > $log_file &
pid=$(pgrep -f api.py)
echo $pid
date >> $log_file
 >> $log_file


