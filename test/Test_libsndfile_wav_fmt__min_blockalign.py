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
class Test_libsndfile_wav_fmt__min_blockalign:
    def test(self):
        passed_message="LIBSNDFILE-1.0.25 divide by zero 'wav_fmt->min.blockalign' TEST PASSED!"
        not_pass_message="ERRORS FOUND IN LIBSNDFILE-1.0.25 divide by zero 'wav_fmt->min.blockalign' TEST!"
        answer_path='answers/libsndfile/libsndfile-1.0.25/'
        name='libsndfile-1.0.25_wav_fmt->min.blockalign'
        logfile_path="gdb_logs/libsndfile/libsndfile-1.0.25/gdb-libsndfile-1.0.25_wav_fmt->min.blockalign.txt"
        taintVars=[TaintVar("wav_fmt->min.blockalign",[])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        passed=test.test()
        return passed
if __name__ == '__main__':
    test=Test_libsndfile_wav_fmt__min_blockalign()
    test.test()
    