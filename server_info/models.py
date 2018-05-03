# -*- coding: utf-8 -*-
from django.db import models

class table(models.Model):
    IDC = models.CharField(verbose_name='机房', max_length=32, blank=True)
    position = models.CharField(verbose_name='机柜', max_length=32, blank=True)
    application = models.CharField(verbose_name='应用', max_length=128, blank=True)
    external_IP = models.IPAddressField(verbose_name='外部IP', blank=True)
    inner_IP_1 = models.IPAddressField(verbose_name='内部IP_1', blank=True)
    inner_IP_2 = models.IPAddressField(verbose_name='内部IP_2', blank=True)
    manage_IP = models.IPAddressField(verbose_name='内部IP_2', blank=True)
    root_pass = models.CharField(verbose_name='root密码', max_length=32, blank=True)
    ubuntu_pass = models.CharField(verbose_name='ubuntu密码', max_length=32, blank=True)
    comment_1 = models.CharField(verbose_name='备注_1', max_length=128, blank=True)
    comment_2 = models.CharField(verbose_name='备注_2', max_length=128, blank=True)
    comment_3 = models.CharField(verbose_name='备注_3', max_length=128, blank=True)
    comment_4 = models.CharField(verbose_name='备注_4', max_length=128, blank=True)



class domain_name_CRT(models.Model):
    name_server = models.CharField(verbose_name='域名', max_length=32, blank=True)
    apply_time = models.DateField(verbose_name='申请时间', null=True)
    name_server_expiration_time = models.DateField(verbose_name='域名过期时间', null=True)
    CRT_expiration_time = models.DateField(verbose_name='证书过期时间', null=True)
    DNSPOD = models.CharField(verbose_name='DNSPOD', max_length=32, blank=True)
    account = models.CharField(verbose_name='账号', max_length=32, blank=True)
    comment = models.CharField(verbose_name='备注', max_length=32, blank=True)
    ICP = models.CharField(verbose_name='ICP备案号', max_length=32, blank=True)



class service_id(models.Model):
    service_name = models.CharField(verbose_name='服务名', max_length=32, blank=True)
    service_id = models.CharField(verbose_name='服务ID', max_length=16, blank=True)
    service_module = models.CharField(verbose_name='服务模块', max_length=16, blank=True)