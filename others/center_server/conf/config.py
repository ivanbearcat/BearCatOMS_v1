#!/usr/bin/env python
#coding=utf-8
server = {}
server['port'] = 7777
server['allow'] = ['127.0.0.1', '192.168.100.151', '192.168.100.42']
server['suggestThreadPoolSize'] = 10

factory = {}
factory['max_connections'] = 5
factory['timeout'] = 3
factory['perdefer'] = 5

SECRET_KEY = '#ioag^zjg!+wq^=x-jum(qz*)*&amp;*h&amp;v@_#@_ks%7l3=dyzqu_t'
