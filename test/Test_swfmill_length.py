'''
Created on Oct 7, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest

class Test_swfmill_length:
    def test(self):
        passed_message="SWFMILL-0.3.3 'length' TEST PASSED!"
        not_pass_message="ERRORS FOUND IN SWFMILL-0.3.3 'length' TEST!"
        answer_path='answers/swfmill/'
        name='swfmill-0.3.3_length'
        logfile_path="gdb_logs/swfmill-0.3.3/gdb-swfmill-0.3.3__new_unsigned_char[length]_exploit_0_0.txt"
        c_proj_path='gdb_logs/swfmill-0.3.3/swfmill-0.3.3'
        taintVars=[TaintVar("length",[''])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed,time_cost=test.test()
        return passed,time_cost
if __name__ == '__main__':
    test=Test_swfmill_length()
    test.test()