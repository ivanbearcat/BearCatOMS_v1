#coding:utf-8
from multiprocessing import Process
import Queue
import time,os


def a():
    while 1:
        print 1
        time.sleep(1)


if __name__ == '__main__':
    q = Queue.Queue()
    s = Process(target=a)
    q.put(s)
    s.start()
    l = q.get()
    print l
    time.sleep(5)
    l.terminate()