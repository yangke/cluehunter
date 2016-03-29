'''
Created on Dec 13, 2015

@author: yangke
'''
from ArgHandler import ArgHandler
from model.TaintJob import TaintJob
from model.TaintVar import TaintVar
from utils.Filter import Filter
import re
class sscanf_handler(object):
    
    @staticmethod
    def gen_match_str(variable):
        access=variable.accessStr()
        if '|' not in access:
            return r"(?<![_A-Za-z0-9])sscanf\s*\([^,]*,.*,\s*&\s*"+access+r"\s*[,\)]"
        else:
            pointerstr=variable.pointerStr()
            return r"(?<![_A-Za-z0-9])sscanf\s*\([^,]*,.*,\s*"+pointerstr+r"\s*[,\)]"
    @staticmethod
    def isArgDef(variable,codestr):
        lib_definition=sscanf_handler.gen_match_str(variable)
        m=re.search(lib_definition,codestr)
        if m is None:
            return False
        else:
            return True
    
    @staticmethod
    def getJobs(index,varstr,codestr):
        syscall_definition=sscanf_handler.gen_match_str(varstr)
        m0=re.search(syscall_definition,codestr)
        sscanf_str=m0.group()
        start_pos=re.search("sscanf\s*\(",sscanf_str).span()[1]
        end_pos,islast=ArgHandler.nextarg(sscanf_str,start_pos)
        if end_pos is None:
            print "Error! sscanf second arg wrong!" 
            x=1/0
        elif islast:
            print "Error! sscanf format string arg missing!" 
            x=1/0
        former_vars,follow_vars=ArgHandler.vars_in_pointer_offset_style(sscanf_str[start_pos:end_pos])
        jobs=[]
        jobs.append(TaintJob(index,TaintVar(former_vars[0],['*'])))
        if follow_vars:
            for v in follow_vars:
                jobs.append(TaintJob(index,TaintVar(v,[])))
        start_pos=end_pos+1
        end_pos,islast=ArgHandler.nextarg(sscanf_str,start_pos)
        if end_pos is None or islast:
            print "Error! format string wrong or third arg missing !" 
            x=1/0
        vs=Filter.expression2vars(sscanf_str[start_pos:end_pos])
        for v in vs:
            jobs.append(TaintJob(index,TaintVar(v,[])))
        return jobs