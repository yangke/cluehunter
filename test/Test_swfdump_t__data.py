'''
Created on Oct 29, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest
class Test_swfdump_t__data:
    def test(self):
        passed_message="SWFTOOLS-0.9.2 't->data' in 't->data[i]' TEST PASSED!"
        not_pass_message="ERRORS FOUND DURING SWFTOOLS-0.9.2 't->data' in 't->data[i]' TEST!"
        answer_path='answers/swftools-0.9.2/swfdump/'
        name='swftools-0.9.2_swfdump_t-data'
        logfile_path="gdb_logs/swftools-0.9.2/swfdump/gdb-swfdump_t-data_i.txt"
        c_proj_path='gdb_logs/swftools-0.9.2/swftools-0.9.2'
        taintVars=[TaintVar("t->data",["*"])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        c_proj_path='gdb_logs/swftools-0.9.2/swftools-0.9.2'
        passed=test.test()
        return passed
if __name__ == '__main__':
    test=Test_swfdump_t__data()
    test.test()