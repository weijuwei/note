#!/usr/bin/python3
# 公司公网地址是浮动公网ip，探测公网IP地址的变动
import os,re
import send_mail as sm  # 同一目录下的send_mail.py发送邮件脚本


def get_ip():

	# 获取本地公网ip地址
	ip = os.popen('curl -s ifconfig.me').readline()
	
	if not os.path.isfile('ip.txt'):  # 判断存放IP的文件是否存在，不存在则创建，并写入一个地址
		with open('ip.txt','w') as f:
			f.write('127.0.0.1')

	# 读取本地文件中存储的ip地址
	with open('ip.txt','r') as f:
		record_ip = f.readline()
	
	return (ip,record_ip)  # 返回一个元组信息


def ip_notify(get_ip,record_ip):
	if not get_ip == record_ip:
		dt = re.sub(r'\n','',os.popen('date +%F-%T').readline()) # 记录检测时间
		log = '%s ip: %s —> %s\n'%(dt,re.sub(r'\n','',record_ip),get_ip)
		with open('ip.txt','w+') as f:  # 将新的ip写入到文件中
			f.write(get_ip)
		#with open('ip_change.log','a') as f1:  # 将变更记录到到日志文件中
		#	f1.write(log)
		from_addr = ''  # 发件人地址
		to_addr = ''  # 收件人地址
		password = ''  # 邮箱密码
		subject = '公网ip地址变更通知'  # 邮件主题
		msg = sm.mail_content(log,from_addr,to_addr,subject)
		sm.send_mail(from_addr,password,to_addr,msg)
	

ip_tup = get_ip()
ip_1 = ip_tup[0]
ip_2 = ip_tup[1]

ip_notify(ip_1,ip_2)
