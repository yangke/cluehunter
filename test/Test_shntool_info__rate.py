'''
Created on Oct 29, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest
class Test_shntool_info__rate:
    def test(self):
        passed_message="SHNTOOL-3.0.10 'info->rate' TEST PASSED!"
        not_pass_message="ERRORS FOUND DURING SHNTOOL-3.0.10 'info->rate' TEST!"
        answer_path='answers/shntool-3.0.10/'
        name='shntool-3.0.10_info__rate'
        logfile_path="gdb_logs/shntool-3.0.10/gdb-shntool-3.0.10_info__rate.txt"
        c_proj_path='gdb_logs/shntool-3.0.10/shntool-3.0.10'
        taintVars=[TaintVar("info->rate",[])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed=test.test()
        return passed
if __name__ == '__main__':
    test=Test_shntool_info__rate()
    test.test()