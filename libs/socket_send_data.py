# -*- coding: utf-8 -*-
from BearCatOMS.settings import SECRET_KEY
from libs import crypt
import socket,time

def client_send_data(cmd,dest,port):
    send_data = crypt.strong_encrypt(SECRET_KEY,cmd)
    addr = (dest,port)
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(addr)
    recv_data = ''
    s.send(send_data)
    try:
        while 1:
            data = s.recv(1024)
            recv_data += data
            s.setblocking(0)
            time.sleep(0.1)
    except Exception:
        pass
    recv_data = crypt.strong_decrypt(SECRET_KEY,str(recv_data))
    s.close()
    return recv_data