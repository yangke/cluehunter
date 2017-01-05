'''
Created on Sep 6, 2015

@author: yangke
'''
import re
class LineOfCode:

    def __init__(self, line, func_call_info):
        
        lineNumPattern = re.compile(r'^[1-9][0-9]*')
        lineNumStr = re.findall(lineNumPattern,line)[0]
        self.codestr_with_comments = line.lstrip(lineNumStr)#note that there are space character before the codeline
        self.linenum = int(lineNumStr)
        self.codestr = self.remove_comments(self.codestr_with_comments)
        self.expand_code_list = None
        self.func_call_info=func_call_info
        
    def remove_comments(self,codestr):
        if len(codestr)>1:
            for i in range(0,len(codestr)-1):
                if codestr[i]=="/":
                    if codestr[i+1]=="/" or codestr[i+1]=="*":
                        codestr=codestr[:i]
                        break
        return codestr
    
    def get_func_call_info(self):
        return self.func_call_info

    def set_func_call_info(self, value):
        self.func_call_info = value

    def get_linenum(self):
        return self.linenum

    def get_codestr(self):
        return self.codestr
        
    def __str__(self): 
        return str(self.linenum) + self.codestr_with_comments
        
    def __eq__(self,obj):
        return isinstance(obj,LineOfCode) and str(self)==str(obj)\
            and self.func_call_info == obj.func_call_info
            #and self.expand_code_list == obj.expand_code_list
            
    def __hash__(self):
        return hash(str(self))^hash(self.func_call_info) 