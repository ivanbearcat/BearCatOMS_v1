#coding:utf-8
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect,HttpResponse
from django.utils.log import logger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import simplejson,re,datetime,os
from user_manage.models import perm
from operation.models import server_group_list
from django.db.models.query_utils import Q
from BearCatOMS.settings import BASE_DIR,SECRET_KEY
from libs import crypt
from libs.check_perm import check_permission
from libs.server_list_conf import server_lists
from libs.socket_send_data import client_send_data


@login_required
def chpasswd(request):
    flag = check_permission(u'修改密码',request.user.username)
    if flag < 1:
        return render_to_response('public/no_passing.html')
    path = request.path.split('/')[1]
    return render_to_response('user_manage/chpasswd.html',{'user':request.user.username,
                                                           'path1':'user_manage',
                                                           'path2':path,
                                                           'page_name1':u'用户管理',
                                                           'page_name2':u'修改密码',})

@login_required
def post_chpasswd(request):
    password_current = request.POST.get('password_current')
    password_new = request.POST.get('password_new')
    password_new_again = request.POST.get('password_new_again')
    user = User.objects.get(username=request.user.username)
    if not user.check_password(password_current):
        code = 1
        msg = u'当前密码错误'
    elif password_new == '' or password_new_again == '':
        code = 2
        msg = u'新密码不能为空'
    elif not password_new == password_new_again:
        code = 3
        msg = u'新密码不一致'
    else:
        try:
            user.set_password(password_new)
            user.save()
            code = 0
            msg = u'密码修改成功'
        except Exception,e:
            code = 4
            msg = u'密码修改失败'
    return HttpResponse(simplejson.dumps({'code':code,'msg':msg}),content_type="application/json")

@login_required
def post_server_chpasswd(request):
    server_password_current = request.POST.get('server_password_current')
    server_password_new = request.POST.get('server_password_new')
    server_password_new_again = request.POST.get('server_password_new_again')
    orm = perm.objects.get(username=request.user.username)
    three_months_later = datetime.datetime.now()+datetime.timedelta(91)
    aes = crypt.crypt_aes(SECRET_KEY[:32])
    orm_server_password = aes.decrypt_aes(orm.server_password)
    print server_password_current
    print orm_server_password
    if server_password_current != orm_server_password:
        code = 1
        msg = u'当前密码错误'
    elif server_password_new == '' or server_password_new_again == '':
        code = 2
        msg = u'新密码不能为空'
    elif not server_password_new == server_password_new_again:
        code = 3
        msg = u'新密码不一致'
    elif server_password_current == server_password_new:
        code = 4
        msg = u'新密码不能与当前相同'
    else:
        server_password_new = aes.encrypt_aes(server_password_new)
        try:
            if os.system('id %s' % request.user.username):
                code = os.system('useradd -e $(date "+%D" -d "+3 months") ' + request.user.username + ' && echo ' + server_password_new_again + '|passwd --stdin ' + request.user.username)

                if code:
                    return HttpResponse(simplejson.dumps({'code':code,'msg':'密码修改失败'}),content_type="application/json")
            else:
                code = os.system('usermod -e $(date "+%D" -d "+3 months") ' + request.user.username + ' && echo ' + server_password_new_again + '|passwd --stdin ' + request.user.username)
                if code:
                    return HttpResponse(simplejson.dumps({'code':code,'msg':'密码修改失败'}),content_type="application/json")
            for i in server_lists.values():
                os.system('ssh-copy-id -i /home/%s/.ssh/id_rsa.pub root@%s' % (request.user.username,i))
            if os.system('grep logout /home/%s/.bashrc'% request.user.username):
                os.system('echo "python %s %s" >> /home/%s/.bashrc && echo "logout" >> /home/%s/.bashrc' % (BASE_DIR + '/fortress_server.py',request.user.username,request.user.username,request.user.username))
            orm.server_password = server_password_new
            orm.server_password_expire = three_months_later.strftime('%Y-%m-%d')
            orm.save()
            code = 0
            msg = u'密码修改成功'
        except Exception,e:
            code = 5
            msg = u'密码修改失败'
    return HttpResponse(simplejson.dumps({'code':code,'msg':msg}),content_type="application/json")

@login_required
def user_perm(request):
    if not request.user.is_superuser:
        return render_to_response('public/no_passing.html')
    path = request.path.split('/')[1]
    return render_to_response('user_manage/user_perm.html',{'user':request.user.username,
                                                           'path1':'user_manage',
                                                           'path2':path,
                                                           'page_name1':u'用户管理',
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
    server_password = request.POST.get('server_password')
    server_groups = request.POST.get('server_groups')
    three_months_later = datetime.datetime.now()+datetime.timedelta(91)
    aes = crypt.crypt_aes(SECRET_KEY[:32])
    server_password = aes.encrypt_aes(server_password)
    try:
        if _id =='':
            if server_password:
                perm.objects.create(username=username,name=name,web_perm=web_perm,server_password=server_password,server_groups=server_groups,\
                                    server_password_expire=three_months_later.strftime('%Y-%m-%d'))
            else:
                perm.objects.create(username=username,name=name,web_perm=web_perm,server_password=server_password,server_groups=server_groups)

        else:
            orm = perm.objects.get(id=_id)
            orm.username = username
            orm.name = name
            orm.web_perm = web_perm
            if server_password:
                orm.server_password = server_password
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