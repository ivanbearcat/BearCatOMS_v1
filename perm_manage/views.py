# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect,HttpResponse
from django.utils.log import logger
from django.contrib.auth.decorators import login_required
from perm_manage.models import server_group_list,perm
from django.contrib.auth.models import User
from operation.models import server_list
from django.db.models.query_utils import Q
from BearCatOMS.settings import BASE_DIR,SECRET_KEY
from libs import crypt
import simplejson,datetime,re


@login_required
def user_perm(request):
    if not request.user.is_superuser:
        return render_to_response('public/no_passing.html')
    path = request.path.split('/')[1]
    return render_to_response('perm_manage/user_perm.html',{'user':request.user.username,
                                                           'path1':'perm_manage',
                                                           'path2':path,
                                                           'page_name1':u'权限管理',
                                                           'page_name2':u'用户权限管理',})

@login_required
def user_perm_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['username','name',None,None,'server_groups','server_password_expire']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = perm.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = perm.objects.all().count()
        else:
            result_data = perm.objects.filter(Q(username__contains=sSearch) | \
                                               Q(name__contains=sSearch) | \
                                               Q(web_perm__contains=sSearch) | \
                                               Q(server_groups__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = perm.objects.filter(Q(username__contains=sSearch) | \
                                                 Q(name__contains=sSearch) | \
                                                 Q(web_perm__contains=sSearch) | \
                                                 Q(server_groups__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = perm.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = perm.objects.all().count()
        else:
            result_data = perm.objects.filter(Q(username__contains=sSearch) | \
                                               Q(name__contains=sSearch) | \
                                               Q(web_perm__contains=sSearch) | \
                                               Q(server_groups__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = perm.objects.filter(Q(username__contains=sSearch) | \
                                                 Q(name__contains=sSearch) | \
                                                 Q(web_perm__contains=sSearch) | \
                                                 Q(server_groups__contains=sSearch)).count()

    for i in  result_data:
        aaData.append({
                       '0':i.username,
                       '1':i.name,
                       '2':i.web_perm,
                       '3':i.server_password,
                       '4':str(i.server_password_expire),
                       '5':i.server_groups,
                       '6':i.id,
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def user_perm_dropdown(request):
    _id = request.POST.get('id')
    server_groups = request.POST.get('server_groups')
    web_perm = request.POST.get('web_perm')
    result = {}
    result['username_list'] = []
    result['username_edit'] = ''
    result['web_perm_list'] = []
    result['web_perm_edit'] = []
    result['server_groups_list'] = []
    result['server_groups_edit'] = []
    count = 0
    if not _id == None:
        orm = perm.objects.get(id=_id)
        result['username_edit'] = {'text':orm.username}
        if web_perm:
            for i in orm.web_perm.split(','):
                result['web_perm_edit'].append({'text':i,'id':count})
                count += 1
        if server_groups:
            for i in orm.server_groups.split(','):
                orm_server_groups = server_group_list.objects.get(server_group_name=i)
                result['server_groups_edit'].append({'text':i,'id':orm_server_groups.id})
    orm_User = User.objects.all()
    for i in orm_User:
        result['username_list'].append({'text':i.username,'id':i.id})
    sidebar_list = []
    sidebar_list.append('所有权限')
    with open(BASE_DIR + '/templates/public/sidebar.html') as f:
        line = f.readline()
        while line:
            data = re.search(r'name=".*"',line)
            if data:
                data = data.group().replace('"','')
                sidebar_list.append(data.replace('name=',''))
            line = f.readline()
    for i in sidebar_list:
        result['web_perm_list'].append({'text':i,'id':count})
        count += 1
    orm_server_group = server_group_list.objects.all()
    for i in orm_server_group:
        result['server_groups_list'].append({'text':i.server_group_name,'id':i.id})
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def user_perm_save(request):
    _id = request.POST.get('id')
    username = request.POST.get('username')
    name = request.POST.get('name')
    web_perm = request.POST.get('web_perm')
    # server_password = request.POST.get('server_password')
    server_groups = request.POST.get('server_groups')
    three_months_later = datetime.datetime.now()+datetime.timedelta(91)
    aes = crypt.crypt_aes(SECRET_KEY[:32])
    # server_password = aes.encrypt_aes(server_password)
    try:
        if _id =='':
            # if server_password:
            #     perm.objects.create(username=username,name=name,web_perm=web_perm,server_password=server_password,server_groups=server_groups,\
            #                         server_password_expire=three_months_later.strftime('%Y-%m-%d'))
            # else:
            #     perm.objects.create(username=username,name=name,web_perm=web_perm,server_password=server_password,server_groups=server_groups)
            perm.objects.create(username=username,name=name,web_perm=web_perm,server_groups=server_groups)

        else:
            orm = perm.objects.get(id=_id)
            orm.username = username
            orm.name = name
            orm.web_perm = web_perm
            # if server_password:
            #     orm.server_password = server_password
            orm.server_groups = server_groups
            orm.save()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def user_perm_del(request):
    _id = request.POST.get('id')
    try:
        orm = perm.objects.get(id=_id)
        orm.delete()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
    except Exception,e:
        return HttpResponse(simplejson.dumps({'code':1,'msg':e}),content_type="application/json")

@login_required
def server_group(request):
    if not request.user.is_superuser:
        return render_to_response('public/no_passing.html')
    path = request.path.split('/')[1]
    return render_to_response('perm_manage/server_group.html',{'user':request.user.username,
                                                           'path1':'perm_manage',
                                                           'path2':path,
                                                           'page_name1':u'权限管理',
                                                           'page_name2':u'服务器组管理'})
@login_required
def server_group_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['server_group_name','members_server','comment']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = server_group_list.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = server_group_list.objects.all().count()
        else:
            result_data = server_group_list.objects.filter(Q(server_group_name__contains=sSearch) | \
                                               Q(members_server__contains=sSearch) | \
                                               Q(comment__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = server_group_list.objects.filter(Q(server_group_name__contains=sSearch) | \
                                                 Q(members_server__contains=sSearch) | \
                                                 Q(comment__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = server_group_list.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = server_group_list.objects.all().count()
        else:
            result_data = server_group_list.objects.filter(Q(server_group_name__contains=sSearch) | \
                                               Q(members_server__contains=sSearch) | \
                                               Q(comment__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = server_group_list.objects.filter(Q(server_group_name__contains=sSearch) | \
                                                 Q(members_server__contains=sSearch) | \
                                                 Q(comment__contains=sSearch)).count()

    for i in  result_data:
        aaData.append({
                       '0':i.server_group_name,
                       '1':i.members_server,
                       '2':i.comment,
                       '3':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def server_group_save(request):
    _id = request.POST.get('id')
    comment = request.POST.get('comment')
    server_group_name = request.POST.get('server_group_name')
    members_server = request.POST.get('members_server')

    try:
        if _id =='':
            server_group_list.objects.create(server_group_name=server_group_name,members_server=members_server,comment=comment)
        else:
            orm = server_group_list.objects.get(id=_id)
            orm.server_group_name = server_group_name
            orm.members_server = members_server
            orm.comment = comment
            orm.save()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def server_group_dropdown(request):
    _id = request.POST.get('id')
    result = {}
    result['list'] = []
    result['edit'] = []
    if not _id == None:
        orm = server_group_list.objects.get(id=_id)
        for i in orm.members_server.split(','):
            orm_server = server_list.objects.get(server_name=i)
            result['edit'].append({'text':i,'id':orm_server.id})
    result_data = server_list.objects.all()
    for i in result_data:
        result['list'].append({'text':i.server_name,'id':i.id})
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def server_group_del(request):
    _id = request.POST.get('id')
    try:
        orm = server_group_list.objects.get(id=_id)
        orm_user_perm = perm.objects.all()
        for i in orm_user_perm:
            if orm.server_group_name in i.server_groups.split(','):
                return HttpResponse(simplejson.dumps({'code':1,'msg':u'无法删除已经被分配的主机组'}),content_type="application/json")
        orm.delete()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
    except Exception,e:
        return HttpResponse(simplejson.dumps({'code':1,'msg':e}),content_type="application/json")