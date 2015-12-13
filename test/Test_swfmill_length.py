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

class Test_swfmill_length:
    def test(self):
        passed_message="SWFMILL-0.3.3 'length' TEST PASSED!"
        not_pass_message="ERRORS FOUND IN SWFMILL-0.3.3 'length' TEST!"
        answer_path='answers/swfmill/'
        name='swfmill-0.3.3_length'
        logfile_path="gdb_logs/swfmill-0.3.3/gdb-swfmill-0.3.3.txt"
        taintVars=[TaintVar("length",[''])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        passed=test.test()
        return passed
if __name__ == '__main__':
    test=Test_swfmill_length()
    test.test()