# -*- coding: utf-8 -*-
from django.db import models

class saltstack_state(models.Model):
    center_server = models.CharField(verbose_name='中心服务器', max_length=32, blank=False)
    name = models.CharField(verbose_name='模块名', max_length=32, blank=False)
    content = models.CharField(verbose_name='模块内容', max_length=1024, blank=False)

class saltstack_top(models.Model):
    center_server = models.CharField(verbose_name='中心服务器', max_length=32, blank=False)
    target = models.CharField(verbose_name='应用目标', max_length=512, blank=False)
    state = models.CharField(verbose_name='模块', max_length=512, blank=False)

class saltstack_pillar(models.Model):
    center_server = models.CharField(verbose_name='中心服务器', max_length=32, blank=False)
    name = models.CharField(verbose_name='模块名', max_length=32, blank=False)
    content = models.CharField(verbose_name='模块内容', max_length=1024, blank=False)
