'''
Created on Sep 5, 2015

@author: yangke
'''
import re
class FunctionCallInfo:
    
    #===========================================================================
    # def __init__(self, str):
    #     print str
    #     array=str.split('at ')
    #     self.func_name = array[0].split('(')[0].strip()
    #     self.param_list =array[0].split('(')[1].split(')')[0].strip()
    #     self.pos_info = array[1].strip()
    #     self.listOfLines = []
    #===========================================================================
    def __init__(self, str):
        
        i=0
        while str[i]!='(':i+=1
        self.func_name = str[:i].strip()
        j=len(str)-7#'at a.c:9'
        while str[j:j+3]!='at ':j-=1
        self.pos_info = str[j+3:].strip()
        self.param_list = str[i+1:j].strip().rstrip(')')
        self.listOfLines = []
        self.init_file_name_and_line_num_now()
        #-------LOG INFO-------------
        #=======================================================================
        # print "init codestr:",str
        # print "function name:",self.func_name
        # print "position info",self.pos_info
        # print "param_list",self.param_list
        #=======================================================================
    def init_file_name_and_line_num_now(self):
        self.file_name=self.pos_info.split(":")[0]
        self.line_num_now=self.pos_info.split(":")[1]
    def get_line_num_now(self):
        return int(self.line_num_now)
    def get_file_name(self):
        return self.file_name
       
    def addLines(self,l):
        self.listOfLines.extend(l)
           
    def get_func_name(self):
        return self.func_name

    def get_param_list(self):
        return self.param_list

    def set_func_name(self, value):
        self.func_name = value


    def set_param_list(self, value):
        self.param_list = value


    def set_file_name(self, value):
        self.__file_name = value
        
    def ignore_param_value_str(self):
        s1=re.sub(r'0x[a-fA-F0-9]+','',str(self))
        return re.sub(r'=[0-9]+','',s1)
    
    def __str__(self):
        #paramlist="format=format@".join(re.split(r'format.*format@',self.param_list))
        return self.func_name+' ('+self.param_list+')'+' at '+self.pos_info
    
    def __eq__(self, obj):
        return isinstance(obj, FunctionCallInfo) and self.func_name==obj.func_name
       
    def __hash__(self):
        return hash(str(self))
