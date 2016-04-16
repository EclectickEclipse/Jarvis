#! /bin/bash 
# echo 'Running First Pipeline'
ifconfig | grep -A 6 $1 | grep netmask | ./Resources/Scripts/jarvFiner.r/cutter.py