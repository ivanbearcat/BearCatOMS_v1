#!/usr/bin/env python
#coding=utf-8
# from twisted.internet import epollreactor
# try:
#     epollreactor.install()
# except:
#     pass
from twisted.internet import reactor
from signal import SIGTERM
from factory.factory import server_factory
from twisted.internet.error import CannotListenError
# from libs.log import logger
from conf.config import server
import os,sys,atexit,psutil

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

__pid__ = os.path.abspath(os.path.dirname(__file__)) + '/logs/center_server.pid'
def start():
    def start_daemon():
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError, e:
            # logger.debug(sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror))
            sys.exit(1)
        os.setsid()
        os.umask(0)
        try:
            pid = os.fork()
            if pid > 0:
                print "Service Start on PID %d" % pid
                with open(__pid__, 'w') as f:
                    f.write(str(pid))
                sys.exit(0)

        except OSError, e:
            # logger.debug(sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror))
            sys.exit(1)

    def del_pid():
        if os.path.exists(__pid__):
            os.remove(__pid__)

    if os.path.exists(__pid__):
        f = open(__pid__, 'r')
        pid = int(f.read())
        f.close()
        if psutil.pid_exists(pid):
            print "Service is already Start!"
            sys.exit(0)
        else:
            start_daemon()
    else:
        start_daemon()
    atexit.register(del_pid)
    main()

def stop():
    if not os.path.exists(__pid__):
        print "Service has Not been Started !"

    else:
        try:
            with open(__pid__, 'r') as f:
                pid = int(f.read())
                os.kill(pid, SIGTERM)
            os.remove(__pid__)
        except OSError:
            pass
        print "Service Stoped"




def restart():
    stop()
    import time
    time.sleep(3)
    start()


def main():
    """
    程序入口
    """
    try:
        reactor.listenTCP(server['port'], server_factory())
        reactor.suggestThreadPoolSize(server['suggestThreadPoolSize'])
        reactor.run()
        # logger.info("\033[32;1mRunning Socket on %s:%s\033[0m" % ("", str(MServerConfig['SERVE_PORT'])))
    except CannotListenError:
        # logger.info("\033[31;1mSocket %s  Address already in use.\033[0m" % str(MServerConfig['SERVE_PORT']))
        # print ''
        sys.exit(1)


if __name__ == '__main__':

    root_dir = os.path.abspath(os.path.dirname(__file__))
    os.chdir(root_dir)
    if len(sys.argv) >= 2:
        if 'start' == sys.argv[1]:
            start()
            sys.exit(0)
        elif 'stop' == sys.argv[1]:
            stop()
            sys.exit(0)
        elif "restart" == sys.argv[1]:
            restart()
            sys.exit(0)
        elif "help" == sys.argv[1]:
            print "usage: python center_server.py start|stop|restart|help"
            sys.exit(0)
        else:
            print """Unknown option: %s
"usage: python center_server.py start|stop|restart|help""" % ' '.join(sys.argv[1:])
            sys.exit(0)
        sys.exit(0)
    else:
        main()