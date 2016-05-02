'''
Created on Oct 29, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest
class Test_swfstrings_fonts_t:
    def test(self):
        passed_message="SWFTOOLS-0.9.2 'fonts[t]->id' TEST PASSED!"
        not_pass_message="ERRORS FOUND DURING SWFTOOLS-0.9.2 'fonts[t]->id' TEST!"
        answer_path='answers/swftools-0.9.2/swfstrings/'
        name='swftools-0.9.2_swfstrings_fonts_t'
        logfile_path="gdb_logs/swftools-0.9.2/swfstrings/gdb-swfstrings_fonts_t.txt"
        c_proj_path='gdb_logs/swftools-0.9.2/swftools-0.9.2'
        taintVars=[TaintVar("fonts",['*']),TaintVar("t",[])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed,time_cost=test.test()
        return passed,time_cost
if __name__ == '__main__':
    test=Test_swfstrings_fonts_t()
    test.test()