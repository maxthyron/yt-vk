#!/bin/bash

read -rp "Enter login: " LOGIN
read -rsp "Enter password: " PASSW
read -rp "Enter key: " KEY
read -rp "Enter group ID: " GROUP_ID

echo LOGIN=$LOGIN > .env
echo PASSW=$PASSW >> .env
echo KEY=$KEY >> .env
echo GROUP_ID=$GROUP_ID >> .env

