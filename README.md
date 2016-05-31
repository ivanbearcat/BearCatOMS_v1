# BearCatOMS_v1
## 依赖包:  
###yum:  
MySQL-python  
gcc  
python-devel  
shellinabox  

###pip:  
django==1.4.20
PyYAML  
gevent  
paramiko  
pexpect  
pycrypto  

###注:  
1. WEB端服务器需要和center_server建立SSH的KEY登录  

2. 升级到1.8.13需要修改log：  
#from django.utils.log import logger  
import logging  
logger = logging.getLogger(__name__)  
