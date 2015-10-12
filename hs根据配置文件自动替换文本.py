#! /usr/bin/python
# -*- encoding:utf-8 -*-

## Designed By Jian.Hu

# The Name Repalce method:
# - Replace the ObjectId
#   use command sed -i 's/objectId=\".*\"objectId=\"[New Value]\"/g'
# - Replace the English Name
#   use command sed -i 's/englishName=\"[a-z0-9A-Z_]*\"/englishName=\"[New Value]\"/g'
# - Replace Code zone[chinese ]
#   use command sed -i '
# - Replace the File Name.
#   user command sed - i 's/[old value]/[new value]/g'

import os
import sys
import csv
import shutil

# Macro
INDEX_OLD_FILENAME=0;
INDEX_NEW_FILENAME=1;
INDEX_OBJECT_ID=2;
INDEX_ENGLISH_NAME=3;

# Global Value.
g_config_info=[];
g_config_path='';
g_work_path=[];

# Show version information
def version():
    print("Name-Change-V1.0 Designed By Jian.Hu\n");
    return;

# Show usage information
def usage():
    print("Usage:\n"
          "  name_change [Config Path] [target1] (taget2) (target3)...\n"
          "  *** target2, target3 is optional\n"
          "e.g.\n"
          "  name_change /home/huja/config.csv /home/huja/src/"
    );
    exit();

# Read the config file which shoule be a csv file.
# and put the config file into config info.
def read_config_file():
    global g_config_path;
    global g_config_info;

    try:
        fp = open(g_config_path, 'r');
    except:
        print("[ErrorInfo] Can't open file :%s"%g_config_path);
        exit();

    try:
        buf = csv.reader(fp);
    except:
        print("[ErrorInfo]Can't read the csv file");
        fp.close();
        exit();
        
    for line in buf:
        g_config_info.append(line);

    fp.close();
    return;

# Check the Config file path and Work path is avaiable
# and this script need two tools which are Svn and Sed
def check_sys():
    global g_config_path;
    global g_work_path;

    try:
        g_config_path = sys.argv[1];
    except:
        usage();

    if os.path.exists(g_config_path) == False:
        print("[ErrorInfo]Config File %s is not exists."%g_config_path);
        exit();

    for arg in sys.argv[2:]:
        if os.path.exists(arg) == False:
            print("[WarningInfo] %s is not exists."%arg);
        else:
            g_work_path.append(arg);

    if len(g_work_path) < 1:
        print("[ErrorInfo] Work Path is not indicate");
        usage();
        
    cmds = {"svn":"svn --help >> nul",
            "sed":"sed --help >> nul"};

    for prog,cmd in cmds.items():
        #invoke command.
        ret = os.system(cmd);
        if ret != 0:
            print("[ErrInfo]:%s is not installed."%prog);
            exit();
    return;

# Get the file context which had been include by '[]'
def get_code_info(target):
    code_info = [];
    arg = '';
    try:
        fp = open(target, 'r');
    except:
        print("[ErrorInfo]Can't Open %s."%target);
        exit();

    while True:
        flg = False;
        arg = '';
        buf = fp.readline();
        if not buf:break;
        for i in buf:
            if flg == True:
                if i == '[':
                    flg = False;
                    continue;
                
                if i == ']':
                    flg = False;
                    code_info.append(arg);
                    arg = '';
                    continue;
                arg = arg + i;
                continue;

            if i == '[':
                flg = True;
                continue;

    return code_info;

# Replace work starts.
def replace_main(work):
    global g_config_info;
    hit_flg = False;

    # split the old file name from work path
    (path,oldname) = os.path.split(work);
    (old_file_name, extend_name) = os.path.splitext(oldname);
    
    for info in g_config_info:
        if old_file_name == info[INDEX_OLD_FILENAME]:
            hit_flg = True;
            break;

    if hit_flg == False:
        return;

    new_name = info[INDEX_NEW_FILENAME];
    object_id = info[INDEX_OBJECT_ID];
    english_name = info[INDEX_ENGLISH_NAME];

    if path != '':
        newfile = path + '/' + new_name + extend_name; 
    else:
        newfile = new_name + extend_name;
    
    try:
        shutil.copyfile(work,newfile);
    except:
        print("[WarningInfo] Copy New file [%s] from [%s] faild"%newfile,work);
        return;

    # 1.replace objectid wtih New
    cmd = "sed -i \"s/objectId=\".*\"/objectId=\""+object_id+"\"/g\" "+newfile;
    os.system(cmd);
    
    # 2.replace English Name with New
    cmd = "sed -i \"s/englishName=\".*\"/englishName=\""+english_name+"\"/g\" "+newfile;
    os.system(cmd);
    
    # 3.Code Zone Replace.
    zone_info = get_code_info(newfile);
    for i in zone_info:
        for info in g_config_info:
            if i == info[INDEX_OLD_FILENAME]:
                new_invoke = info[INDEX_NEW_FILENAME];
                cmd = "sed -i \"s/"+i+"/"+new_invoke+"/g\" " + newfile;
                os.system(cmd);
    return;
    
## The Main Event
def do_main(work):
    if os.path.isdir(work) == True:
        #this should enter the sub directory,and search for all file.
        nil;

    if os.path.isfile(work) == True:
        replace_main(work);

    return;

# Invoke svn command lock
#def svn_lock(target_file):
#    cmd = "svn lock " + target_file;
#    ret = os.popen(cmd).read();
    
# Invoke svn command unlock  
#def svn_unlock(target_file):
#    cmd = "svn unlock " + target_file; 
#    ret = os.popen(cmd).read();

## Main process
if __name__ == '__main__':
    check_sys();
    read_config_file();
    for work in g_work_path:
        do_main(work);

 


