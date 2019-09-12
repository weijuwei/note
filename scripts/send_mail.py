from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib


# 邮件内容 文本内容
def mail_content(content,from_addr,to_addr,subject):
    msg = MIMEText(content,'plain','utf-8')
    msg['From'] = from_addr  # 邮件头部发件人信息
    msg['To'] = to_addr  # 邮件头部收件人信息
    msg['Subject'] = subject  # 邮件主题

    return msg.as_string()

# 邮件内容，添加图片附件
def mail_content_attach(content,from_addr,to_addr,subject,img_path):
    msg = MIMEMultipart()
    msg.attach(MIMEText(content,'plain','utf-8'))
    msg['From'] = from_addr  # 邮件头部发件人信息
    msg['To'] = to_addr  # 邮件头部收件人信息
    msg['Subject'] = subject  # 邮件主题

    with open(img_path,'rb') as f:
        mime = MIMEImage(f.read())
        mime.add_header('Content-ID', 'Imgid')
        msg.attach(mime)
    return msg.as_string()


def send_mail(from_addr,password,to_addr,msg):
    smtp_server = 'smtp.' + from_addr.split('@')[1]  # 邮箱SMTP服务器

    try:
        server = smtplib.SMTP(smtp_server, 25)  # 连接服务
#        server.set_debuglevel(1)  # 在控制台输出详细信息
        server.login(from_addr, password)  # 登陆认证
        server.sendmail(from_addr, to_addr, msg)  # 发送邮件
        server.quit()
    except smtplib.SMTPException:
        print("发送失败，请重新检查！！！")




if __name__ == '__main__':
    #  发件人地址
    #from_addr = input("请输入发送者邮箱地址：")
    from_addr = 'weijuwei@sina.cn'
    # 发件人密码
    #password = input("请输入发送者邮箱密码：")
    password = 'w583112952sina'
    # 收件人地址
    #to_addr = input("请输入收件者邮箱地址：")
    to_addr = '583112952@qq.com'
    # 邮件smtp服务地址
    # smtp_server = input("请输入邮件发送服务器SMTP：")


    content = "你好，这封邮件时从python发过来的！！！！"
    msg = mail_content(content,from_addr,to_addr,"测试邮件3")
    # msg = mail_content_attach(content,from_addr,to_addr,"测试邮件3",'file')
    send_mail(from_addr,password,to_addr,msg)
