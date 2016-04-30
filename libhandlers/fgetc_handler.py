'''
Created on Dec 13, 2015

@author: yangke
'''
from model.TaintJob import TaintJob
from model.TaintVar import TaintVar
import re
num_pattern=re.compile(r"\s*[0-9]|([1-9][0-9]+)\s*")
class fgetc_handler(object):
    @staticmethod
    def gen_match_str(variable):
        access=variable.accessStr()
        return r"(?<![_A-Za-z0-9])fgetc\s*\(\s*"+access+r"\s*\)"
    @staticmethod
    def isArgDef(variable,codestr):
        lib_definition=fgetc_handler.gen_match_str(variable)
        m=re.search(lib_definition,codestr)
        if m is None:
            return False
        else:
            return True
        
    @staticmethod
    def getJobs(i,varstr,codestr):
        lib_definition=fgetc_handler.gen_match_str(varstr)
        m=re.search(lib_definition,codestr)
        jobs=[]
        if m:
            v=m.group().lstrip("fgetc").strip().strip("()").strip()
            jobs.append(TaintJob(i,TaintVar(v,[])))
            print "The fgetc is handled!"
        return jobs