import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
from email.mime.application import MIMEApplication

#邮件发送的用户名和密码  常识：第三方授权码
_user = "133451XXXXXX@qq.com"
_pwd = "rcXXXXXih"     #要在邮箱获取第三方授权码P0p3功能

now = time.strftime('%Y-%m-%d_%H_%M_%S')#获取时间戳

class sendEmail:
    def send_email(self, email_to, filepath):
        #email_to  收件方
        #filepath 你要发送附件的地址
        #如名字所示Multipart就是分多个部分
        msg = MIMEMultipart()
        msg["Subject"] = now+"接口测试报告_20181020"
        msg["From"] = _user
        msg["To"] = email_to

        #---这是文字部分---
        part = MIMEText("这次接口自动化测试结果，请查收！")
        msg.attach(part)

        #---这是附件部分---
        part = MIMEApplication(open(filepath, 'rb').read())  #文件要打开才能发送
        part.add_header('Content-Disposition', 'attachment', filename=filepath)
        msg.attach(part)
        s = smtplib.SMTP_SSL("smtp.qq.com", timeout=30)   #连接smtp邮件服务器,端口默认是25
        s.login(_user, _pwd)       #登陆服务器
        s.sendmail(_user, email_to, msg.as_string())           #发送邮件
        s.close()

if __name__ == '__main__':
    sendEmail().send_email("775341320@qq.com", r"E:\2018Python课件&代码\code\python_10\API_Frame_Work_1019\test_result\report\test_api.html")
    # 地址要转义 \r \t \201 特殊意义 1.加多/转义 2.前面r 全部转为普通