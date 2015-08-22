#coding:utf-8
from libs.socket_send_data import client_send_data
import time
cmd = ["curl http://www.whereismyip.com/|grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'"]
start = time.time()
external_ip = client_send_data("{'salt':1,'act':'cmd.run','hosts':'%s','argv':%s}" % ('DB-01',cmd),'123.59.107.121',7777)
end = time.time()
print external_ip
print end - start