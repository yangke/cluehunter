'''
Created on Sep 9, 2015
@author: yangke
'''
from parse.FunctionCallInfo import FunctionCallInfo
class TaintJob:
    
    def __init__(self,index,var,corresponding_arg_pos=None):
        self.trace_index=index
        self.var=var
        self.corresponding_arg_pos=corresponding_arg_pos
    def __eq__(self,obj):
        return   str(self)==str(obj)
    def __hash__(self):
        return hash(str(self))
    def __str__(self):
        return str(self.trace_index)+" "+str(self.var)
    def isParamJob(self,l):
        return isinstance(l[self.trace_index],FunctionCallInfo)     