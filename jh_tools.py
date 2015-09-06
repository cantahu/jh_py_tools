#! /usr/bin/python
#-*- coding:utf-8 -*-

#===============================#
#	Design By Jian.Hu	#
#===============================#

# ########################################################################
# 20150906 Update: install的时候增加了source命令，不需要在使用su命令了
# ########################################################################
# 拷贝到用户目录下，
# 如我的用户目录是/home/hansun/ 就拷贝到这里,
# 然后执行 python jh_tools.h
# 然后重新 su - [你的用户名]
# 再次进入后可以使用hmake, start stop服务了
# hmake 简化了每次make需要输入的东西，并且可以一次性输入多个gcc文件
# 用空格分割
# Start和Stop系列命令，则不需要每次进入workspace里面执行了，
# 直接在SRC下面也可以执行
# #######################################################################

import os
import getpass
import sys

# Global Setting ==========================
g_file_path = os.getcwd()+"/" + __file__;

# Start and Stop Command.
WORK_CMD={
    0:'startaccessar.sh &',
    1:"stopaccessar.sh &",
    2:"startbusar.sh &",
    3:"stopbusar.sh &",
    4:"startlogicas.sh &",
    5:"stoplogicas.sh &",
    6:"startatomas.sh &",
    7:"stopatomas.sh &",
};


## Get Current User Name.
def jh_getusername():
    return getpass.getuser();


def jh_chdir(work_path):
    try:
        os.chdir(work_path);
    except:
        print("[ErrInfo] os.chdir:%s failed"%work_path);
        sys.exit();
    return;

## Do make Command
def do_hmake():
    for i in sys.argv[2:]:
        cmd = "make -f "+ i +' ORA_VER=10'
        os.system(cmd);
    return;


##
def chk_is_install(work_path):
    cmd = "grep hmake "+work_path+".bash_profile -c"
    val = os.popen(cmd).read();
    val=int(val);
    if(val > 0):
        print("Install Over");
        sys.exit();

def install_command(cmdname, arg):
    file_path = os.getcwd()+"/" + __file__;
    cmd = "echo \"alias " + cmdname + "=\'python "+ g_file_path +" "+ arg + "\'\" >> .bash_profile ";
    os.system(cmd);

## Install this Tools
def do_install(username):
    work_path = "/home/"+jh_username+"/";
    chk_is_install(work_path); 

    #install
    jh_chdir(work_path)
    install_command("hmake", "90");
    install_command("startaccessar", "0");
    install_command("stopaccessar", "1");
    install_command("startbusar", "2");
    install_command("stopbusar", "3");
    install_command("startlogicas", "4");
    install_command("stoplogicas", "5");
    install_command("startatomas", "6");
    install_command("stopatomas", "7");
    #reload bash_profile
    os.system("source .bash_profile");

    
## make Start and Stop Easy.
def do_svr(username,arg):
    work_path = "/home/"+jh_username+"/workspace/";
    jh_chdir(work_path);
    os.system(WORK_CMD[arg]);
    return;

## Main Event.
if __name__ == '__main__':
    try:
        arg = sys.argv[1];
    except:
        arg = 99;
    arg = int(arg);

    ## Get Current UserName.
    jh_username = jh_getusername();
    
    #install this tool
    if(arg == 99):
        do_install(jh_username);

    # Do make Command
    if(arg == 90):
        do_hmake();

    if(arg >=0 and arg <= 7):
        do_svr(jh_username, arg);


        
