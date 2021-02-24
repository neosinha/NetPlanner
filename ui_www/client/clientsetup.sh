#!/usr/bin/env bash

stdt=$(date)
clear
echo "=== Updating System, started $stdt  ==="
sleep 1
apt-get update
apt-get -y install lshw
apt-get -y install curl
apt-get -y install isc-dhcp-server
apt-get -y install vim
apt-get -y install python3-pip
echo ""


stdt=$(date)
echo "=== Starting setup at $stdt  ==="
ip a > sysnetinfo
echo ";" >> sysnetinfo
lshw -short >> sysnetinfo
echo "==" >> sysnetinfo
netinfo=$(ip a | grep ^[0-9]*:.*: | sed 's/^[0-9]*://g' | sed 's/^ //g' | sed 's/:.*$//g' | sed ':a;N;$!ba;s/\n/;/g' | base64)
b64str=$(base64 -w 0 sysnetinfo)
echo $b64str > sysnetinfo.b64
info=$(base64 -d sysnetinfo.b64)
curl 'http://172.16.10.54:6001/registerhost?appldef='"$netinfo"
sleep 1
curl 'http://172.16.10.54:6001/networkinterfaces?appldef='"$netinfo" > interfaces
echo "==================="
echo "=== Cleaning Up ===="
rm -vf sysnetinfo*
rm -vf getInstallScript

