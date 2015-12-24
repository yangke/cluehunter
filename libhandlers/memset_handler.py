'''
Created on Dec 13, 2015

@author: yangke
'''
from ArgHandler import ArgHandler
from model.TaintJob import TaintJob
from model.TaintVar import TaintVar
from utils.Filter import Filter
import re
class memset_handler(object):
    
    @staticmethod
    def gen_match_str(varstr):
        #return r"(?<![A-Za-z0-9_])memset\s*\(\s*"+varstr+r"([^,\(]*),([^,\(]*),([^,\(]*)\s*\)"
        return r"(?<![A-Za-z0-9_])memset\s*\(\s*"+varstr+r"\s*,"
    @staticmethod
    def isArgDef(varstr,codestr):
        lib_definition=memset_handler.gen_match_str(varstr)
        m=re.search(lib_definition,codestr)
        if m is None:
            return False
        else:
            return True
    @staticmethod
    def getJobs(index,varstr,codestr):
        syscall_definition=memset_handler.gen_match_str(varstr)
        m=re.search(syscall_definition,codestr)
        start_pos=m.span()[1]
        end_pos,islast=ArgHandler.nextarg(codestr,start_pos)
        if end_pos is None:
            print "Error! memset second arg wrong!"
            x=1/0
        elif islast:
            print "Error! memset third arg missing!" 
            x=1/0
        start_pos=end_pos+1
        end_pos,islast=ArgHandler.nextarg(codestr,start_pos)
        if end_pos is None or not islast :
            print "Error! memset third arg wrong!" 
            x=1/0
        third_param=codestr[start_pos:end_pos]
        vs=Filter.expression2vars(third_param)
        jobs=[]
        for v in vs:
            jobs.append(TaintJob(index,TaintVar(v,[])))
            print "handle memset! new job var:",v,[]
        return jobs