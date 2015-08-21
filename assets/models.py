# -*- coding: utf-8 -*-
from django.db import models

class asset(models.Model):
    name = models.CharField(verbose_name='资产名', max_length=30, blank=False)
    assets_type = models.CharField(verbose_name='资产型号', max_length=30)
    assets_code = models.CharField(verbose_name='资产编号', max_length=30)
    status = models.CharField(verbose_name='发放状态', max_length=6, default='未发放')
    comment = models.CharField(verbose_name='备注', max_length=256)
    add_time = models.DateTimeField(verbose_name='入库时间', auto_now_add=True)

class user(models.Model):
    name = models.CharField(verbose_name='员工名', max_length=30, blank=False)
    department = models.CharField(verbose_name='部门', max_length=30, blank=False)
    assets = models.CharField(verbose_name='拥有的资产', max_length=128, blank=False)
    comment = models.CharField(verbose_name='备注', max_length=256)
    modify_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    assets_id = models.CharField(verbose_name='拥有的资产ID', max_length=30)

class log(models.Model):
    comment = models.CharField(verbose_name='备注', max_length=256)
    add_time = models.DateTimeField(verbose_name='记录时间', auto_now_add=True)


