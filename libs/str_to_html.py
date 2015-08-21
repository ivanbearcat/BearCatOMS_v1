# -*- coding: utf-8 -*-
import re,yaml

def convert_str_to_html(cmd_result):
    cmd_result = eval(cmd_result)
    cmd_result = yaml.dump(cmd_result)
    cmd_result = re.sub(r'\{','',cmd_result)
    cmd_result = re.sub(r'\}','',cmd_result)
    cmd_result = re.sub(r'\n','<br>',cmd_result)
    cmd_result = re.sub(r' ','&nbsp',cmd_result)
    cmd_result = re.sub(r',','<br><br><br><br>',cmd_result)
    return cmd_result