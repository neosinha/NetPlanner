'''
Created on Oct 6, 2019

@author: navendusinha
'''

cmdbuffers = {}
cmdbuffers['ip-a'] = '1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000\n\
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00\n\
    inet 127.0.0.1/8 scope host lo\n\
       valid_lft forever preferred_lft forever\n\
    inet6 ::1/128 scope host \n\
       valid_lft forever preferred_lft forever\n\
2: enp1s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000\n\
    link/ether 00:90:27:e2:21:a2 brd ff:ff:ff:ff:ff:ff\n\
    inet 172.16.10.28/24 brd 172.16.10.255 scope global dynamic enp1s0\n\
       valid_lft 31533033sec preferred_lft 31533033sec\n\
    inet6 fe80::290:27ff:fee2:21a2/64 scope link \n\
       valid_lft forever preferred_lft forever\n\
3: enp2s0: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000\n\
    link/ether 00:90:27:e2:21:a3 brd ff:ff:ff:ff:ff:ff\n\
4: enp3s0: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000\n\
    link/ether 00:90:27:e2:21:a4 brd ff:ff:ff:ff:ff:ff\n\
5: enp4s0: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000\n\
    link/ether 00:90:27:e2:21:a5 brd ff:ff:ff:ff:ff:ff\n'
    
    
