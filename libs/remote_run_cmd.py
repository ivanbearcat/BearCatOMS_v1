#!/usr/bin/env python
import paramiko
import os

def r_cmd(hostname,cmd,username='root'):
    paramiko.util.log_to_file('logs/remote_run_cmd.log')
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privatekey = os.path.expanduser('/root/.ssh/id_rsa')
    key = paramiko.RSAKey.from_private_key_file(privatekey)

    ssh.connect(hostname=hostname,username='root',pkey=key)
    stdin,stdout,stderr=ssh.exec_command(cmd)
    ssh.close()
    return stdout.read()

