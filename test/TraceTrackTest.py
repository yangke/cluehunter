'''
Created on Dec 13, 2015

@author: yangke
'''
import subprocess

from parse.parse import LogParser
from model.TaintVar import TaintVar
from Tracker import Tracker
import filecmp
import time

class TraceTrackTest(object):
    

    def __init__(self,answer_path,name,logfile_path,taintVars,passed_message,not_pass_message,outputdir='./testoutput/'):
        
        self.outputdir=outputdir
        self.answer_path=answer_path
        self.name=name
        self.logfile_path=logfile_path
        self.taintVars=taintVars
        self.passed_message=passed_message
        self.not_pass_message=not_pass_message
        
        
    def test_tracker(self,tracker,traceIndex):
        tracker.setStartJobs(traceIndex, self.taintVars)
        TG=tracker.track()
        output=file(self.outputdir+self.name+'.dot', 'w')
        print TG.serialize2dot()
        output.write(TG.serialize2dot())
        output.close()
        #print str(TG)
        subprocess.call("dot -Tpng '"+self.outputdir+self.name+".dot' -o '"+self.outputdir+self.name+".png'", shell = True)
        x=filecmp.cmp(self.outputdir+self.name+".dot", self.answer_path+self.name+".dot")
        self.print_message(x)
        return x
    
    def print_message(self,passed):
        if passed:
            print self.passed_message
        else:
            print self.not_pass_message
            
    def test(self):
        start = time.clock()
        parser=LogParser()
        l=parser.parse(self.logfile_path)
        tracker=Tracker(l)
        traceIndex=len(l)-1
        passed=self.test_tracker(tracker,traceIndex)
        end = time.clock()
        print "finished: %f s" % (end - start)
        return passed
    
    