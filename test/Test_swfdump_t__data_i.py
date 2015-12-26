'''
Created on Oct 29, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest
class Test_swfdump_t__data_i:
    def test(self):
        passed_message="SWFTOOLS-0.9.2 't->data[i]' TEST PASSED!"
        not_pass_message="ERRORS FOUND DURING SWFTOOLS-0.9.2 't->data[i]' TEST!"
        answer_path='answers/swftools-0.9.2/swfdump/'
        name='swftools-0.9.2_swfdump_t-data_i'
        logfile_path="gdb_logs/swftools-0.9.2/gdb-swfdump_t-data_i.txt"
        c_proj_path='gdb_logs/swftools-0.9.2/swftools-0.9.2'
        taintVars=[TaintVar("t->data",["*"]),TaintVar("i",[])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed=test.test()
        return passed

if __name__ == '__main__':
    test=Test_swfdump_t__data_i()
    test.test()