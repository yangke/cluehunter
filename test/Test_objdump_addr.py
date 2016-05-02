'''
Created on Oct 29, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest
class Test_objdump_addr:
    def test(self):
        passed_message="BINUTILS-2.23 'addr[1]' TEST PASSED!"
        not_pass_message="ERRORS FOUND IN BINUTILS-2.23 'addr[1]' TEST!"
        answer_path='answers/binutils/binutils-2.23/objdump/'
        name='binutils-2.23_objdump_addr'
        logfile_path="gdb_logs/binutils-2.23/binutils-2.23_objdump_gdb.txt"
        c_proj_path="gdb_logs/binutils-2.23/binutils-2.23"
        taintVars=[TaintVar("addr",['*'])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed,time_cost=test.test()
        return passed,time_cost
if __name__ == '__main__':
    test=Test_objdump_addr()
    test.test()