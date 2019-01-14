#! /usr/bin/env python

'''
# 模块名称：hmail
# 模块版本：v1.0.1
# 功能描述：
 - 支持邮件发送
# 版本变更说明：
 - 连接服务器追加Timeout参数默认5秒
 - 移除了服务器状态的判断，降低代码代码复杂度
 - Hcontact不对外暴露，内部实现降低代码复杂度

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


# 默认Timeout，单位：秒
TIMEOUT = 5

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


class Hcontact:
    """
    联系人类型
    """
    def __init__(self, addr, name=None):
        if not isinstance(addr,str):raise TypeError(addr)
        self.addr = str(addr)
        self.name = name or addr

class Hattach:
    """
    附件类型
    """
    def __init__(self,path,name=None):
        if not isinstance(path,str):raise TypeError(path)
        self.path = path
        self.name = name or path.split('/')[-1]

class Hsmtp():
    """
    SMTP业务封装实现
    """
    def __init__(self,host,port=465,ssl=True):
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

    def connect(self,host,port,ssl=True,timeout=TIMEOUT):
        """
        连接服务器
        # Arg：
          - host：服务器名
          - port：服务器端口
          - ssl：是否启用SSL(True：启用 / False：不启用) default:True
          - timeout:服务器连接超时时间
        """
        if ssl:
            self.__obj = smtplib.SMTP_SSL(host,port,timeout = timeout)
        else:
            self.__obj = smtplib.SMTP(host,port,timeout = timeout)


    def login(self, user, passwd):
        """
        # 登陆
          - user：用户名
          - passwd:密码
        """
        self.__obj.login(user,passwd)

    def set_sender(self,addr,name=None):
        """
        # 设置发信人
        """
        try:
            self.sender = Hcontact(addr,name)
        except Exception as e:
            raise e

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
                    if not isinstance(data, Hcontact):raise TypeError(data)
                    list.append(data)
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
        self.list_attach = attach_list

    def send(self,title=None,msg=None,att_list=None):
        """
        # 发送邮件
        """
        title = title or self.title
        msg = msg or self.msg
        att_list = att_list or self.list_attach
        mime = MIMEMultipart()

        def mime_set(mime,type,val):
            mime[type] = formataddr([val.name,val.addr])

        def mime_attach(mime, att, attid):
            li = Hattach(att)
            att = MIMEText(open(li.path,'rb').read(), TYPE_BASE_64, self.__encode)
            att["Content-Type"] = 'application/octet-stream'
            att["Content-Disposition"] = 'attachment; filename='+li.name
            att.add_header('Content-ID', str(attid))
            mime.attach(att)

        # Title 设置
        mime['Subject'] = Header(title,self.__encode)

        # 发件人设置
        mime_set(mime, SENDTYPE_FROM, self.sender)

        # 收件人设置
        send_list = []
        for (type,list) in self.__recv_mapping_list:
            for contact in list:
                send_list.append(contact.addr)
                mime_set(mime,type,contact)

        # 附件设置
        attid = 0
        for li in att_list:
            mime_attach(mime,li,attid)
            attid+=1

        mime.attach(MIMEText(msg,self.__type,self.__encode))
        self.__obj.sendmail(self.sender.addr, send_list, mime.as_string())

    def close(self):
        """
        关闭连接
        """
        self.__obj.quit()
