'''
Created on Dec 13, 2015

@author: yangke
'''
import subprocess

from parse.RecordManager import RecordManager
from Tracker import Tracker
import filecmp
import datetime
import os
from parse.MacroInspector import MacroInspector

class TraceTrackTest(object):
    
    def __init__(self,answer_path,name,logfile_path,taintVars,passed_message,not_pass_message,outputdir='./testoutput/'):
        
        self.outputdir=outputdir
        self.answer_path=answer_path
        self.name=name
        self.logfile_path=logfile_path
        self.taintVars=taintVars
        self.passed_message=passed_message
        self.not_pass_message=not_pass_message
        self.c_proj_dir=None
        
    def set_c_proj_path(self,c_proj_path):
        self.c_proj_dir=c_proj_path
        
    def test_tracker(self,tracker,traceIndex):
        tracker.setStartJobs(traceIndex, self.taintVars)
        TG=tracker.track()
        output=file(self.outputdir+self.name+'.dot', 'w')
        print TG.serialize2dot()
        output.write(TG.serialize2dot())
        output.close()
        #print str(TG)
        subprocess.call("dot -Tsvg '"+self.outputdir+self.name+".dot' -o '"+self.outputdir+self.name+".svg'", shell = True)
        if os.path.exists(self.answer_path+self.name+".dot"):
            x=filecmp.cmp(self.outputdir+self.name+".dot", self.answer_path+self.name+".dot")
        elif os.path.exists(self.answer_path+self.name+"_level0.dot"):
            x=filecmp.cmp(self.outputdir+self.name+".dot", self.answer_path+self.name+"_level0.dot")
            if not x:
                if os.path.exists(self.answer_path+self.name+"_level1.dot"):
                    x=filecmp.cmp(self.outputdir+self.name+".dot", self.answer_path+self.name+"_level1.dot")
        self.print_message(x)
        return x
    
    def print_message(self,passed):
        if passed:
            print self.passed_message
        else:
            print self.not_pass_message
      
    def test(self,start_line_num=None):
        start = datetime.datetime.now()#time.clock()
        macro_inspector=MacroInspector(self.c_proj_dir)
        rm=RecordManager(start_line_num, self.logfile_path, macro_inspector)
        rm.fetchSome()
        tracker=Tracker(rm)
        traceIndex=-1
        passed=self.test_tracker(tracker,traceIndex)
        end = datetime.datetime.now()
        print "Time cost:",end-start
        return passed
    
    