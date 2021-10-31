#!/usr/bin/env bash
# C: Fahad ahammed

grep "Host " /Users/fahad/.ssh/config | awk '{print $2}'
echo -e "................"
read -p 'Host to Connect: ' hn

ssh $hn
