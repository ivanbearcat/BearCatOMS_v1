import socket

def check_center_server_up(ip,port):
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((ip,port))
    except socket.error,socket.timeout:
        return False
    else:
        s.close()
        return True