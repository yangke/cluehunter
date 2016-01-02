'''
Created on Oct 29, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest
class Test_png2swf_len:
    def test(self):
        passed_message="SWFTOOLS-0.9.2 'i' in 'len' TEST PASSED!"
        not_pass_message="ERRORS FOUND DURING SWFTOOLS-0.9.2 'i' in 'len' TEST!"
        answer_path='answers/swftools-0.9.2/png2swf/'
        name='swftools-0.9.2_png2swf_len'
        logfile_path="gdb_logs/swftools-0.9.2/png2swf/gdb-png2swf_len.txt"
        c_proj_path='gdb_logs/swftools-0.9.2/swftools-0.9.2'
        taintVars=[TaintVar("len",[])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed=test.test(-2)
        return passed

if __name__ == '__main__':
    test=Test_png2swf_len()
    test.test()

