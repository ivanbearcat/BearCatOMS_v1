# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from django.utils.log import logger
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from assets.models import asset,user,log
from libs.check_perm import check_permission
import json

@login_required
def assets_asset(request):
    flag = check_permission(u'资产出入库',request.user.username)
    if flag < 1:
        return render(request,'public/no_passing.html')
    path = request.path.split('/')[1]
    return render(request,'assets/assets_asset.html',{'user':request.user.username,
                                                           'path1':'assets',
                                                           'path2':path,
                                                           'page_name1':u'资产管理',
                                                           'page_name2':u'资产出入库'})

@login_required
def assets_asset_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['name','assets_type','assets_code','status','comment','add_time','id']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = asset.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = asset.objects.all().count()
        else:
            result_data = asset.objects.filter(Q(name__contains=sSearch) | \
                                               Q(assets_type__contains=sSearch) | \
                                               Q(assets_code__contains=sSearch) | \
                                               Q(comment__contains=sSearch) | \
                                               Q(status__contains=sSearch) | \
                                               Q(id__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = asset.objects.filter(Q(name__contains=sSearch) | \
                                                 Q(assets_type__contains=sSearch) | \
                                                 Q(assets_code__contains=sSearch) | \
                                                 Q(comment__contains=sSearch) | \
                                                 Q(status__contains=sSearch) | \
                                                 Q(id__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = asset.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = asset.objects.all().count()
        else:
            result_data = asset.objects.filter(Q(name__contains=sSearch) | \
                                               Q(assets_type__contains=sSearch) | \
                                               Q(assets_code__contains=sSearch) | \
                                               Q(comment__contains=sSearch) | \
                                               Q(status__contains=sSearch) | \
                                               Q(id__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = asset.objects.filter(Q(name__contains=sSearch) | \
                                                 Q(assets_type__contains=sSearch) | \
                                                 Q(assets_code__contains=sSearch) | \
                                                 Q(comment__contains=sSearch) | \
                                                 Q(status__contains=sSearch) | \
                                                 Q(id__contains=sSearch)).count()
    for i in  result_data:
        aaData.append({
                       '0':i.name,
                       '1':i.assets_type,
                       '2':i.assets_code,
                       '3':i.comment,
                       '4':i.status,
                       '5':str(i.add_time).split('+')[0],
                       '6':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")

@login_required
def assets_asset_save(request):
    _id = request.POST.get('id')
    assets_type = request.POST.get('assets_type')
    comment = request.POST.get('comment')
    assets_code = request.POST.get('assets_code')
    name = request.POST.get('name')

    if _id =='':
        orm = asset(name=name,assets_type=assets_type,assets_code=assets_code,comment=comment)
        comment_info = u'%s %s %s 入库' % (name,assets_type,assets_code)
        orm_log = log(comment=comment_info)
    else:
        orm = asset.objects.get(id=int(_id))
        orm.name = name
        orm.assets_type = assets_type
        orm.assets_code = assets_code
        orm.comment = comment
        comment_info = u'%s %s %s 编辑' % (name,assets_type,assets_code)
        orm_log = log(comment=comment_info)

    try:
        orm_log.save()
        orm.save()
        return HttpResponse(json.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e,comment)
        return HttpResponse(json.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def assets_asset_del(request):
    _id = request.POST.get('id')
    orm = asset.objects.get(id=_id)
    if orm.status == u'已发放':
        return HttpResponse(json.dumps({'code':2,'msg':u'该物品已被发放，请收回后再删除'}),content_type="application/json")
    else:
        comment_info = u'%s %s %s 出库' % (orm.name,orm.assets_type,orm.assets_code)
        orm_log = log(comment=comment_info)
        try:
            orm_log.save()
            orm.delete()
            return HttpResponse(json.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
        except Exception,e:
            return HttpResponse(json.dumps({'code':1,'msg':str(e)}),content_type="application/json")




@login_required
def assets_user(request):
    flag = check_permission(u'员工资产',request.user.username)
    if flag < 1:
        return render(request,'public/no_passing.html')
    path = request.path.split('/')[1]
    return render(request,'assets/assets_user.html',{'user':request.user.username,
                                                           'path1':'assets',
                                                           'path2':path,
                                                           'page_name1':u'资产管理',
                                                           'page_name2':u'员工资产'})

@login_required
def assets_user_dropdown(request):
    _id = request.POST.get('id')
    result = {}
    result['list'] = []
    result['edit'] = []
    if not _id == None:
        orm = user.objects.get(id=_id)
        for i in orm.assets_id.split(','):
            orm_assets = asset.objects.get(id=i)
            result['edit'].append({'text':orm_assets.name + ' ' + orm_assets.assets_type + ' ' + orm_assets.assets_code,'id':orm_assets.id})
    result_data = asset.objects.filter(status=u'未发放')
    for i in result_data:
        result['list'].append({'text':i.name + ' ' + i.assets_type + ' ' + i.assets_code,'id':i.id})
    return HttpResponse(json.dumps(result),content_type="application/json")



@login_required
def assets_user_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['name','department','assets','comment','modify_time','id']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = user.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = user.objects.all().count()
        else:
            result_data = user.objects.filter(Q(name__contains=sSearch) | \
                                               Q(department__contains=sSearch) | \
                                               Q(assets__contains=sSearch) | \
                                               Q(comment__contains=sSearch) | \
                                               Q(id__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = user.objects.filter(Q(name__contains=sSearch) | \
                                                 Q(department__contains=sSearch) | \
                                                 Q(assets__contains=sSearch) | \
                                                 Q(comment__contains=sSearch) | \
                                                 Q(id__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = user.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = user.objects.all().count()
        else:
            result_data = user.objects.filter(Q(name__contains=sSearch) | \
                                               Q(department__contains=sSearch) | \
                                               Q(assets__contains=sSearch) | \
                                               Q(comment__contains=sSearch) | \
                                               Q(id__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = user.objects.filter(Q(name__contains=sSearch) | \
                                                 Q(department__contains=sSearch) | \
                                                 Q(assets__contains=sSearch) | \
                                                 Q(comment__contains=sSearch) | \
                                                 Q(id__contains=sSearch)).count()

    for i in  result_data:
        aaData.append({
                       '0':i.name,
                       '1':i.department,
                       '2':i.assets,
                       '3':i.comment,
                       '4':str(i.modify_time).split('+')[0],
                       '5':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")

@login_required
def assets_user_save(request):
    _id = request.POST.get('id')
    department = request.POST.get('department')
    comment = request.POST.get('comment')
    assets = request.POST.get('asset')
    name = request.POST.get('name')
    assets_data = ''

    try:
        if _id =='':
            for i in assets.split(','):
                orm_assets = asset.objects.get(id=i)
                orm_assets.status = '已发放'
                orm_assets.save()
                comment_info = u'%s %s %s 出库，发放给<%s>' % (orm_assets.name,orm_assets.assets_type,orm_assets.assets_code,name)
                orm_log = log(comment=comment_info)
                orm_log.save()
            if assets_data == '':
                assets_data = '< %s %s %s >' % (orm_assets.name,orm_assets.assets_type,orm_assets.assets_code)
            else:
                assets_data = '%s< %s %s %s >' % (assets_data,orm_assets.name,orm_assets.assets_type,orm_assets.assets_code)
            orm_user = user(name=name,department=department,assets=assets_data,comment=comment,assets_id=assets)
            orm_user.save()
        else:
            orm = user.objects.get(id=_id)
            for i in orm.assets_id.split(','):
                if not i in assets.split(','):
                    orm_assets = asset.objects.get(id=i)
                    orm_assets.status = '未发放'
                    orm_assets.save()
                    comment_info = u'%s %s %s 入库库，从<%s>处收回' % (orm_assets.name,orm_assets.assets_type,orm_assets.assets_code,name)
                    orm_log = log(comment=comment_info)
                    orm_log.save()
            for i in assets.split(','):
                if not i in orm.assets_id.split(','):
                    orm_assets = asset.objects.get(id=i)
                    orm_assets.status = '已发放'
                    orm_assets.save()
                    comment_info = u'%s %s %s 出库，发放给<%s>' % (orm_assets.name,orm_assets.assets_type,orm_assets.assets_code,name)
                    orm_log = log(comment=comment_info)
                    orm_log.save()
            if assets_data == '':
                assets_data = '< %s %s %s >' % (orm_assets.name,orm_assets.assets_type,orm_assets.assets_code)
            else:
                assets_data = '%s< %s %s %s >' % (assets_data,orm_assets.name,orm_assets.assets_type,orm_assets.assets_code)
            orm.name = name
            orm.department = department
            orm.assets = assets_data
            orm.comment = comment
            orm.assets_id = assets
            orm.save()
        return HttpResponse(json.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e,comment)
        return HttpResponse(json.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def assets_user_del(request):
    _id = request.POST.get('id')
    try:
        orm = user.objects.get(id=_id)
        for i in orm.assets_id.split(','):
            orm_assets = asset.objects.get(id=i)
            orm_assets.status = "未发放"
            orm_assets.save()
            comment_info = u'%s %s %s 入库，从<%s>处收回' % (orm_assets.name,orm_assets.assets_type,orm_assets.assets_code,orm.name)
            orm_log = log(comment=comment_info)
            orm_log.save()
        orm.delete()
        return HttpResponse(json.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
    except Exception,e:
        return HttpResponse(json.dumps({'code':0,'msg':e}),content_type="application/json")

@login_required
def assets_log(request):
    flag = check_permission(u'出入库记录',request.user.username)
    if flag < 1:
        return render(request,'public/no_passing.html')
    path = request.path.split('/')[1]
    return render(request,'assets/assets_log.html',{'user':request.user.username,
                                                           'path1':'assets',
                                                           'path2':path,
                                                           'page_name1':u'资产管理',
                                                           'page_name2':u'出入库记录'})

@login_required
def assets_log_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['comment','add_time','id']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = log.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = log.objects.all().count()
        else:
            result_data = log.objects.filter(Q(comment__contains=sSearch) | \
                                               Q(id__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = log.objects.filter(Q(comment__contains=sSearch) | \
                                                 Q(id__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = log.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = log.objects.all().count()
        else:
            result_data = log.objects.filter(Q(comment__contains=sSearch) | \
                                               Q(id__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = log.objects.filter(Q(comment__contains=sSearch) | \
                                                 Q(id__contains=sSearch)).count()
    for i in  result_data:
        aaData.append({
                       '0':i.comment,
                       '1':str(i.add_time).split('+')[0],
                       '2':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")

@login_required
def assets_image(request):
    flag = check_permission(u'资产统计图',request.user.username)
    if flag < 1:
        return render(request,'public/no_passing.html')
    path = request.path.split('/')[1]
    return render(request,'assets/assets_image.html',{'user':request.user.username,
                                                           'path1':'assets',
                                                           'path2':path,
                                                           'page_name1':u'资产管理',
                                                           'page_name2':u'资产统计图'})

@login_required
def assets_get_data(request):
    orm = {}
    assets_list = []
    orm['data'] = []
    num = 0
    not_info = []
    already_info = []
    all_info = []
    orm['not'] = asset.objects.filter(status='未发放').count()
    orm['already'] = asset.objects.filter(status='已发放').count()
    orm['all'] = asset.objects.all().count()

    for i in asset.objects.all():
        assets_list.append(i.name)
    assets_list_uniq = list(set(assets_list))
    for i in assets_list_uniq:
        not_info.append(asset.objects.filter(name=i).filter(status='未发放').count())
        already_info.append(asset.objects.filter(name=i).filter(status='已发放').count())
        all_info.append(asset.objects.filter(name=i).count())

    detail = zip(not_info,already_info,all_info)
    for i in assets_list_uniq:
        orm['data'].append({'name':i, 'data':list(detail[num])})
        num += 1
    return HttpResponse(json.dumps(orm),content_type="application/json")


