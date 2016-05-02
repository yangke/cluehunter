'''
Created on Oct 7, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest
class Test_memcpy_dst:
       
    def test(self):
        passed_message="MEMCPY 'dst' TEST PASSED!"
        not_pass_message="ERRORS FOUND IN MEMCPY 'dst' TEST!"
        answer_path='answers/memcpy/'
        name='memcpy_dst'
        logfile_path="gdb_logs/memcpy/gdb-memcpy.txt"
        c_proj_path="gdb_logs/memcpy"
        taintVars=[TaintVar("dst",['*'])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed,time_cost=test.test()
        return passed,time_cost
    
if __name__ == '__main__':
    test=Test_memcpy_dst()
    test.test()
    