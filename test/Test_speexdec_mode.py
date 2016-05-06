'''
Created on Oct 29, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest
class Test_speexdec_mode:
    def test(self):
        passed_message="SPEEX-1.1.12 'mode' TEST PASSED!"
        not_pass_message="ERRORS FOUND DURING SPEEX-1.1.12 'mode' TEST!"
        answer_path='answers/speex/CVE-2008-1686/speex-1.1.12/speexdec/'
        name='speex-1.1.12_speexdec_mode'
        logfile_path="gdb_logs/speex/CVE-2008-1686/speex-1.1.12/speexdec/gdb-speex-1.1.12_speexdec_mode.txt"
        c_proj_path='gdb_logs/speex/CVE-2008-1686/speex-1.1.12/speex-1.1.12'
        taintVars=[TaintVar("mode",['*'])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed=test.test()
        return passed
if __name__ == '__main__':
    test=Test_speexdec_mode()
    test.test()