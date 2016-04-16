#! /bin/bash

# runs airodump

check=$(ifconfig | grep -c mon0)
if [ $check > 0 ]; then
	echo $check
	echo 'Scanner.sh was able to start airodump-ng.'
	sudo airodump-ng mon0
else
	echo 'Starting airmon for wlan0.'
	sudo airmon-ng start wlan0
	sleep 7
	echo 'Starting airodump-ng for mon0...'
	sudo airodump-ng mon0
fi
