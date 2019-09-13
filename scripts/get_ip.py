#!/usr/bin/python3

import os

if not os.path.isdir("/root/python"):
    os.mkdir("/root/python")
os.chdir("/root/python")

ok = os.path.exists('ip.txt')

if not ok:
    with open("ip.txt","w") as f:
        f.write("127.0.0.1")

# 读取文件保存的公网ip地址
with open("ip.txt",'r') as f:
    content = f.read()

content_ip = content.split()[0]

result = os.popen("curl -s members.3322.org/dyndns/getip","r")
r = result.read()

# 和文件中的ip地址比较，不相同则发送邮件，并覆盖现有文件
# 把地址记录到另外一个文件中
if r != "":
    get_ip = r.split()[0]
    if get_ip != content_ip:
        with open('ip.log','a+') as f1:
            f1.write(get_ip+'\n')

        with open('ip.txt','w') as f:
            f.write(get_ip)
        os.system('mailx -s "public ip" 583112952@qq.com < ip.txt')