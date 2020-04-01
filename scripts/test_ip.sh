#!/bin/bash

for n in {33..254}
do
	host=192.168.1.$n
	(ping -c2 $host &>/dev/null

	if [ $? = 0 ];then
		echo "$host is UP"
		echo "$host UP" >> ip.txt
	else
		echo "$host is DOWN"
	fi)&
done
