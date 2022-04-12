#!/bin/bash
sudo service redis-server stop

killall redis-server

echo " "
echo "Redis server stoped..."