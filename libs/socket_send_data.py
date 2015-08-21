# -*- coding: utf-8 -*-
from BearCatOMS.settings import SECRET_KEY
from libs import crypt
import socket

def client_send_data(cmd,dest,port):
    send_data = crypt.strong_encrypt(SECRET_KEY,cmd)
    addr = (dest,port)
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # s.setblocking(0)
    s.connect(addr)
    s.send(send_data)
    recv_data = s.recv(1024000)
    recv_data = crypt.strong_decrypt(SECRET_KEY,str(recv_data))
    s.close()
    return recv_data