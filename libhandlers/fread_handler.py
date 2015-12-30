'''
Created on Dec 13, 2015

@author: yangke
'''
from model.TaintJob import TaintJob
from model.TaintVar import TaintVar
import re
num_pattern=re.compile(r"\s*[0-9]|([1-9][0-9]+)\s*")
class fread_handler(object):
    @staticmethod
    def gen_match_str(varstr):
        return r"(?<![_A-Za-z0-9])fread\s*\(\s*"+varstr+r"([^,\(]*),([^,\(]*),([^,\(]*),([^,\(]*)\s*\)"
    @staticmethod
    def isArgDef(varstr,codestr):
        lib_definition=fread_handler.gen_match_str(varstr)
        m=re.search(lib_definition,codestr)
        if m is None:
            return False
        else:
            return True
    @staticmethod
    def getJobs(i,varstr,codestr):
        lib_definition=fread_handler.gen_match_str(varstr)
        m=re.search(lib_definition,codestr)
        jobs=[]
        if m:
            size=m.group(1)
            num_pattern=re.compile(r"\s*[0-9]|([1-9][0-9]+)\s*")
            if "sizeof" not in size and num_pattern.match(size) is not None:
                jobs.append(TaintJob(i,TaintVar(size,[])))
            count=m.group(2)
            if "sizeof" not in size and num_pattern.match(size) is not None:
                jobs.append(TaintJob(i,TaintVar(count,[])))
            fp=m.group(3)
            jobs.append(TaintJob(i,TaintVar(fp,['*'])))
            print "The lib call definition is handled!"
        return jobs