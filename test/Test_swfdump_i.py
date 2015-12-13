'''
Created on Oct 29, 2015

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
class Test_swfdump_i:
    def test(self):
        passed_message="SWFTOOLS-0.9.2 'i' in 't->data[i]' TEST PASSED!"
        not_pass_message="ERRORS FOUND DURING SWFTOOLS-0.9.2 'i' in 't->data[i]' TEST!"
        answer_path='answers/swftools-0.9.2/swfdump/'
        name='swftools-0.9.2_swfdump_i'
        logfile_path="gdb_logs/swftools-0.9.2/gdb-swfdump_t-data_i.txt"
        taintVars=[TaintVar("i",[])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        passed=test.test()
        return passed

if __name__ == '__main__':
    test=Test_swfdump_i()
    test.test()

