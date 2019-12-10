#!/bin/sh

nohup python3 -u ./api.py > logs.txt 2>&1 &
