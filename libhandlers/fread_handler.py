'''
Created on Dec 13, 2015

@author: yangke
'''
from model.TaintJob import TaintJob
from model.TaintVar import TaintVar
import re
from libhandlers.ArgHandler import ArgHandler
num_pattern=re.compile(r"\s*[0-9]|([1-9][0-9]+)\s*")
from utils.Filter import Filter
class fread_handler(object):
    @staticmethod
    def gen_match_str(variable):
        access=variable.accessStr()
        if '|' not in access:
            return r"(?<![_A-Za-z0-9])fread\s*\(\s*&\s*"+access+r"([^,\(]*),"
        else:
            pointerstr=variable.pointerStr()
            return r"(?<![_A-Za-z0-9])fread\s*\(\s*"+pointerstr+r"([^,\(]*),"
    @staticmethod
    def isArgDef(variable,codestr):
        lib_definition=fread_handler.gen_match_str(variable)
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
            startpos=m.span()[1]
            endpos,reachend=ArgHandler.nextarg(codestr,startpos)
            if reachend:
                print "Fatal Error the fread third argument is missing.",1/0
            size=codestr[startpos:endpos]
            varstrs=Filter.expression2vars(size)
            for v in varstrs:
                jobs.append(TaintJob(i,TaintVar(v,[])))
            startpos=endpos+1
            endpos,reachend=ArgHandler.nextarg(codestr,startpos)
            if reachend:
                print "Fatal Error the fread fourth argument is missing.",1/0
            count=codestr[startpos:endpos]
            varstrs=Filter.expression2vars(count)
            for v in varstrs:
                jobs.append(TaintJob(i,TaintVar(v,[])))
            startpos=endpos+1
            endpos,reachend=ArgHandler.nextarg(codestr,startpos)
            if not reachend:
                print "Fatal Error the fread have 4 argument, at least five argument detected here!",1/0
            fp=codestr[startpos:endpos]
            varstrs=Filter.expression2vars(fp)
            for v in varstrs:
                jobs.append(TaintJob(i,TaintVar(v,[])))
            print "The fread is handled!"
        return jobs