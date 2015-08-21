# -*- coding: utf-8 -*-
from django.db import models

class upload_files(models.Model):
    file_name = models.CharField(verbose_name='文件名', max_length=64, blank=False)
    file_size = models.IntegerField(verbose_name='文件大小', blank=False)
    upload_time = models.DateTimeField(verbose_name='上传时间', auto_now_add=True )
    upload_user = models.CharField(verbose_name='上传人', max_length=32, blank=False)

class server_list(models.Model):
    server_name = models.CharField(verbose_name='服务器名', max_length=32, blank=False, unique=True)
    ip = models.CharField(verbose_name='IP', max_length=64, blank=False)
    os = models.CharField(verbose_name='系统', max_length=64, blank=False)
    belong_to = models.CharField(verbose_name='属于哪个服务器', max_length=64, blank=False)
    status = models.BooleanField(verbose_name='状态')

class server_group_list(models.Model):
    server_group_name = models.CharField(verbose_name='服务器组名', max_length=32, blank=False, unique=True)
    members_server = models.CharField(verbose_name='成员服务器', max_length=512, blank=False)
    comment = comment = models.CharField(verbose_name='备注', max_length=128)