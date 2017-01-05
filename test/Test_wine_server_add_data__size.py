'''
Created on Oct 7, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest

class Test_wine_server_add_data__size:
    def test(self):
        passed_message="WINE-1.8.5 'size' in wine_server_add_data() TEST PASSED!"
        not_pass_message="ERRORS FOUND IN WINE-1.8.5 'size' in wine_server_add_data() TEST!"
        answer_path='answers/wine-1.8.5/'
        name='wine_server_add_data__size'
        logfile_path="gdb_logs/wine-1.8.5/gdb-wine_server_add_data__size.txt"
        c_proj_path=None
        taintVars=[TaintVar("size",[''])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed=test.test()
        return passed
if __name__ == '__main__':
    test=Test_wine_server_add_data__size()
    test.test()