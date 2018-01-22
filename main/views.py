# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.log import logger
from django.contrib import auth
from django.contrib.auth.decorators import login_required

@login_required
def main(request):
    path = request.path.split('/')[1]
    return render(request,'public/index.html',{'user':request.user.first_name,
                                                   'path1':path,
                                                   'page_name1':u'主页'})