#coding:utf-8
import logging,os
from logging.handlers import RotatingFileHandler

class logger(object):
    def __init__(self):
        self.log = logging.getLogger() 
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter) 
        self.log.addHandler(stream_handler)
        #定义一个RotatingFileHandler，最多备份5个日志文件，每个日志文件最大10M
        Rthandler = RotatingFileHandler(os.path.abspath(os.path.dirname(__file__)) + '/../logs/server.log', maxBytes=1024*1024,backupCount=5)
        Rthandler.setFormatter(formatter)
        self.log.addHandler(Rthandler)
        self.log.setLevel(logging.INFO)

    def warn(self,msg):
        self.log.warn(msg)

    def error(self,msg):
        self.log.error(msg)

    def info(self,msg):
        self.log.info(msg)

