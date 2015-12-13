'''
Created on Dec 13, 2015

@author: yangke
'''
from ArgHandler import ArgHandler
from model.TaintJob import TaintJob
from model.TaintVar import TaintVar
from utils.Filter import Filter
import re
class strcpy_handler(object):
    
    @staticmethod
    def gen_match_str(varstr):
        return r"(?<![A-Za-z0-9_])strcpy\s*\(\s*"+varstr+r"\s*,"
    @staticmethod
    def isArgDef(varstr,codestr):
        lib_definition=strcpy_handler.gen_match_str(varstr)
        m=re.search(lib_definition,codestr)
        if m is None:
            return False
        else:
            return True
    @staticmethod
    def getJobs(index,varstr,codestr):
        syscall_definition=strcpy_handler.gen_match_str(varstr)
        m=re.search(syscall_definition,codestr)
        start_pos=m.span()[1]
        end_pos=ArgHandler.nextarg(codestr,start_pos)
        if codestr[end_pos]!=")":
            print "Error! strcpy second arg malformed!" 
            x=1/0
        jobs=[]
        former_vars,follow_vars=ArgHandler.vars_in_pointer_offset_style(codestr[start_pos:end_pos])
        jobs.append(TaintJob(index,TaintVar(former_vars[0],['*'])))
        print "handle memset! new job var:",vars[0],['*']
        if follow_vars:
            for v in follow_vars:
                jobs.append(TaintJob(index,TaintVar(v,[])))
                print "handle memset! new job var:",v,[]
        return jobs