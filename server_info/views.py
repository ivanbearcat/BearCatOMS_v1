# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from django.utils.log import logger
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from server_info.models import table
from libs.check_perm import check_permission
import json

@login_required
def server_info_table(request):
    # if not request.user.has_perm('server_info.can_view'):
    #     return render(request,'public/no_passing.html')
    path = request.path.split('/')[1]
    return render(request,'server_info/server_info_table.html',{'user':request.user.username,
                                                               'path1':'server_info',
                                                               'path2':path,
                                                               'page_name1':u'服务器信息',
                                                               'page_name2':u'服务器信息表'})



@login_required
def server_info_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['IDC','position','application','external_IP','inner_IP_1','inner_IP_2','manage_IP','root_pass',
            'ubuntu_pass','comment_1','comment_2','comment_3','comment_4','id']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = table.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.all().count()
        else:
            result_data = table.objects.filter(Q(application__contains=sSearch) | \
                                               Q(external_IP__contains=sSearch) | \
                                               Q(inner_IP_1__contains=sSearch) | \
                                               Q(inner_IP_2__contains=sSearch) | \
                                               Q(manage_IP__contains=sSearch) | \
                                               Q(comment_1__contains=sSearch) | \
                                               Q(comment_2__contains=sSearch) | \
                                               Q(comment_3__contains=sSearch) | \
                                               Q(comment_4__contains=sSearch) | \
                                               Q(id__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(Q(application__contains=sSearch) | \
                                               Q(external_IP__contains=sSearch) | \
                                               Q(inner_IP_1__contains=sSearch) | \
                                               Q(inner_IP_2__contains=sSearch) | \
                                               Q(manage_IP__contains=sSearch) | \
                                               Q(comment_1__contains=sSearch) | \
                                               Q(comment_2__contains=sSearch) | \
                                               Q(comment_3__contains=sSearch) | \
                                               Q(comment_4__contains=sSearch) | \
                                               Q(id__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = table.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.all().count()
        else:
            result_data = table.objects.filter(Q(application__contains=sSearch) | \
                                               Q(external_IP__contains=sSearch) | \
                                               Q(inner_IP_1__contains=sSearch) | \
                                               Q(inner_IP_2__contains=sSearch) | \
                                               Q(manage_IP__contains=sSearch) | \
                                               Q(comment_1__contains=sSearch) | \
                                               Q(comment_2__contains=sSearch) | \
                                               Q(comment_3__contains=sSearch) | \
                                               Q(comment_4__contains=sSearch) | \
                                               Q(id__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = table.objects.filter(Q(application__contains=sSearch) | \
                                               Q(external_IP__contains=sSearch) | \
                                               Q(inner_IP_1__contains=sSearch) | \
                                               Q(inner_IP_2__contains=sSearch) | \
                                               Q(manage_IP__contains=sSearch) | \
                                               Q(comment_1__contains=sSearch) | \
                                               Q(comment_2__contains=sSearch) | \
                                               Q(comment_3__contains=sSearch) | \
                                               Q(comment_4__contains=sSearch) | \
                                               Q(id__contains=sSearch)).count()
    for i in  result_data:
        aaData.append({
                       '0':i.IDC,
                       '1':i.position,
                       '2':i.application,
                       '3':i.external_IP,
                       '4':i.inner_IP_1,
                       '5':i.inner_IP_2,
                       '6':i.manage_IP,
                       '7':i.root_pass,
                       '8':i.ubuntu_pass,
                       '9':i.comment_1,
                       '10':i.comment_2,
                       '11':i.comment_3,
                       '12':i.comment_4,
                       '13':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")



@login_required
def server_info_save(request):
    _id = request.POST.get('id')
    IDC = request.POST.get('IDC')
    position = request.POST.get('position')
    application = request.POST.get('application')
    external_IP = request.POST.get('external_IP')
    inner_IP_1 = request.POST.get('inner_IP_1')
    inner_IP_2 = request.POST.get('inner_IP_2')
    manage_IP = request.POST.get('manage_IP')
    root_pass = request.POST.get('root_pass')
    ubuntu_pass = request.POST.get('ubuntu_pass')
    comment_1 = request.POST.get('comment_1')
    comment_2 = request.POST.get('comment_2')
    comment_3 = request.POST.get('comment_3')
    comment_4 = request.POST.get('comment_4')

    if _id =='':
        orm = table(IDC=IDC,position=position,application=application,external_IP=external_IP,inner_IP_1=inner_IP_1,
                    inner_IP_2=inner_IP_2,manage_IP=manage_IP,root_pass=root_pass,ubuntu_pass=ubuntu_pass,
                    comment_1=comment_1,comment_2=comment_2,comment_3=comment_3,comment_4=comment_4)
    else:
        orm = table.objects.get(id=int(_id))
        orm.IDC = IDC
        orm.position = position
        orm.application = application
        orm.external_IP = external_IP
        orm.inner_IP_1 = inner_IP_1
        orm.inner_IP_2 = inner_IP_2
        orm.manage_IP = manage_IP
        orm.root_pass = root_pass
        orm.ubuntu_pass = ubuntu_pass
        orm.comment_1 = comment_1
        orm.comment_2 = comment_2
        orm.comment_3 = comment_3
        orm.comment_4 = comment_4
    try:
        orm.save()
        return HttpResponse(json.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(json.dumps({'code':1,'msg':str(e)}),content_type="application/json")




@login_required
def server_info_del(request):
    _id = request.POST.get('id')
    orm = table.objects.get(id=_id)

    try:
        orm.delete()
        return HttpResponse(json.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
    except Exception,e:
        return HttpResponse(json.dumps({'code':1,'msg':str(e)}),content_type="application/json")