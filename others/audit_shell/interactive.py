# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
#
# This file is part of paramiko.
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distrubuted in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.


import socket
import sys
import datetime
import MySQLdb

# windows does not have termios...
try:
    import termios
    import tty
    has_termios = True
except ImportError:
    has_termios = False


def interactive_shell(chan,web_username,hostname):
    if has_termios:
        posix_shell(chan,web_username,hostname)
    else:
        windows_shell(chan)


def posix_shell(chan,web_username,hostname):
    import select
    with open('/home/%s/.tempfile' % web_username) as f:
        DATABASES = f.readline()
        DATABASES = eval(DATABASES)

    oldtty = termios.tcgetattr(sys.stdin)
    print DATABASES['HOST'],DATABASES['USER'],DATABASES['PASSWORD'],DATABASES['NAME']
    conn=MySQLdb.connect(host=DATABASES['HOST'],user=DATABASES['USER'],passwd=DATABASES['PASSWORD'],db=DATABASES['NAME'],port=3306,charset="utf8")
    cur = conn.cursor()

    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)

        record = []

        while True:
            r, w, e = select.select([chan, sys.stdin], [], [])
            if chan in r:
                try:
                    x = chan.recv(1024)
                    if len(x) == 0:
                        print '\r\n*** EOF\r\n',
                        break
                    sys.stdout.write(x)
                    sys.stdout.flush()
                except socket.timeout:
                    pass

            if sys.stdin in r:
                x = sys.stdin.read(1)
                if len(x) == 0:
                    break
                try:
                    record.append(x)
                    if x == '\x7f' or x == '\x08':
                        record.pop()
                        record.pop()
                    if x == '\t':
                        record.pop()
                        record.append('[tab]')
                except Exception:
                    pass
                chan.send(x)
            if x == '\r':
                cmd = ''.join(record)
                time_now = datetime.datetime.now().strftime('%F %X')
                cur.execute('insert into audit_log (source_ip,username,command,time) values("%s","%s","%s","%s")' % (hostname,web_username,cmd,time_now))
                record = []

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)
        conn.commit()
        cur.close()
        conn.close()

    
# thanks to Mike Looijmans for this code
def windows_shell(chan):
    import threading

    sys.stdout.write("Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n")
        
    def writeall(sock):
        while True:
            data = sock.recv(256)
            if not data:
                sys.stdout.write('\r\n*** EOF ***\r\n\r\n')
                sys.stdout.flush()
                break
            sys.stdout.write(data)
            sys.stdout.flush()
        
    writer = threading.Thread(target=writeall, args=(chan,))
    writer.start()
        
    try:
        while True:
            d = sys.stdin.read(1)
            if not d:
                break
            chan.send(d)
    except EOFError:
        # user hit ^Z or F6
        pass
