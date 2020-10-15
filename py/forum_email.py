import smtplib
import base64
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import COMMASPACE



class email():
    def __init__(self, config):

        self.SENDER = config[0]
        self.USER_ACCOUNT = {'username': config[1], 'password': config[2]}
    

    def send(self, receivers:list, subject, text):
        print("邮箱发送邮件到 {}".format(receivers))
        try:
            msg_root = MIMEMultipart()  # 创建一个带附件的实例
            msg_root['Subject'] = subject  # 邮件主题
            msg_root['To'] = COMMASPACE.join(receivers)  # 接收者
            msg_text = MIMEText(text, 'html', 'utf-8')  # 邮件正文
            msg_root.attach(msg_text)  # attach邮件正文内容

            smtp = smtplib.SMTP('smtp.gmail.com:587')
            # smtp = smtplib.SMTP('smtp.qq.com')

            smtp.ehlo()
            smtp.starttls()
            # print(self.USER_ACCOUNT['username'], self.USER_ACCOUNT['password'])
            smtp.login(self.USER_ACCOUNT['username'], self.USER_ACCOUNT['password'])
            smtp.sendmail(self.SENDER, receivers, msg_root.as_string())
            print("邮件发送成功")
            return True
        except:
            print("邮件发送失败")
            return False
