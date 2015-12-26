'''
Created on Oct 7, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest

class Test_memcpy_src:
    def test(self):
        passed_message="MEMCPY 'src' TEST PASSED!"
        not_pass_message="ERRORS FOUND IN MEMCPY 'src' TEST!"
        answer_path='answers/memcpy/'
        name='memcpy_src'
        logfile_path="gdb_logs/memcpy/gdb-memcpy.txt"
        c_proj_path="gdb_logs/memcpy"
        taintVars=[TaintVar("src",['*'])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed=test.test()
        return passed

if __name__ == '__main__':
    test=Test_memcpy_src()
    test.test()
    