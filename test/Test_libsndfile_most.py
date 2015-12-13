'''
Created on Oct 7, 2015

@author: yangke
'''
import os
import re
import subprocess
from model.TaintGraph import TaintGraph
from parse.parse import LogParser
from model.TaintJob import TaintJob
from model.TaintVar import TaintVar
from parse.FunctionCallInfo import FunctionCallInfo
from parse.LineOfCode import LineOfCode
from utils.Filter import Filter
from Tracker import Tracker
import filecmp
from numpy import diff
import time
from TraceTrackTest import TraceTrackTest
class Test_libsndfile_most:
    def test(self):
        passed_message="LIBSNDFILE-1.0.19 'most' TEST PASSED!"
        not_pass_message="ERRORS FOUND IN LIBSNDFILE-1.0.19 'most' TEST!"
        answer_path='answers/libsndfile/libsndfile-1.0.19-CVE-2009-1788/'
        name='libsndfile-1.0.19_most'
        logfile_path="gdb_logs/libsndfile/libsndfile-1.0.19-CVE-2009-1788/gdb-libsndfile-1.0.19.txt"
        taintVars=[TaintVar("most",[])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        passed=test.test() 
        return passed     
if __name__ == '__main__':
    test=Test_libsndfile_most()
    test.test()
    
    