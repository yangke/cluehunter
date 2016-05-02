'''
Created on Oct 7, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest
class Test_libsndfile_wav_fmt__min_blockalign:
    def test(self):
        passed_message="LIBSNDFILE-1.0.25 divide by zero 'wav_fmt->min.blockalign' TEST PASSED!"
        not_pass_message="ERRORS FOUND IN LIBSNDFILE-1.0.25 divide by zero 'wav_fmt->min.blockalign' TEST!"
        answer_path='answers/libsndfile/libsndfile-1.0.25/'
        name='libsndfile-1.0.25_wav_fmt->min.blockalign'
        logfile_path="gdb_logs/libsndfile/libsndfile-1.0.25/gdb-libsndfile-1.0.25_wav_fmt->min.blockalign.txt"
        c_proj_path="gdb_logs/libsndfile/libsndfile-1.0.25/libsndfile-1.0.25"
        taintVars=[TaintVar("wav_fmt->min.blockalign",[])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed,time_cost=test.test()
        return passed,time_cost
if __name__ == '__main__':
    test=Test_libsndfile_wav_fmt__min_blockalign()
    test.test()
    