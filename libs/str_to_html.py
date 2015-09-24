# -*- coding: utf-8 -*-
import re,yaml
from ast import literal_eval

def convert_str_to_html(cmd_result):
    cmd_result = literal_eval(cmd_result)
    cmd_result = yaml.dump(cmd_result)
    cmd_result = re.sub(r'\{','',cmd_result)
    cmd_result = re.sub(r'\}','',cmd_result)
    cmd_result = re.sub(r'\n','<br>',cmd_result)
    cmd_result = re.sub(r' ','&nbsp',cmd_result)
    cmd_result = re.sub(r',','<br><br><br>',cmd_result)
    return cmd_result