#! /usr/bin/env python

'''
1.Python有2个模块支持SMTP
    - smtplib   负责发送邮件
    - email     负责构造邮件
'''

# 当前支持SMTP协议的发送程序
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

# plain/html
JHEMAIL_TYPE_PLAIN = 'plain'
JHEMAIL_TYPE_HTML = 'html'

# 追加类型的时候，下面List中也要追加
JHEMAIL_TYPE_LIST = (
    JHEMAIL_TYPE_PLAIN,
    JHEMAIL_TYPE_HTML
)

# utf8
JHEMAIL_ENCODE_UTF8 = 'utf-8'
# 追加类型的时候，下面List中也要追加
JHEMAIL_ENCODE_LIST = (JHEMAIL_ENCODE_UTF8)

class JHEmail:
    obj = None      #SMTP对象
    sender = []     #发信人
    list_to = []    #To对象
    list_cc = []    #Cc对象
    list_bcc = []   #Bcc对象

    def __init__(self,host,port,ssl_flg = True):
        if ssl_flg:
            self.obj = smtplib.SMTP_SSL(host,port)
        else:
            self.obj = smtplib.SMTP(host,port)

    def __val_chk(self,val,chk_list):
        return val in chk_list

    def __format_addr(self,msg, tar, list):
        for i in list:
            msg[tar] = formataddr([i,i])

    def __set_addrname(self,msg):
        msg['From'] = formataddr([self.sender,self.sender])
        self.__format_addr(msg,'To',self.list_to);
        self.__format_addr(msg,'Cc',self.list_cc);
        self.__format_addr(msg,'Bcc',self.list_bcc);

    def login(self, username, passwd):
        self.obj.login(username,passwd)
        self.sender = username;

    def sendmsg(self,title,content,type = JHEMAIL_TYPE_HTML,encode = JHEMAIL_ENCODE_UTF8):
        # 判断类型和编码,并且自动修复
        if not self.__val_chk(type, JHEMAIL_TYPE_LIST):
            type = JHEMAIL_TYPE_HTML

        if not self.__val_chk(encode, JHEMAIL_ENCODE_LIST):
            encode = JHEMAIL_ENCODE_UTF8

        # 正文内容设置
        msg = MIMEText(content,type,encode)
        self.__set_addrname(msg)
        msg['Subject'] = title

        #合并SendList内容
        send_list = self.list_to + self.list_cc + self.list_bcc
        self.obj.sendmail(self.sender, send_list, msg.as_string())

    def close(self):
        self.obj.quit();

if __name__ == '__main__':
    '''
    jhemail = jhemail.JHEmail(SMTPHOST, SMTPPORT)
    jhemail.login(USER, PWD)
    jhemail.list_to = ['huj@citytsm.com']
    # jhemail.list_bcc = ['joestarhu@163.com']
    jhemail.sendmsg(MSGTITLE,MSGINFO)
    jhemail.close();
    '''
