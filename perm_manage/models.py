# -*- coding: utf-8 -*-
from django.db import models

class perm(models.Model):
    username = models.CharField(verbose_name='用户名', max_length=32, blank=False, unique=True)
    name = models.CharField(verbose_name='姓名',max_length=32)
    web_perm = models.CharField(verbose_name='网页权限',max_length=256)
    server_password = models.TextField(verbose_name='服务器密码')
    server_groups = models.CharField(verbose_name='服务器组',max_length=64)
    server_password_expire = models.CharField(verbose_name='服务器密码过期时间',max_length=32, blank=True)

class server_group_list(models.Model):
    server_group_name = models.CharField(verbose_name='服务器组名', max_length=32, blank=False, unique=True)
    members_server = models.CharField(verbose_name='成员服务器', max_length=512, blank=False)
    comment = comment = models.CharField(verbose_name='备注', max_length=128)
