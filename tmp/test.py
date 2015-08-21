import re
from BearCatOMS.settings import BASE_DIR
sidebar_list = []
sidebar_list2 = []
with open(BASE_DIR + '/templates/public/sidebar.html') as f:
    line = f.readline()
    while line:
        data = re.search(r'name=".*"',line)
        if data:
            data = data.group().replace('"','')
            sidebar_list.append(data.replace('name=',''))
        line = f.readline()
for i in sidebar_list:
    print i