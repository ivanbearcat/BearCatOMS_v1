# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect,HttpResponse
from django.utils.log import logger
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from libs.check_perm import check_permission
from libs.socket_send_data import client_send_data
from BearCatOMS.settings import CENTER_SERVER
from saltstack.models import saltstack_state,saltstack_top
import simplejson,os,commands

@login_required
def salt_state(request):
    flag = check_permission(u'state模块定义',request.user.username)
    if flag < 1:
        return render_to_response('public/no_passing.html')
    path = request.path.split('/')[1]
    return render_to_response('saltstack/salt_state.html',{'user':request.user.username,
                                                           'path1':'saltstack',
                                                           'path2':path,
                                                           'page_name1':u'saltstack',
                                                           'page_name2':u'state模块定义'})

def salt_state_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['name','content']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = saltstack_state.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_state.objects.all().count()
        else:
            result_data = saltstack_state.objects.filter(Q(name__contains=sSearch) | \
                                               Q(content__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_state.objects.filter(Q(name__contains=sSearch) | \
                                                 Q(content__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = saltstack_state.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_state.objects.all().count()
        else:
            result_data = saltstack_state.objects.filter(Q(name__contains=sSearch) | \
                                               Q(content__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_state.objects.filter(Q(name__contains=sSearch) | \
                                                 Q(content__contains=sSearch)).count()

    for i in  result_data:
        content = []
        for j in i.content.split('\n'):
            content.append(j+'<br>')
        aaData.append({
                       '0':i.center_server,
                       '1':i.name,
                       '2':''.join(content).replace(' ','&nbsp'),
                       '3':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def salt_state_save(request):
    _id = request.POST.get('id')
    center_server = request.POST.get('center_server')
    name = request.POST.get('name')
    content = request.POST.get('content')

    try:
        if _id =='':
            saltstack_state.objects.create(center_server=center_server,name=name,content=content)
        else:
            orm = saltstack_state.objects.get(id=_id)
            orm.name = name
            orm.content = content
            orm.save()
        dir = commands.getoutput('''ssh %s "grep -A2 '^file_roots' /etc/salt/master |grep 'base:' -A1|grep '-'|awk '{print $3}'"''' % CENTER_SERVER[center_server][0])
        print dir
        # print '''ssh %s "%s/%s;echo '%s' > %s/%s/init.sls"''' % (CENTER_SERVER[center_server][0],dir,name,content,dir,name)
        # os.system('''ssh %s "%s/%s;echo '%s' > %s/%s/init.sls"''' % (CENTER_SERVER[center_server][0],dir,name,content,dir,name))
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def salt_state_dropdown(request):
    result = []
    count = 0
    for i in CENTER_SERVER.keys():
        result.append({'text':i,'id':count})
        count += 1
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def salt_state_del(request):
    try:
        _id = request.POST.get('id')
        orm = saltstack_state.objects.get(id=_id)
        orm.delete()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(simplejson.dumps({'code':1,'msg':u'删除失败'}),content_type="application/json")