# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from django.utils.log import logger
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from libs.check_perm import check_permission
from libs.socket_send_data import client_send_data
from libs.str_to_html import convert_str_to_html
from libs.check_center_server import check_center_server_up
from libs.remote_run_cmd import r_cmd
from BearCatOMS.settings import CENTER_SERVER
from saltstack.models import saltstack_state,saltstack_top,saltstack_pillar
from operation.models import server_list
from audit.models import log
from perm_manage.models import perm,server_group_list
import os,commands,datetime,re,paramiko,json

# from gevent import monkey; monkey.patch_socket()
import gevent
from gevent.queue import Queue
from gevent.pool import Pool

@login_required
def salt_top(request):
    flag = check_permission(u'state模块对应',request.user.username)
    if flag < 1:
        return render(request,'public/no_passing.html')
    path = request.path.split('/')[1]
    return render(request,'saltstack/salt_top.html',{'user':request.user.username,
                                                           'path1':'saltstack',
                                                           'path2':path,
                                                           'page_name1':u'saltstack',
                                                           'page_name2':u'state模块对应'})

@login_required
def salt_top_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['center_server','target','state','id']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = saltstack_top.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_top.objects.all().count()
        else:
            result_data = saltstack_top.objects.filter(Q(target__contains=sSearch) | \
                                               Q(center_server__contains=sSearch) | \
                                               Q(state__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_top.objects.filter(Q(target__contains=sSearch) | \
                                                 Q(center_server__contains=sSearch) | \
                                                 Q(state__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = saltstack_top.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_top.objects.all().count()
        else:
            result_data = saltstack_top.objects.filter(Q(target__contains=sSearch) | \
                                               Q(center_server__contains=sSearch) | \
                                               Q(state__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_top.objects.filter(Q(target__contains=sSearch) | \
                                                 Q(center_server__contains=sSearch) | \
                                                 Q(state__contains=sSearch)).count()

    orm = perm.objects.get(username=request.user.username)
    servers = []
    for i in orm.server_groups.split(','):
        orm_server = server_group_list.objects.get(server_group_name=i)
        servers += orm_server.members_server.split(',')
    for i in result_data:
        flag = 0
        for j in  i.target.split(','):
            if j in servers:
                flag += 1
        if flag == len(i.target.split(',')):
            aaData.append({
                           '0':i.center_server,
                           '1':i.target,
                           '2':i.state,
                           '3':i.id
                          })

    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")

@login_required
def salt_top_save(request):
    _id = request.POST.get('id')
    # center_server = request.POST.get('center_server')
    target = request.POST.get('target')
    state = request.POST.get('state')
    # master_dir = commands.getoutput('''ssh %s "grep -A2 '^file_roots' /etc/salt/master |grep 'base:' -A1|grep '-'|cut -d'-' -f2"''' % CENTER_SERVER[center_server][0])

    try:
        center_server = ''
        for i in target.split(','):
            orm_server = server_list.objects.get(server_name=i)
            if center_server:
                if orm_server.belong_to != center_server:
                    return HttpResponse(json.dumps({'code':1,'msg':u'目标主机不在同一个中心服务器上'}),content_type="application/json")
            else:
                center_server = orm_server.belong_to
            for j in state.split(','):
                orm_state = saltstack_state.objects.get(name=j)
                if not center_server in orm_state.center_server.split(','):
                    return HttpResponse(json.dumps({'code':1,'msg':u'目标主机的中心服务器上没有这个模块'}),content_type="application/json")
        if _id =='':
            # for i in target.split(','):
            #     if saltstack_top.objects.filter(target=i):
            #         return HttpResponse(json.dumps({'code':1,'msg':u'目标主机已存在对应'}),content_type="application/json")
            #     else:
            saltstack_top.objects.create(center_server=center_server,target=target,state=state)
        else:
            orm = saltstack_top.objects.get(id=_id)
            orm.center_server = center_server
            orm.target = target
            orm.state = state
            orm.save()
        # content = 'base:\n'
        # for i in  saltstack_top.objects.all():
        #     content += "  '%s':\n" % i.target
        #     for j in i.state.split(','):
        #         content += '    - %s\n' % j
        # content += 'EOF'
        # os.system('''ssh %s "cat > %s/top.sls << EOF\n%s"''' % (CENTER_SERVER[center_server][0],master_dir,content))
        return HttpResponse(json.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(json.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def salt_top_dropdown(request):
    _id = request.POST.get('id')
    result = {}
    result['target'] = {}
    result['target']['list'] = []
    result['target']['edit'] = []
    result['state'] = {}
    result['state']['list'] = []
    result['state']['edit'] = []
    result['center_server'] = []
    count = 0
    if _id:
        orm = saltstack_top.objects.get(id=_id)
        for i in orm.target.split(','):
            orm_target = server_list.objects.get(server_name=i)
            result['target']['edit'].append({'text':i,'id':orm_target.id})
        for i in orm.state.split(','):
            orm_state = saltstack_state.objects.get(name=i)
            result['state']['edit'].append({'text':i,'id':orm_state.id})

    orm = perm.objects.get(username=request.user.username)
    servers = []
    for i in orm.server_groups.split(','):
        orm_server = server_group_list.objects.get(server_group_name=i)
        servers += orm_server.members_server.split(',')

    for i in CENTER_SERVER.keys():
        result['center_server'].append({'text':i,'id':count})
        count += 1
    for i in server_list.objects.all():
        if i.server_name in servers:
            result['target']['list'].append({'text':i.server_name,'id':i.id})
    for i in saltstack_state.objects.all():
        result['state']['list'].append({'text':i.name,'id':i.id})




    return HttpResponse(json.dumps(result),content_type="application/json")

@login_required
def salt_top_del(request):
    try:
        target_id = request.POST.get('target_id')
        for i in target_id.split(','):
            orm = saltstack_top.objects.get(id=i)
            orm.delete()
        return HttpResponse(json.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(json.dumps({'code':1,'msg':u'删除失败'}),content_type="application/json")

@login_required
def salt_top_run(request):
    center_server = request.POST.get('center_server')
    run_target = request.POST.get('run_target')
    state = request.POST.get('state')

    for server in center_server.split('|'):
        if not check_center_server_up(CENTER_SERVER[server][0],CENTER_SERVER[server][1]):
            return HttpResponse(json.dumps({'code':1,'msg':u'无法连接到%s' % server, 'cmd_results':''}),content_type="application/json")

    run_target_dict = {}
    target = []
    cmd_results = ''
    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for i in  zip(center_server.split('|'),run_target.split('|'),state.split('|')):
        if not run_target_dict.has_key(i[0]):
            run_target_dict[i[0]] = []
        run_target_dict[i[0]].append((i[1],i[2]))

    for i in run_target_dict.keys():
        master_dir = commands.getoutput('''ssh %s "grep -A2 '^file_roots' /etc/salt/master |grep 'base:' -A1|grep '-'|cut -d'-' -f2"''' % CENTER_SERVER[i][0])
        content = 'base:\n'
        for j in run_target_dict[i]:
            for n in j[0].split(','):
                if not n in target:
                    target.append(n)
                    cmd = u'state模块 < %s >' % j[1]
                    log.objects.create(source_ip=n,username=request.user.username,command=cmd,time=time_now)
                else:
                    return HttpResponse(json.dumps({'code':1,'msg':u'目标主机不能重复','cmd_results':cmd_results}),content_type="application/json")
                content += "  '%s':\n" % n
                for m in j[1].split(','):
                    content += '    - %s\n' % m
        content += 'EOF'
        os.system('''ssh %s "cat > %s/top.sls << EOF\n%s"''' % (CENTER_SERVER[i][0],master_dir,content))

    try:
        # def gevent_run_all(CENTER_SERVER,client_send_data,p,q):
        #     for i in run_target_dict.keys():
        #         for j in run_target_dict[i]:
        #             p.spawn(gevent_run,CENTER_SERVER,client_send_data,i,j[0],q)
        # def gevent_run(CENTER_SERVER,client_send_data,i,j,q):
        #     cmd_result = client_send_data(json.dumps({'salt':1,'act':'state.highstate','hosts':j,'argv':''}),CENTER_SERVER[i][0],CENTER_SERVER[i][1])
        #     cmd_result = convert_str_to_html(cmd_result)
        #     q.put(cmd_result)
        # p = Pool()
        # q = Queue()
        # p.spawn(gevent_run_all,CENTER_SERVER,client_send_data,p,q)
        # p.join()
        # for i in range(q.qsize()):
        #     cmd_result = q.get()
        #     if not cmd_results:
        #         cmd_results = cmd_result
        #     else:
        #         cmd_results = cmd_results + '<br><br><br><br>' + cmd_result

        hosts_list = []
        for i in run_target_dict.keys():
            for j in run_target_dict[i]:
                hosts_list.append(j[0])
            cmd_result = client_send_data(json.dumps({'salt':1,'act':'state.highstate','hosts':','.join(hosts_list),'argv':''}),CENTER_SERVER[i][0],CENTER_SERVER[i][1])
            cmd_results = convert_str_to_html(cmd_result)
        return HttpResponse(json.dumps({'code':0,'msg':u'模块执行完成','cmd_results':cmd_results}),content_type="application/json")
    except Exception:
        return HttpResponse(json.dumps({'code':1,'msg':u'模块执行失败'}),content_type="application/json")

@login_required
def salt_state(request):
    flag = check_permission(u'state模块定义',request.user.username)
    if flag < 1:
        return render(request,'public/no_passing.html')
    path = request.path.split('/')[1]
    return render(request,'saltstack/salt_state.html',{'user':request.user.username,
                                                           'path1':'saltstack',
                                                           'path2':path,
                                                           'page_name1':u'saltstack',
                                                           'page_name2':u'state模块定义'})

@login_required
def salt_state_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['center_server','name','content','id']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = saltstack_state.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_state.objects.all().count()
        else:
            result_data = saltstack_state.objects.filter(Q(name__contains=sSearch) | \
                                               Q(center_server__contains=sSearch) | \
                                               Q(content__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_state.objects.filter(Q(name__contains=sSearch) | \
                                                 Q(center_server__contains=sSearch) | \
                                                 Q(content__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = saltstack_state.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_state.objects.all().count()
        else:
            result_data = saltstack_state.objects.filter(Q(name__contains=sSearch) | \
                                               Q(center_server__contains=sSearch) | \
                                               Q(content__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_state.objects.filter(Q(name__contains=sSearch) | \
                                                 Q(center_server__contains=sSearch) | \
                                                 Q(content__contains=sSearch)).count()

    for i in  result_data:
        content_list = []
        content = i.content.replace('<','&lt;').replace('>','&gt;')
        for j in content.split('\n'):
            content_list.append(j+'<br>')
        aaData.append({
                       '0':i.center_server,
                       '1':i.name,
                       '2':''.join(content_list).replace(' ','&nbsp'),
                       '3':i.id
                      })
    result = {'sEcho':sEcho,
               'iTotalRecords':iTotalRecords,
               'iTotalDisplayRecords':iTotalRecords,
               'aaData':aaData
    }
    return HttpResponse(json.dumps(result),content_type="application/json")

@login_required
def salt_state_save(request):
    _id = request.POST.get('id')
    center_server = request.POST.get('center_server')
    name = request.POST.get('name')
    content = request.POST.get('content')

    try:
        for i in center_server.split(','):
            master_dir = commands.getoutput('''ssh %s "grep -A2 '^file_roots' /etc/salt/master |grep 'base:' -A1|grep '-'|cut -d'-' -f2"''' % CENTER_SERVER[i][0])
            # os.system('''ssh %s "mkdir -p %s/%s;cat > %s/%s/init.sls << EOF\n%s\nEOF"''' % (CENTER_SERVER[i][0],master_dir,name,master_dir,name,content))
            cmd = '''mkdir -p %s/%s;cat > %s/%s/init.sls << EOF\n%s\nEOF''' % (master_dir,name,master_dir,name,content.replace('$','\$'))
            r_cmd(CENTER_SERVER[i][0],cmd)
        if _id =='':
            saltstack_state.objects.create(center_server=center_server,name=name,content=content)
        else:
            orm = saltstack_state.objects.get(id=_id)
            # old_name = orm.name
            orm.center_server = center_server
            orm.content = content
            orm.save()
            # if name != old_name:
            #     os.system('''ssh %s "rm -r %s/%s"''' % (CENTER_SERVER[i][0],master_dir,old_name))

        return HttpResponse(json.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(json.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def salt_state_dropdown(request):
    center_server = request.POST.get('center_server')
    result = {}
    result['list'] = []
    result['edit'] = []
    if center_server:
        for i in center_server.split(','):
            result['edit'].append({'text':i,'id':CENTER_SERVER[i][3]})
    for i in CENTER_SERVER.keys():
        result['list'].append({'text':i,'id':CENTER_SERVER[i][3]})
    return HttpResponse(json.dumps(result),content_type="application/json")

@login_required
def salt_state_del(request):
    try:
        _id = request.POST.get('id')
        orm = saltstack_state.objects.get(id=_id)
        state_list = []
        for i in saltstack_top.objects.all():
            for j in i.state.split(','):
                state_list.append(j)
        if orm.name in state_list:
            return HttpResponse(json.dumps({'code':1,'msg':u'模块已被应用无法删除'}),content_type="application/json")
        for i in orm.center_server.split(','):
            master_dir = commands.getoutput('''ssh %s "grep -A2 '^file_roots' /etc/salt/master |grep 'base:' -A1|grep '-'|cut -d'-' -f2"''' % CENTER_SERVER[i][0])
            os.system('''ssh %s "rm -r %s/%s"''' % (CENTER_SERVER[i][0],master_dir,orm.name))
        orm.delete()
        return HttpResponse(json.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(json.dumps({'code':1,'msg':u'删除失败'}),content_type="application/json")

@login_required
def salt_pillar(request):
    flag = check_permission(u'state模块定义',request.user.username)
    if flag < 1:
        return render(request,'public/no_passing.html')
    path = request.path.split('/')[1]
    return render(request,'saltstack/salt_pillar.html',{'user':request.user.username,
                                                           'path1':'saltstack',
                                                           'path2':path,
                                                           'page_name1':u'saltstack',
                                                           'page_name2':u'pillar参数定义'})

@login_required
def salt_pillar_data(request):
    sEcho =  request.POST.get('sEcho') #标志，直接返回
    iDisplayStart = int(request.POST.get('iDisplayStart'))#第几行开始
    iDisplayLength = int(request.POST.get('iDisplayLength'))#显示多少行
    iSortCol_0 = int(request.POST.get("iSortCol_0"))#排序行号
    sSortDir_0 = request.POST.get('sSortDir_0')#asc/desc
    sSearch = request.POST.get('sSearch')#高级搜索

    aaData = []
    sort = ['center_server','name','content','id']

    if  sSortDir_0 == 'asc':
        if sSearch == '':
            result_data = saltstack_pillar.objects.all().order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_pillar.objects.all().count()
        else:
            result_data = saltstack_pillar.objects.filter(Q(name__contains=sSearch) | \
                                               Q(center_server__contains=sSearch) | \
                                               Q(content__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0])[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_pillar.objects.filter(Q(name__contains=sSearch) | \
                                                 Q(center_server__contains=sSearch) | \
                                                 Q(content__contains=sSearch)).count()
    else:
        if sSearch == '':
            result_data = saltstack_pillar.objects.all().order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_pillar.objects.all().count()
        else:
            result_data = saltstack_pillar.objects.filter(Q(name__contains=sSearch) | \
                                               Q(center_server__contains=sSearch) | \
                                               Q(content__contains=sSearch)) \
                                            .order_by(sort[iSortCol_0]).reverse()[iDisplayStart:iDisplayStart+iDisplayLength]
            iTotalRecords = saltstack_pillar.objects.filter(Q(name__contains=sSearch) | \
                                                 Q(center_server__contains=sSearch) | \
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
    return HttpResponse(json.dumps(result),content_type="application/json")

@login_required
def salt_pillar_save(request):
    _id = request.POST.get('id')
    center_server = request.POST.get('center_server')
    name = request.POST.get('name')
    content = request.POST.get('content')

    try:
        if _id =='':
            saltstack_pillar.objects.create(center_server=center_server,name=name,content=content)
        else:
            orm = saltstack_pillar.objects.get(id=_id)
            orm.center_server = center_server
            orm.content = content
            orm.save()

        for i in center_server.split(','):
            master_dir = commands.getoutput('''ssh %s "grep -A2 '^pillar_roots' /etc/salt/master |grep 'base:' -A1|grep '-'|cut -d'-' -f2"''' % CENTER_SERVER[i][0])
            os.system('''ssh %s "cat > %s/%s.sls << EOF\n%s\nEOF"''' % (CENTER_SERVER[i][0],master_dir,name,content))
            content_top = '''base:\n  '*':\n'''
            for j in saltstack_pillar.objects.all():
                if i in j.center_server.split(','):
                    content_top += '''    - %s\n''' % j.name
            content_top += 'EOF'
            os.system('''ssh %s "cat > %s/top.sls << EOF\n%s"''' % (CENTER_SERVER[i][0],master_dir,content_top))

        return HttpResponse(json.dumps({'code':0,'msg':u'保存成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(json.dumps({'code':1,'msg':str(e)}),content_type="application/json")

@login_required
def salt_pillar_del(request):
    try:
        _id = request.POST.get('id')
        orm = saltstack_pillar.objects.get(id=_id)
        for i in orm.center_server.split(','):
            master_dir = commands.getoutput('''ssh %s "grep -A2 '^pillar_roots' /etc/salt/master |grep 'base:' -A1|grep '-'|cut -d'-' -f2"''' % CENTER_SERVER[i][0])
            os.system('''ssh %s "rm -r %s/%s\.sls"''' % (CENTER_SERVER[i][0],master_dir,orm.name))
        orm.delete()
        for i in CENTER_SERVER.keys():
            master_dir = commands.getoutput('''ssh %s "grep -A2 '^pillar_roots' /etc/salt/master |grep 'base:' -A1|grep '-'|cut -d'-' -f2"''' % CENTER_SERVER[i][0])
            content_top = '''base:\n  '*':\n'''
            for j in saltstack_pillar.objects.all():
                if i in j.center_server.split(','):
                    content_top += '''    - %s\n''' % j.name
            content_top += 'EOF'
            if len(re.findall(r'\n',content_top)) < 3:
                content_top = ''
            os.system('''ssh %s "cat > %s/top.sls << EOF\n%s"''' % (CENTER_SERVER[i][0],master_dir,content_top))
        return HttpResponse(json.dumps({'code':0,'msg':u'删除成功'}),content_type="application/json")
    except Exception,e:
        logger.error(e)
        return HttpResponse(json.dumps({'code':1,'msg':u'删除失败'}),content_type="application/json")