'''
Created on Sep 9, 2015

@author: yangke
'''
from parse.FunctionCallInfo import FunctionCallInfo
class TaintJob:
    
    def __init__(self,index,var):
        self.trace_index=index
        self.var=var
    def __eq__(self,obj):
        return   str(self)==str(obj)
    def __hash__(self):
        return hash(str(self))
    def __str__(self):
        return str(self.trace_index)+" "+str(self.var)
    def isParamJob(self,l):
        return isinstance(l[self.trace_index],FunctionCallInfo)
        