#!/usr/bin/env python
#coding:utf-8
from perm_manage.models import perm
from django.utils.log import logger


def check_permission(perm_name,username):
    try:
        flag = 0
        orm = perm.objects.get(username=username)
        for i in orm.web_perm.split(','):
            if perm_name == i or u'所有权限' == i:
                flag += 1
        return flag
    except Exception,e:
        logger.error(e)
        return 0



