#coding:utf-8
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect,HttpResponse
from django.utils.log import logger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import simplejson,re,datetime,os,pexpect,time,commands
from perm_manage.models import server_group_list,perm
from operation.models import server_list
from BearCatOMS.settings import BASE_DIR,SECRET_KEY,CENTER_SERVER
from libs import crypt
from libs.check_perm import check_permission
from libs.socket_send_data import client_send_data
from gevent import monkey; monkey.patch_socket()
import gevent
from gevent.pool import Pool



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
                p = pexpect.spawn('su %s -c ssh-keygen' % request.user.username)
                p.expect('Enter file in which to save the key.*')
                p.sendline()
                p.sendline()
                p.sendline()
                time.sleep(3)
                if code:
                    return HttpResponse(simplejson.dumps({'code':code,'msg':'密码修改失败'}),content_type="application/json")
            else:
                code = os.system('usermod -e $(date "+%D" -d "+3 months") ' + request.user.username + ' && echo ' + server_password_new_again + '|passwd --stdin ' + request.user.username)
                if code:
                    return HttpResponse(simplejson.dumps({'code':code,'msg':'密码修改失败'}),content_type="application/json")
            # with open('/home/%s/.ssh/id_rsa.pub' % request.user.username) as f:
            #     public_key = f.readline()
            public_key = commands.getoutput('cat /home/%s/.ssh/id_rsa.pub' % request.user.username)
            cmd = 'mkdir -p /root/.ssh;if ! grep %s /root/.ssh/authorized_keys;then echo "%s" >> /root/.ssh/authorized_keys;fi' % (request.user.username,public_key)
            server_groups = server_group_list.objects.all()
            def gevent_run_all(server_groups,p,client_send_data,cmd,CENTER_SERVER):
                for i in server_groups:
                    for j in i.members_server.split(','):
                        orm_server = server_list.objects.get(server_name=j)
                        p.spawn(gevent_run,client_send_data,orm_server.belong_to,j,cmd,CENTER_SERVER)
            def gevent_run(client_send_data,belong_to,j,cmd,CENTER_SERVER):
                client_send_data("{'salt':1,'act':'cmd.run','hosts':'%s','argv':%s}" % (j,cmd.split(',,')),CENTER_SERVER[belong_to][0],CENTER_SERVER[belong_to][1])
#                    os.system('ssh-copy-id -i /home/%s/.ssh/id_rsa.pub root@%s' % (request.user.username,j))
            p = Pool()
            p.spawn(gevent_run_all,server_groups,p,client_send_data,cmd,CENTER_SERVER)
            p.join()
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
