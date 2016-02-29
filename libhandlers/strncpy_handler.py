'''
Created on Dec 13, 2015

@author: yangke
'''
from ArgHandler import ArgHandler
from model.TaintJob import TaintJob
from model.TaintVar import TaintVar
from utils.Filter import Filter
import re
class strncpy_handler(object):
    
    @staticmethod
    def gen_match_str(variable):
        access=variable.accessStr()
        if '|' not in access:
            return r"(?<![_A-Za-z0-9])strncpy\s*\(\s*&\s*"+access+r"\s*,"
        else:
            pointerstr=variable.pointerStr()
            return r"(?<![_A-Za-z0-9])strncpy\s*\(\s*"+pointerstr+r"\s*,"
    @staticmethod
    def isArgDef(variable,codestr):
        lib_definition=strncpy_handler.gen_match_str(variable)
        m=re.search(lib_definition,codestr)
        if m is None:
            return False
        else:
            return True
    @staticmethod
    def getJobs(index,varstr,codestr):
        syscall_definition=strncpy_handler.gen_match_str(varstr)
        m=re.search(syscall_definition,codestr)
        start_pos=m.span()[1]
        end_pos,islast=ArgHandler.nextarg(codestr,start_pos)
        if end_pos is None:
            print "Error! strncpy second arg wrong!" 
            x=1/0
        elif islast:
            print "Error! strncpy third arg missing!" 
            x=1/0
        former_vars,follow_vars=ArgHandler.vars_in_pointer_offset_style(codestr[start_pos:end_pos])
        jobs=[]
        jobs.append(TaintJob(index,TaintVar(former_vars[0],['*'])))
        if follow_vars:
            for v in follow_vars:
                jobs.append(TaintJob(index,TaintVar(v,[])))
        start_pos=end_pos+1
        end_pos,islast=ArgHandler.nextarg(codestr,start_pos)
        if end_pos is None or not islast :
            print "Error! strncpy third arg wrong!" 
            x=1/0
        vs=Filter.expression2vars(codestr[start_pos:end_pos])
        for v in vs:
            jobs.append(TaintJob(index,TaintVar(v,[])))
        return jobs