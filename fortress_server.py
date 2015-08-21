#!/usr/bin/env python
#coding:utf-8
import MySQLdb,sys,os
#from libs.server_list_conf import server_lists
from BearCatOMS.settings import BASE_DIR
from libs.socket_send_data import client_send_data

username = sys.argv[1]
server_groups = []
all_servers = []
try:
    conn=MySQLdb.connect(host='127.0.0.1',user='admin',passwd='!@#rp1qaz@WSX',db='BearCatOMS',port=3306,charset="utf8")
    cur=conn.cursor()
    cur.execute('select server_groups from user_manage_perm where username="%s"' % username)
    data = cur.fetchall()
    for i in data:
        for j in i:
            for n in j.split(','):
                server_groups.append(n)
    for i in server_groups:
        cur.execute('select members_server from operation_server_group_list where server_group_name="%s"' % i)
        data = cur.fetchall()
        for j in  data:
            for n in j:
                for m in n.split(','):
                    all_servers.append(m)
    conn.commit()
    cur.close()
    conn.close()
except Exception,e:
    print e
    sys.exit(1)

while 1:
    try:
        print '=================='
        for i in all_servers:
            print '\033[34;1m%s\033[0m' % i
        print '=================='

        hostname = raw_input('please input hostname to login("exit" to logout)：').strip()
        if hostname == 'exit':
            sys.exit(0)
        if hostname == '' or hostname not in all_servers:
            print '主机名不正确'
            continue
        client_send_data("{'salt':1,'act':'cmd.run','hosts':'%s','argv':%s}" % (j,cmd.split(',')),CENTER_SERVER[i.server_group_name][0],CENTER_SERVER[i.server_group_name][1])

        os.system('python %s/others/audit_shell/audit_shell.py %s %s' % (BASE_DIR,server_lists[hostname],username))
    except Exception:
        continue
    except KeyboardInterrupt:
        continue
    except EOFError:
        continue
