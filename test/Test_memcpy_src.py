'''
Created on Oct 7, 2015

@author: yangke
'''
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
import time
from TraceTrackTest import TraceTrackTest

class Test_memcpy_src:
    def test(self):
        passed_message="MEMCPY 'src' TEST PASSED!"
        not_pass_message="ERRORS FOUND IN MEMCPY 'src' TEST!"
        answer_path='answers/memcpy/'
        name='memcpy_src'
        logfile_path="gdb_logs/memcpy/gdb-memcpy.txt"
        taintVars=[TaintVar("src",['*'])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        passed=test.test()
        return passed

if __name__ == '__main__':
    test=Test_memcpy_src()
    test.test()
    