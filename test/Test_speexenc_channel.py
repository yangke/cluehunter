'''
Created on Oct 29, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest
class Test_speexenc_channel:
    def test(self):
        passed_message="SPEEX-1.2rc2 'channel' TEST PASSED!"
        not_pass_message="ERRORS FOUND DURING SPEEX-1.2rc2 'channnel' TEST!"
        answer_path='answers/speex/speex-1.2rc2/speexenc/'
        name='speex-1.2rc2_speexenc_channel'
        logfile_path="gdb_logs/speex/speex-1.2rc2/speexenc/gdb-speex-1.2rc2_speexenc_channel.txt"
        c_proj_path='gdb_logs/speex/speex-1.2rc2/speex-1.2rc2'
        taintVars=[TaintVar("channel",[])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed=test.test()
        return passed
if __name__ == '__main__':
    test=Test_speexenc_channel()
    test.test()