#!/usr/bin/python3

import os

if not os.path.isdir("/root/python"):
    os.mkdir("/root/python")
os.chdir("/root/python")

ok = os.path.exists('ip.txt')

if not ok:
    with open("ip.txt","w") as f:
        f.write("127.0.0.1")

with open("ip.txt",'r') as f:
    content = f.read()

content_ip = content.split()[0]

result = os.popen("curl -s members.3322.org/dyndns/getip","r")
r = result.read()

if r != "":
    get_ip = r.split()[0]
    if get_ip != content_ip:
        with open('ip.txt','w') as f:
            f.write(get_ip)
        os.system('mailx -s "public ip" 583112952@qq.com < ip.txt')
