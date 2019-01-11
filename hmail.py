#! /usr/bin/env python

'''
模块名称：hmail
模块版本：v1.0
功能描述：
 - 支持邮件发送

Date:2019-01-10
Author:J.Hu
'''

# smtplib   负责发送邮件
# email     负责构造邮件
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import formataddr
from email.header import Header


# 服务器连接状态
SSTS_OFFLINE   = 0 # 服务器未连接
SSTS_CONNECTED = 1 # 服务器已连接
SSTS_LOGIN     = 2 # 用户已登陆

# 邮件格式类型
TYPE_PLAIN      = 'plain'
TYPE_HTML       = 'html'
TYPE_BASE_64    = 'base64'
TYPE_LIST = (
    TYPE_PLAIN,
    TYPE_HTML,
    TYPE_BASE_64
)

# 邮件内容编码类型
ENCODE_UTF8 = 'utf-8'
ENCODE_LIST = (
    ENCODE_UTF8
)

# 收发信人类型
SENDTYPE_FROM   = 'From'
RECVTYPE_TO     = 'To'
RECVTYPE_CC     = 'Cc'
RECVTYPE_BCC    = 'Bcc'


ERR_CONNECT_FAILED = 1
ERR_LOGIN_FAILED   = 2

class Hcontact:
    """
    联系人类型
    """
    def __init__(self, addr, name=None):
        self.addr = addr
        self.name = name or addr

class Hattach:
    """
    附件类型
    """
    def __init__(self,path,id):
        self.path = path
        self.id = id

class Hsmtp():
    """
    SMTP业务封装实现
    """
    def __init__(self,host,port,ssl=True):
        """
        初始化并连接服务器
        Arg：
          - host：服务器名
          - port：服务器端口
          - ssl：是否启用SSL(True：启用 / False：不启用) default:True
        """
        # 初始化数据
        # public
        self.sender         = None  # 发信人
        self.list_to        = []    # To对象列表
        self.list_cc        = []    # Cc对象列表
        self.list_bcc       = []    # Bcc对象列表
        self.title          = ''    # 邮件Title
        self.msg            = ''    # 邮件内容
        self.list_attach    = []    # 附件列表
        self.errmsg         = ''    # 错误消息

        # private
        self.__obj      = None          # SMTPLIB对象
        self.__ssts     = SSTS_OFFLINE  # 当前连接状态
        self.__encode   = ENCODE_UTF8   # 编码类型
        self.__type     = TYPE_HTML     # 正文类型
        self.__att_type = TYPE_BASE_64  # 附件类型
        self.__recv_mapping_list=(      # 映射关系
            (RECVTYPE_TO, self.list_to),
            (RECVTYPE_CC, self.list_cc),
            (RECVTYPE_BCC,self.list_bcc),
        )

        # 连接服务器
        self.connect(host,port,ssl)

    def connect(self,host,port,ssl):
        """
        连接服务器
        # Arg：
          - host：服务器名
          - port：服务器端口
          - ssl：是否启用SSL(True：启用 / False：不启用) default:True
        # 返回值：False 连接失败
        """
        # 如果已经连接到服务器了,关闭现有服务器，重新连接新服务器
        if self.__ssts != SSTS_OFFLINE:
            self.close()

        try:
            if ssl:
                self.__obj = smtplib.SMTP_SSL(host,port)
            else:
                self.__obj = smtplib.SMTP(host,port)

            self.__ssts = SSTS_CONNECTED    # 更新状态
        except:
            self.__obj = None
            self.errmsg = 'Connect to SMTP Server{0}:{1} Failed'.format(host,port)

    def login(self, user, passwd):
        """
        # 登陆
          - user：用户名
          - passwd:密码
        # 返回值：False：登陆失败,True登陆成功
        """
        # 未连接到服务器则不进行登陆
        if self.__ssts < SSTS_CONNECTED:
            return False

        try:
            self.__obj.login(user,passwd)
            self.__ssts = SSTS_LOGIN
            return True
        except:
            return False

    def set_sender(self,sender):
        """
        # 设置发信人
        """
        if isinstance(sender,Hcontact):
            self.sender = sender

    def set_receiver(self, recvlist_type, objlist=[]):
        """
        # 设置收件人列表
        # type_flg:收件列表类型：RECVTYPE_TO，RECVTYPE_CC，RECVTYPE_BCC
        # objlist:收件人List
        """
        for (type, list) in self.__recv_mapping_list:
            if recvlist_type == type:
                del list[:]
                for data in objlist:
                    if isinstance(data, Hcontact):list.append(data)
                break

    def set_mailtitle(self, title):
        """
        # 设置邮件标题
        """
        self.title = title

    def set_mailmsg(self, msg):
        """
        # 设置邮件内容
        """
        self.msg = msg

    def set_mailattach(self, attach_list=[]):
        """
        # 设置邮件附件列表
        """
        self.attach_list = attach_list

    def send(self,title=None,msg=None):
        """
        # 发送邮件
        """
        # 未登陆
        if self.__ssts != SSTS_LOGIN:
            return False

        title = title or self.title
        msg = msg or self.msg
        mime = MIMEMultipart()

        # Title 设置
        mime['subject'] = Header(title,self.__encode)

        # 发件人设置
        if self.sender is None:
            return False
        mime[SENDTYPE_FROM] = formataddr([self.sender.name,self.sender.addr])

        # 收件人设置
        send_list = []
        for (type,list) in self.__recv_mapping_list:
            for contact in list:
                send_list.append(contact.addr)
                mime[type] = formataddr([contact.name,contact.addr])
        if len(send_list) == 0:
            return False;

        # 附件设置
        
        try:
            mime.attach(MIMEText(msg,self.__type,self.__encode))
            self.__obj.sendmail(self.sender.addr, send_list, mime.as_string())
        except:
            return False
        return True

    def close(self):
        """
        关闭连接
        """
        self.__obj.quit()
        self.__ssts = SSTS_OFFLINE
