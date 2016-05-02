'''
Created on Oct 7, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest
class Test_libsndfile_bytes:
    def test(self):
        passed_message="LIBSNDFILE-1.0.19 'bytes' TEST PASSED!"
        not_pass_message="ERRORS FOUND IN LIBSNDFILE-1.0.19 'bytes' TEST!"
        answer_path='answers/libsndfile/libsndfile-1.0.19-CVE-2009-1788/'
        name='libsndfile-1.0.19_bytes'
        logfile_path="gdb_logs/libsndfile/libsndfile-1.0.19-CVE-2009-1788/gdb-libsndfile-1.0.19.txt"
        c_proj_path="gdb_logs/libsndfile/libsndfile-1.0.19-CVE-2009-1788/libsndfile-1.0.19"
        taintVars=[TaintVar("bytes",[])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed,time_cost=test.test()
        return passed,time_cost
        
           
if __name__ == '__main__':
    test=Test_libsndfile_bytes()
    test.test()
    