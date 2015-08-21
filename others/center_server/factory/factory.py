#coding=utf-8
from twisted.internet.protocol import Factory, Protocol, ClientFactory
from twisted.internet import threads
# from twisted.protocols.basic import LineReceiver
from conf.config import factory,server,SECRET_KEY
# from libs.log import logger
import time,os,yaml
from twisted.internet import reactor
from libs import crypt
from libs.log_mod import logger
logger = logger()
# from lib.data_analysis import ProtoControl
# from lib.c_include import *
# from orm.factorywork import server_info_save, load_history_online, workRegos, workLostClient,query_device, check_online
# from conf.epconfig import EPConfig, MServerConfig,ZS_SERVER


# from zope.interface import implements
# from twisted.cred import portal, checkers
# from twisted.python import filepath
# from twisted.protocols import ftp
# from twisted.internet import task
# from monitorthread import monitor_thread_start, monitor_job_put
# import thread
# from monitor.thread_pool import thread_pool_start


class server_protocol(Protocol):

    def __init__(self):
        self.recvBuf = ""
        self.online_num = {}
        self.oid = None

    def connectionMade(self):
        """
        #第一次连接时需要做的事情
        """
        ip = self.transport.getPeer().host
        if not ip in server['allow']:
            """
            禁IP
            """
            not_allow = 'The IP (%s) not allow' % ip
            logger.error(not_allow)
            msg = crypt.strong_encrypt(SECRET_KEY,not_allow)
            self.transport.write(msg)
	    self.transport.loseConnection()
            # logger.info('The IP (%s) not allow' % ip)
        # else:
        #     self.factory.clientips.append(ip)
        #     self.factory.client_map[ip] = self
            # logger.info('Client connect %s' % ip)


    # def sendDataNoProtaol(self, data):
    #     """
    #     数据发送不处理
    #     """
    #     logger.debug('发送数据(%s)' % len(data))
    #     # outdata = data_analysis.sendData(callid, data)
    #     outdata = data
    #     self.transport.write(outdata)
    #
    # def sendData(self, data):
    #     """
    #     数据协议封包处理后发送
    #     """
    #
    #     s = data.get('act',None)
    #     if s == "heartbeat" or s == "graph_view":
    #         pass
    #     else:
    #         # logger.debug(data)
    #     data = ProtoControl.sendData(data)
    #     self.transport.write(data)

    # def sendError(self, m):
    #     msg = {"code":2,"msg":m ,"act":"sendError"}
    #     self.sendData(msg)
    #     self.transport.loseConnection()

    def dataReceived(self, data):
        try:
            data = crypt.strong_decrypt(SECRET_KEY,str(data))
            print data
            data = eval(data)
	    print data
            if data.get('salt') == 1:
                result = self.factory.call_saltstack(data)
                result = crypt.strong_encrypt(SECRET_KEY,str(result))
                self.transport.write(result)
            else:
                pass
        except Exception, e:
            print e



    def connectionLost(self, reason):
        # try:
        #     os.remove(EPConfig['PID_FILE'])
        # except OSError, e:
        #     logger.info("Not find pid file")
        print self.transport.client, 'disconnected'
        # logger.info("---Client--connectionLost===>%s" % reason)



    # def InvokeAction(self,data):
    #     """
    #     命令调度
    #     """
    #     act = data.get('act')
    #
    #     if act == 'regos':
    #         #注册处理
    #         self.oid = data['oid']
    #         self.factory.addClient(self, data)
    #         self.factory.execRego(data)
    #
    #     elif act == 'heartbeat':
    #         #心跳处理
    #         self.factory.addClient(self, data)
    #         self.factory.execHeartBeat(data)



# class EPClientFactory(ClientFactory):
#     protocol = EPProtocolGame
#     clientips = []
#     def clientConnectionLost(self, connector, reason):
#         logger.debug('connection lost:%s' % reason.getErrorMessage())
#         logger.debug("10s later reconnect")
#         reactor.callLater(10, connector.connect)
#
#
#     def clientConnectionFailed(self, connector, reason):
#         logger.debug('connection failed:%s' % reason.getErrorMessage())
#         logger.debug("10s later reconnect")
#         reactor.callLater(10, connector.connect)


class server_factory(Factory):
    protocol = server_protocol
    #本系统最大允许10000人同时在线
    max_connections = factory['max_connections']
    timeout = factory['timeout']
    perdefer = factory['perdefer'] #每个进程运行的子线程数

    def __init__(self):
        pass

    def call_saltstack(self,data):
        import salt.client
        client = salt.client.LocalClient()
        act = data.get('act')
        hosts = data.get('hosts')
        argv = data.get('argv')
        result = client.cmd(hosts,act,argv)
        if len(hosts.split(',')) > 1:
            result = client.cmd(hosts,act,argv,expr_form='list')
        else:
            result = client.cmd(hosts,act,argv)
        return result
	

