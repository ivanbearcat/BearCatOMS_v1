# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.utils.log import logger
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from libs.check_perm import check_permission

@login_required
def nagios(request):
    flag = check_permission(u'nagios',request.user.username)
    if flag < 1:
        return render_to_response('public/no_passing.html')
    path = request.path.split('/')[1]
    return render_to_response('monitor/nagios.html',{'user':request.user.username,
                                                     'path1':'monitor',
                                                     'path2':path,
                                                     'page_name1':u'监控',
                                                     'page_name2':'nagios'})

@login_required
def zabbix(request):
    flag = check_permission(u'zabbix',request.user.username)
    if flag < 1:
        return render_to_response('public/no_passing.html')
    path = request.path.split('/')[1]
    return render_to_response('monitor/zabbix.html',{'user':request.user.username,
                                                     'path1':'monitor',
                                                     'path2':path,
                                                     'page_name1':u'监控',
                                                     'page_name2':'zabbix'})
