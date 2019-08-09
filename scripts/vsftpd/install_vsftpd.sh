#!/bin/bash

# get public ip
IP_ADDR=$(curl -s members.3322.org/dyndns/getip)

if [ $? -eq 0 ];then
	sed -i "s/#pasv_address=8.8.8.8/pasv_address=$IP_ADDR/" vsftpd.conf;
fi

useradd -d /ftp -s /sbin/nologin vuser 2>&1 > /dev/null 

if [ ! -e /ftp ];then
	mkdir /ftp;
fi

chmod +rx /ftp
chmod -w /ftp

if [ ! -e /ftp/upload ];then
	mkdir /ftp/upload;
fi

setfacl -m u:vuser:rwx /ftp/upload

yum install -y vsftpd ftp 2>&1 > /dev/null 
chmod 600 vusers.db

/usr/bin/cp -rf {vsftpd.conf,vusers.d,vusers.db,.vusers.txt} /etc/vsftpd/
/usr/bin/cp vsftpd.pam /etc/pam.d/

systemctl enable vsftpd
systemctl start vsftpd
