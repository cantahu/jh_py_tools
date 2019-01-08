#! /usr/bin/env python

'''
1.Python有2个模块支持SMTP
    - smtplib   负责发送邮件
    - email     负责构造邮件
'''

# 当前支持SMTP协议的发送程序
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import formataddr
from email.header import Header

# 邮件格式类型
TYPE_PLAIN = 'plain'
TYPE_HTML = 'html'
TYPE_BASE_64='base64'
TYPE_LIST = (
    TYPE_PLAIN,
    TYPE_HTML
)

# 编码类型
ENCODE_UTF8 = 'utf-8'
ENCODE_LIST = (
    ENCODE_UTF8
)

# 收信人类型
RECETYPE_TO = 'To'
RECETYPE_CC = 'Cc'
RECETYPE_BCC = 'Bcc'
RECETYPE_LIST = (
    RECETYPE_TO,
    RECETYPE_CC,
    RECETYPE_BCC
)

class JHSmtp:
    obj = None      #SMTP对象
    __type = TYPE_HTML        # 格式
    __encode = ENCODE_UTF8    # 编码

    sender = ''     #发信人
    list_to = []    #To对象
    list_cc = []    #Cc对象
    list_bcc = []   #Bcc对象
    msg = ''        #邮件内容
    list_attach = []#附件列表

    ## 判断条件
    __list_flg = (
        (RECETYPE_TO, list_to),
        (RECETYPE_CC, list_cc),
        (RECETYPE_BCC,list_bcc),
    )

    # 初始化邮件对象
    def __init__(self,host,port,ssl_flg = True):
        if ssl_flg:
            self.obj = smtplib.SMTP_SSL(host,port)
        else:
            self.obj = smtplib.SMTP(host,port)

        #self.__mimemsg = MIMEMultipart('alternative')
        self.__mimemsg = MIMEMultipart()

    # 登陆SMTP服务器
    def login(self, username, passwd):
        self.obj.login(username,passwd)
        self.set_sender(username)

    # 设置邮件名
    def set_title(self, title):
        self.__mimemsg['Subject'] = Header(title,self.__encode)

    # 设置发件人
    def set_sender(self, val):
        self.sender = val
        self.__mimemsg['From'] = formataddr([self.sender,self.sender])

    # 设置收件人(to,cc,bcc)
    def set_receiver(self, type_flg, objlist=[]):
        for (type, list) in self.__list_flg:
            if type_flg == type:
                list.extend(objlist)
                break

    # 设置邮件内容
    def set_mailmsg(self, msg):
        self.msg = msg

    # 设置附件列表
    def set_attach(self, attach_list=[]):
        self.list_attach = attach_list

    # 发送邮件
    def send(self):
        # 设置收件人名称和邮件地址
        for (type, list) in self.__list_flg:
            for ma in list:
                self.__mimemsg[type] = formataddr([ma,ma])

        # 发送列表设置（to+cc+bcc）
        send_list = self.list_to + self.list_cc + self.list_bcc

        i = 0
        for li in self.list_attach:
            att = MIMEText(open(li,'rb').read(), TYPE_BASE_64, self.__encode)
            att["Content-Type"] = 'application/octet-stream'
            # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
            att["Content-Disposition"] = 'attachment; filename="test.txt"'
            att.add_header('Content-ID', str(i))
            self.__mimemsg.attach(att)
            i+=1;

        try:
            self.__mimemsg.attach(MIMEText(self.msg,self.__type,self.__encode))
            self.obj.sendmail(self.sender, send_list, self.__mimemsg.as_string())
        except:
            print("SendError")

    def sendmail(self,title,msg,attach=[]):
        self.set_title(title)
        self.set_mailmsg(msg)
        self.set_attach(attach)
        self.send()

    # 关闭SMTP
    def close(self):
        self.obj.quit();

if __name__ == '__main__':
    '''
    jhemail = je.JHSmtp(SMTPHOST, SMTPPORT)
    jhemail.login(USER, PWD)
    jhemail.set_receiver(je.RECETYPE_TO,['huj@citytsm.com','joestarhu@163.com'])
    title = get_mailtitle()
    msg  = get_mailmsg()
    jhemail.sendmail(title,msg,['年度工作总结.md','z.png'])
    jhemail.close();
     '''
