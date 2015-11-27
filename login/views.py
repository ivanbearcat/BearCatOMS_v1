# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.log import logger
from django.contrib import auth
from Queue import Queue
from django.contrib.auth.decorators import login_required


def login(request):
    return render(request,'login/login.html')

def login_auth(request):
    user_auth = request.POST.get('username')
    passwd_auth = request.POST.get('password')
    authed = auth.authenticate(username=user_auth,password=passwd_auth)
    if authed and authed.is_active:
        auth.login(request,authed)
        # if globals().has_key('next_next') and not next_next == None:
        #     logger.info('<%s> login in sucess.' % user_auth)
        #     next_page = next_next
        #     globals().pop('next_next')
        #     return HttpResponseRedirect(next_page)
        # else:
        #     logger.info('<%s> login in sucess.' % user_auth)
        #     return HttpResponseRedirect('/main/')
        next_page = request.session.get('next')
        if next_page:
            request.session.pop('next')
            print request.session.get('next')
            return HttpResponseRedirect(next_page)
        else:
            return HttpResponseRedirect('/main/')
    else:
        logger.warn('<%s> login in fail.' % user_auth)
        return render(request,'login/login.html',{'msg':u'账号或密码错误'})

def logout(request):
    auth.logout(request)
    return render(request,'login/login.html')

def not_login(request):
    next_next = request.GET.get('next')
    # print next_next
    # global next_next
    request.session['next'] = next_next
    return render(request,'login/login.html',{'msg':u'您还没有登录'})