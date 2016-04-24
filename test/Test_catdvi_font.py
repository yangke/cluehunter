'''
Created on Oct 29, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest
class Test_catdvi_font:
    def test(self):
        passed_message="CATDVI-0.14 'font' TEST PASSED!"
        not_pass_message="ERRORS FOUND DURING CATDVI-0.14 'font' TEST!"
        answer_path='answers/catdvi-0.14/catdvi/'
        name='catdvi-0.14_font'
        logfile_path="gdb_logs/catdvi-0.14/catdvi/gdb-catdvi_font.txt"
        c_proj_path='gdb_logs/catdvi-0.14/catdvi-0.14'
        taintVars=[TaintVar("font",[])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed=test.test()
        return passed
if __name__ == '__main__':
    test=Test_catdvi_font()
    test.test()