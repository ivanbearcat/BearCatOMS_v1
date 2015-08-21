#!/usr/bin/env python
import urllib,urllib2,socket,sys,fcntl,struct,threading,os

def get_local_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))
    ret = socket.inet_ntoa(inet[20:24])
    return ret

def run(post_url,data):
    urllib2.urlopen(post_url,data)

try:
    pid = os.fork()
    if pid > 0:
        sys.exit(0)
    ip = get_local_ip("eth0")
    username = sys.argv[2]
    time = ' '.join(sys.argv[3:5])
    command = ' '.join(sys.argv[5:])

    values = {'ip':ip,
              'username':username,
              'command':command,
              'time':time}

    data = urllib.urlencode(values)
    post_url = 'http://192.168.100.42:8000/audit_get_data/'

    thread = threading.Thread(target=run, args=(post_url,data))
    thread.start()
#	conn = urllib2.urlopen(post_url,data)
except Exception , e:
    pass
