#!/usr/bin/env python
#coding:utf-8
import os,socket,Queue
from threading import Thread

class open_web_shell(object):

    def __init__(self):
        self.port_pool = range(20001,20004)
        self.q = Queue.Queue(10)

    def process(self,ip_list):
        for i in eval(ip_list):
            port = self.port_pool.pop(0)
            self.port_pool.append(port)
            if self.port_test(i,22):
                if self.q.qsize() >= 10:
                    process = self.q.get()
                    process.terminate()
                process = Thread(target=self.open,args=(port,i))
                self.q.put(process)
                process.start()
                return True
            else:
                return False


    def open(self,port,ip):
        os.system('/usr/local/shellinabox/bin/shellinaboxd -u shellinabox -g shellinabox -b -c /var/lib/shellinabox -p %s -s /:SSH:%s' % (port,ip))

    def port_test(self,ip,port):
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            s.connect((ip,port))
            s.shutdown(2)
            return True
        except:
            return False