#!/usr/bin/env python
#coding:utf-8
import MySQLdb,sys,os
from BearCatOMS.settings import BASE_DIR,DATABASES

username = sys.argv[1]
server_groups = []
all_servers = []
with open('/home/%s/.tempfile' % username,'w') as f:
    f.write('''{'HOST': '%s', 'USER': '%s','PASSWORD': '%s','NAME': '%s',}''' % (DATABASES.values()[0]['HOST'],DATABASES.values()[0]['USER'],DATABASES.values()[0]['PASSWORD'],DATABASES.values()[0]['NAME']))

try:
    conn=MySQLdb.connect(host=DATABASES.values()[0]['HOST'],user=DATABASES.values()[0]['USER'],passwd=DATABASES.values()[0]['PASSWORD'],db=DATABASES.values()[0]['NAME'],port=3306,charset="utf8")
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
        conn=MySQLdb.connect(host=DATABASES.values()[0]['HOST'],user=DATABASES.values()[0]['USER'],passwd=DATABASES.values()[0]['PASSWORD'],db=DATABASES.values()[0]['NAME'],port=3306,charset="utf8")
        cur=conn.cursor()
        cur.execute('select external_ip from operation_server_list where server_name="%s"' % hostname)
        data = cur.fetchone()
        for i in data:
            external_ip = i
        conn.commit()
        cur.close()
        conn.close()
        os.system('python %s/others/audit_shell/audit_shell.py %s %s %s' % (BASE_DIR,i,username,hostname))
    except Exception:
        continue
    except KeyboardInterrupt:
        continue
    except EOFError:
        continue
