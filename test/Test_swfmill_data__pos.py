'''
Created on Oct 7, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest

class Test_swfmill_data__pos:
    def test(self):
        passed_message="SWFMILL-0.3.3 'data[pos++]' TEST PASSED!"
        not_pass_message="ERRORS FOUND IN SWFMILL-0.3.3 'data' TEST!"
        answer_path='answers/swfmill/'
        name='swfmill-0.3.3_data__pos'
        logfile_path="gdb_logs/swfmill-0.3.3/gdb-swfmill-0.3.3_data[pos++].txt"
        c_proj_path='gdb_logs/swfmill-0.3.3/swfmill-0.3.3'
        taintVars=[TaintVar("r",['->pos'])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed=test.test(-8)
        return passed
if __name__ == '__main__':
    test=Test_swfmill_data__pos()
    test.test()