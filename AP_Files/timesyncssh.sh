#!/bin/bash

#Author: Anamitra Datta

#Script to SSH into every Pi in the network from the Access point Raspberry Pi attached with an RTC and set the time on each Pi
#to the time on the AP pi's RTC

#INCOMPLETE

#Get the list of all IP addresses in the current network
nmap -sn -oG ip.txt 192.168.5.1-255 > /dev/null

#get the host machines's IP address
iphost=$(hostname -I)
#echo "$iphost"

#make a list of all IP addresses besides the host's IP address
iplist=($(cat ip.txt | grep Host: | awk -v h=$iphost 'NR> 1 {if ($2!=h) print $2}'))
#printf '%s\n' "${iplist[@]}"

#Make an SSH key for the network 
ssh-keygen -b 2048 -t rsa -f /home/pi/.ssh/id_rsa -q -N "" 0>&-

#Copy the SSH key into every Pi. NEEDS TO BE IMPROVED
for i in "${iplist[@]}"
do
	sudo sshpass -p "raspberry" ssh-copy-id -i ~/.ssh/id_rsa pi@$i
	ssh-copy-id -i ~/.ssh/id_rsa pi@$i
done

#Set the time in each Raspberry Pi from the RTC through ssh
for i in "${iplist[@]}"
do
	#echo $i
	ssh pi@$i sudo date -s$(date -Ins) > /dev/null
done
