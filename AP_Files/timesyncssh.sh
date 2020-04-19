#!/bin/bash

nmap -sn -oG ip.txt 192.168.5.1-255 > /dev/null
iphost=$(hostname -I)
#echo "$iphost"
iplist=($(cat ip.txt | grep Host: | awk -v h=$iphost 'NR> 1 {if ($2!=h) print $2}'))
#printf '%s\n' "${iplist[@]}"
#ssh-keygen -b 2048 -t rsa -f /home/pi/.ssh/id_rsa -q -N "" 0>&-
#for i in "${iplist[@]}"
#do
	#sudo sshpass -p "raspberry" ssh-copy-id -i ~/.ssh/id_rsa pi@$i
	#ssh-copy-id -i ~/.ssh/id_rsa pi@$i
#done
for i in "${iplist[@]}"
do
	#echo $i
	ssh pi@$i sudo date -s$(date -Ins) > /dev/null
done
