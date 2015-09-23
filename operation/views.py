# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from django.utils.log import logger
from django.contrib.auth.decorators import login_required
import simplejson,re,os,datetime,time,subprocess
from django.db.models.query_utils import Q
from operation.models import upload_files,server_list,command_template
from audit.models import log
from perm_manage.models import perm,server_group_list
from django import forms
from libs.socket_send_data import client_send_data
from libs.str_to_html import convert_str_to_html
from BearCatOMS.settings import BASE_DIR,CENTER_SERVER
from libs.check_perm import check_permission
from gevent import monkey; monkey.patch_socket()
import gevent
from gevent.pool import Pool

@login_required
def upload(request):
    flag = check_permission(u'文件上传',request.user.username)
    if flag < 1:
        return render(request,'public/no_passing.html')
    path = request.path.split('/')[1]
    return render(request,'operation/upload.html',{'user':request.user.username,
                                                           'path1':'operation',
                                                           'path2':path,
                                                           'page_name1':u'运维操作',
                                                           'page_name2':u'文件上传'})

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

@login_required
def handle_uploaded_file(request,f):
    file_name = ''
    try:
        path = BASE_DIR + '/uploads/'
        file_name = path + f.name
        if not os.path.exists(path):
            os.makedirs(path)
        if os.path.isfile(file_name):
            time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            os.rename(file_name,file_name + '_' + time)
            orm = upload_files.objects.get(file_name=f.name)
            orm.file_name = f.name + '_' + time
            orm.save()
        file = open(file_name, 'wb+')
        for chunk in f.chunks():
            file.write(chunk)
        file.close()
        file_size = os.path.getsize(file_name)
        upload_files.objects.create(file_name=f.name,file_size=file_size,upload_user=request.user.username)
        result_code = 0
    except Exception, e:
        logger.error(e)
        result_code = 1
    return result_code

@login_required
def get_upload(request):
    file = request.FILES.get('file')
    if not file == None:
        result_code = handle_uploaded_file(request,file)
        if result_code == 0:
            return HttpResponse(simplejson.dumps({'msg': "上传成功", "code": 0}),content_type="application/json")
        else:
            return HttpResponse(simplejson.dumps({'msg': "上传失败", "code": 1}),content_type="application/json")
    else:
        return HttpResponse(simplejson.dumps({'msg': "上传失败", "code": 1}),content_type="application/json")

@login_required
def upload_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['file_name','file_size','upload_time','upload_user']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = upload_files.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = upload_files.objects.all().count()
        else:
            result_data = upload_files.objects.filter(Q(file_name__contains=sSearch) | \
                                               Q(file_size__contains=sSearch) | \
                                               Q(upload_user__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = upload_files.objects.filter(Q(file_name__contains=sSearch) | \
                                                 Q(file_size__contains=sSearch) | \
                                                 Q(upload_user__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = upload_files.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = upload_files.objects.all().count()
        else:
            result_data = upload_files.objects.filter(Q(file_name__contains=sSearch) | \
                                               Q(file_size__contains=sSearch) | \
                                               Q(upload_user__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = upload_files.objects.filter(Q(file_name__contains=sSearch) | \
                                                 Q(file_size__contains=sSearch) | \
                                                 Q(upload_user__contains=sSearch)).count()

    for i in  result_data:
        if len(str(i.file_size)) >= 4 and len(str(i.file_size)) < 7:
            file_size = i.file_size / 1024.0
            file_size = re.search(r'\d+\.\d\d',str(file_size))
            file_size = file_size.group() + 'K'
        elif len(str(i.file_size)) >= 7 and len(str(i.file_size)) < 10:
            file_size = i.file_size / 1024.0 / 1024.0
            file_size = re.search(r'\d+\.\d\d',str(file_size))
            file_size = file_size.group() + 'M'
        elif len(str(i.file_size)) >= 10:
            file_size = i.file_size / 1024.0 / 1024.0 / 1024.0
            file_size = re.search(r'\d+\.\d\d',str(file_size))
            file_size = file_size.group() + 'G'
        aaData.append({
                       '0':i.file_name,
                       '1':file_size,
                       '2':str(i.upload_time).split('+')[0],
                       '3':i.upload_user,
                       '4':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def upload_del(request):
    _id = request.POST.get('id')
    orm = upload_files.objects.get(id=_id)
    try:
        os.remove(BASE_DIR + '/uploads/' + orm.file_name)
        orm.delete()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def upload_upload(request):
    flag = request.POST.get('flag')
    file_name = request.POST.get('file_name')
    if int(flag) == 0:
        #开始传输
        # orm = upload_files.objects.get(file_name=file_name)
        rsync_dest = request.POST.get('rsync_dest')
        if rsync_dest:
            rsync_ip = CENTER_SERVER[rsync_dest][0]
            rsync_dir = CENTER_SERVER[rsync_dest][2]
            cmdLine = []
            cmdLine.append('rsync')
            cmdLine.append('--progress')
            cmdLine.append(BASE_DIR + '/uploads/%s' % file_name)
            cmdLine.append('%s:%s' % (rsync_ip,rsync_dir))
            tmpFile = BASE_DIR + "/tmp/upload.tmp"  #临时生成一个文件
            fpWrite = open(tmpFile,'w')
            with open(BASE_DIR + '/tmp/rsync_status_file.tmp','w') as f:
                pass
            process = subprocess.Popen(cmdLine,stdout = fpWrite,stderr = subprocess.PIPE);
            while True:
                fpRead = open(tmpFile,'r')  #这里又重新创建了一个文件读取对象，不知为何，用上面的就是读不出来，改w+也不>行
                lines = fpRead.readlines()
                for line in lines:
                    a = re.search(r'\d+%',line)
                    if a:
                        with open(BASE_DIR + '/tmp/percent.tmp','a') as f:
                                f.write(a.group())
                if  process.poll() == 0:
                    break;
                elif process.poll() == None:
                    pass
                else:
                    break
                fpWrite.truncate()  #此处清空文件，等待记录下一次输出的进度
                fpRead.close()
                time.sleep(0.7)
            fpWrite.close()
            os.remove(BASE_DIR + '/tmp/rsync_status_file.tmp')
        #    error = process.stderr.read()
        #    if not error == None:
        #        print 'error info:%s' % error
            os.remove(tmpFile) #删除临时文件
            os.remove(BASE_DIR + '/tmp/percent.tmp')
            return HttpResponse(simplejson.dumps({'code':0,'msg':u'文件传输成功'}),content_type="application/json")
    elif int(flag) == 1:
        #获取百分比
        if os.path.exists(BASE_DIR + '/tmp/rsync_status_file.tmp'):
            process = 1
        else:
            process = 0
        if os.path.exists(BASE_DIR + '/tmp/percent.tmp'):
            with open(BASE_DIR + '/tmp/percent.tmp') as f:
                data = f.readline()
                if data:
                    last_percent = re.search(r'\d{1,2}%$',data)
                    if last_percent:
                        return HttpResponse(simplejson.dumps({'code':0,'percent':last_percent.group(),'process':process}),content_type="application/json")
        else:
            return HttpResponse(simplejson.dumps({'code':0,'percent':0,'process':process}),content_type="application/json")

    else:
        pass
        return HttpResponse(simplejson.dumps({'code':1,'msg':u'文件传输失败'}),content_type="application/json")

@login_required
def rsync_dest_dropdown(request):
    result = {}
    count = 0
    result['rsync_dest_dropdown_list'] = []
    for k in CENTER_SERVER.keys():
        result['rsync_dest_dropdown_list'].append({'text':k, 'id': count})
        count += 1
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def server_operation(request):
    flag = check_permission(u'服务器操作',request.user.username)
    if flag < 1:
        return render(request,'public/no_passing.html')
    path = request.path.split('/')[1]
    return render(request,'operation/server_operation.html',{'user':request.user.username,
                                                           'path1':'operation',
                                                           'path2':path,
                                                           'page_name1':u'运维操作',
                                                           'page_name2':u'服务器操作'})

@login_required
def password_expire(request):
    orm = perm.objects.get(username=request.user.username)
    expire_time = orm.server_password_expire
    if expire_time:
        expire_time_format = datetime.date(int(expire_time.split('-')[0]),int(expire_time.split('-')[1]),int(expire_time.split('-')[2]))
        expire_day = int(expire_time_format.strftime('%s')) - int(datetime.date.today().strftime('%s'))
        expire_day = expire_day / 60 / 60 / 24
        if expire_day < 10:
            msg = '您的服务器密码将于%s过期，请尽快修改密码' % expire_day
            return HttpResponse(simplejson.dumps({'code':0,'msg':msg}),content_type="application/json")
        else:
            return HttpResponse(simplejson.dumps({'code':1}),content_type="application/json")
    else:
        return HttpResponse(simplejson.dumps({'code':1}),content_type="application/json")

@login_required
def cmd_template(request):
    flag = check_permission(u'命令模板',request.user.username)
    if flag < 1:
        return render(request,'public/no_passing.html')
    path = request.path.split('/')[1]
    return render(request,'operation/cmd_template.html',{'user':request.user.username,
                                                           'path1':'operation',
                                                           'path2':path,
                                                           'page_name1':u'运维操作',
                                                           'page_name2':u'命令模板'})

def cmd_template_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['description','cmd']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = command_template.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = command_template.objects.all().count()
        else:
            result_data = command_template.objects.filter(Q(description__contains=sSearch) | \
                                               Q(cmd__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = command_template.objects.filter(Q(description__contains=sSearch) | \
                                                 Q(cmd__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = command_template.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = command_template.objects.all().count()
        else:
            result_data = command_template.objects.filter(Q(description__contains=sSearch) | \
                                               Q(cmd__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = command_template.objects.filter(Q(description__contains=sSearch) | \
                                                 Q(cmd__contains=sSearch)).count()

    for i in  result_data:
        cmd = []
        for j in i.cmd.split('\n'):
            cmd.append(j+'<br>')
        aaData.append({
                       '0':i.description,
                       '1':''.join(cmd),
                       '2':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def cmd_template_save(request):
    _id = request.POST.get('id')
    description = request.POST.get('description')
    cmd = request.POST.get('cmd')

    try:
        if _id =='':
            command_template.objects.create(description=description,cmd=cmd)
        else:
            orm = command_template.objects.get(id=_id)
            orm.description = description
            orm.cmd = cmd
            orm.save()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(simplejson.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def cmd_template_dropdown(request):
    result = []
    orm = command_template.objects.all()
    for i in orm:
        result.append({'text':i.description,'id':i.id})
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def cmd_template_del(request):
    try:
        _id = request.POST.get('id')
        orm = command_template.objects.get(id=_id)
        orm.delete()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(simplejson.dumps({'code':1,'msg':u'删除失败'}),content_type="application/json")

@login_required
def get_server_list(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['server_name','inner_ip','external_ip','os','belong_to','status']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = server_list.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = server_list.objects.all().count()
        else:
            result_data = server_list.objects.filter(Q(server_name__contains=sSearch) | \
                                               Q(inner_ip__contains=sSearch) | \
                                               Q(external_ip__contains=sSearch) | \
                                               Q(belong_to__contains=sSearch) | \
                                               Q(os__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = server_list.objects.filter(Q(server_name__contains=sSearch) | \
                                                 Q(inner_ip__contains=sSearch) | \
                                                 Q(external_ip__contains=sSearch) | \
                                                 Q(belong_to__contains=sSearch) | \
                                                 Q(os__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = server_list.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = server_list.objects.all().count()
        else:
            result_data = server_list.objects.filter(Q(server_name__contains=sSearch) | \
                                               Q(inner_ip__contains=sSearch) | \
                                               Q(external_ip__contains=sSearch) | \
                                               Q(belong_to__contains=sSearch) | \
                                               Q(os__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = server_list.objects.filter(Q(server_name__contains=sSearch) | \
                                                 Q(inner_ip__contains=sSearch) | \
                                                 Q(external_ip__contains=sSearch) | \
                                                 Q(belong_to__contains=sSearch) | \
                                                 Q(os__contains=sSearch)).count()

    orm = perm.objects.get(username=request.user.username)
    servers = []
    for i in orm.server_groups.split(','):
        orm_server = server_group_list.objects.get(server_group_name=i)
        servers += orm_server.members_server.split(',')

    for i in  result_data:
        if i.server_name in servers:
            aaData.append({
                           '0':i.server_name,
                           '1':i.inner_ip,
                           '2':i.external_ip,
                           '3':i.os,
                           '4':i.belong_to,
                           '5':i.status,
                           '6':i.id
                          })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(simplejson.dumps(result),content_type="application/json")

@login_required
def search_server_list(request):
    try:
        def gevent_run_all(CENTER_SERVER,client_send_data,server_list,p):
            for i in CENTER_SERVER.keys():
                recv_data = client_send_data("{'salt':1,'act':'test.ping','hosts':'*','argv':[]}",CENTER_SERVER[i][0],CENTER_SERVER[i][1])
                dict_data = eval(recv_data)
                for k,v in dict_data.items():
                    p.spawn(gevent_run,client_send_data,server_list,i,k,v,dict_data)

        def gevent_run(client_send_data,server_list,i,k,v,dict_data):
            uniq_test = server_list.objects.filter(server_name=k)
            if v == True and not uniq_test:
                inner_ip = client_send_data("{'salt':1,'act':'grains.item','hosts':'%s','argv':['ipv4']}" % k,CENTER_SERVER[i][0],CENTER_SERVER[i][1])
                inner_ip = eval(inner_ip)
                inner_ip[k]['ipv4'].remove('127.0.0.1')
                # cmd = ["curl http://www.whereismyip.com/|grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'"]
                cmd = ['curl http://members.3322.org/dyndns/getip']
                external_ip = client_send_data("{'salt':1,'act':'cmd.run','hosts':'%s','argv':%s}" % (k,cmd),CENTER_SERVER[i][0],CENTER_SERVER[i][1])
                external_ip = eval(external_ip)
                external_ip = external_ip[k].split('\n')[-1]
                os = client_send_data("{'salt':1,'act':'grains.item','hosts':'%s','argv':['os']}" % k,CENTER_SERVER[i][0],CENTER_SERVER[i][1])
                os = eval(os)
                belong_to = i
                server_list.objects.create(server_name=k,inner_ip=','.join(inner_ip[k]['ipv4']),external_ip=external_ip,os=os[k]['os'],belong_to=belong_to,status=1)
            elif uniq_test:
                orm_server = server_list.objects.get(server_name=k)
                orm_server.status = 1
                orm_server.save()
            for i in server_list.objects.filter(belong_to=i):
                if not i.server_name in dict_data.keys():
                    i.status = 0
                    i.save()
        p = Pool()
        p.spawn(gevent_run_all,CENTER_SERVER,client_send_data,server_list,p)
        p.join()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'获取完成'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(simplejson.dumps({'code':1,'msg':u'获取失败'}),content_type="application/json")

@login_required
def run_cmd(request):
    try:
        server_names = request.POST.get('server_names')
        belong_tos = request.POST.get('belong_tos')
        server_names = server_names.split(',')
        belong_tos = belong_tos.split(',')
        cmd = request.POST.get('cmd')
        cmd_template = request.POST.get('cmd_template')

        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        servers = {}
        cmd_results = ''
        for i in  zip(server_names,belong_tos):
            if not servers.has_key(i[1]):
                servers[i[1]] = []
            servers[i[1]].append(i[0])
        for k,v in servers.items():
            v = ','.join(v)
            if cmd:
                cmd_result = client_send_data("{'salt':1,'act':'cmd.run','hosts':'%s','argv':%s}" % (v,cmd.split(',,')),CENTER_SERVER[k][0],CENTER_SERVER[k][1])
                cmd_result = convert_str_to_html(cmd_result)
                if not cmd_results:
                    cmd_results = cmd_result
                else:
                    cmd_results = cmd_results + '<br><br><br><br>' + cmd_result
            if cmd_template:
                orm = command_template.objects.get(description=cmd_template)
                command = '''echo '%s' > /tmp/tempfile && bash /tmp/tempfile;rm -rf /tmp/tempfile''' % orm.cmd
                cmd_result = client_send_data("{'salt':1,'act':'cmd.run','hosts':'%s','argv':%s}" % (v,command.split(',,')),CENTER_SERVER[k][0],CENTER_SERVER[k][1])
                cmd_result = convert_str_to_html(cmd_result)
                if cmd_results:
                    cmd_results = cmd_result
                else:
                    cmd_results = cmd_results + '<br><br><br><br>' + cmd_result
                cmd = u'模板 < %s >' % cmd_template
        for i in server_names:
            log.objects.create(source_ip=i,username=request.user.username,command=cmd,time=time_now)
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'完成执行完成','cmd_results':cmd_results}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(simplejson.dumps({'code':1,'msg':u'完成执行失败'}),content_type="application/json")

@login_required
def server_del(request):
    try:
        server_names = request.POST.get('server_names')
        for i in server_names.split(','):
            orm = server_list.objects.get(server_name=i)
            orm.delete()
        return HttpResponse(simplejson.dumps({'code':0,'msg':u'服务器删除成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(simplejson.dumps({'code':1,'msg':u'服务器删除失败'}),content_type="application/json")

# @login_required
# def sync_password(request):
#     try:
#         have_server = ''
#         orm_user_perm = perm.objects.get(username=request.user.username)
#         for i in orm_user_perm.server_groups.split(','):
#             orm_server_group = server_group_list.objects.get(server_group_name=i)
#             if have_server == '':
#                 have_server = orm_server_group.members_server
#             else:
#                 have_server = have_server + ',' + orm_server_group.members_server
#         servers = {}
#         aes = crypt_aes(SECRET_KEY[:32])
#         password = aes.decrypt_aes(orm_user_perm.server_password)
#         expire_time = orm_user_perm.server_password_expire
#         cmd = 'if ! id ' + request.user.username + ';then useradd -e $(date "+%D" -d "+3 months") ' + request.user.username + ';fi;echo "' + password + '$(sed -n "/^id:/p" /etc/salt/minion|cut -d" " -f2)" |passwd ' + request.user.username + ' --stdin;usermod -e $(date -d "' + expire_time + '" "+%D") ' + request.user.username
#         for i in have_server.split(','):
#             orm_server = server_list.objects.get(server_name=i)
#             if not servers.has_key(orm_server.belong_to):
#                 servers[orm_server.belong_to] = []
#             servers[orm_server.belong_to].append(i)
#         for k,v in servers.items():
#             v = ','.join(v)
#             client_send_data("{'salt':1,'act':'cmd.run','hosts':'%s','argv':%s}" % (v,cmd.split(',')),CENTER_SERVER[k][0],CENTER_SERVER[k][1])
#         return HttpResponse(simplejson.dumps({'code':0,'msg':u'密码同步完成'}),content_type="application/json")
#     except Exception,e:
#         logger.error(e)
#         return HttpResponse(simplejson.dumps({'code':1,'msg':u'密码同步失败'}),content_type="application/json")

# @login_required
# def login_server(request):
#     # shellinabox = open_web_shell()
#     # a = Process(target=shellinabox.open,args=(20002,'192.168.100.151'))
#     # a.start()
#     # return HttpResponse(simplejson.dumps({'code':0,'msg':u'shell开启成功'}),content_type="application/json")
#     server_ips = request.POST.get('server_ips')
#     for i in server_ips.split(','):
#         shellinabox = open_web_shell()
#         if shellinabox.process(i):
#             return HttpResponse(simplejson.dumps({'code':0,'msg':u'shell开启成功'}),content_type="application/json")
#         else:
#             return HttpResponse(simplejson.dumps({'code':1,'msg':u'shell开启失败'}),content_type="application/json")

@login_required
def fortress_server(request):
    flag = check_permission(u'堡垒机',request.user.username)
    if flag < 1:
        return render(request,'public/no_passing.html')
    path = request.path.split('/')[1]
    return render(request,'operation/fortress_server.html',{'user':request.user.username,
                                                           'path1':'operation',
                                                           'path2':path,
                                                           'page_name1':u'运维操作',
                                                           'page_name2':u'堡垒机'})
