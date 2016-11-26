'''
Created on Oct 29, 2015

@author: yangke
'''
from model.TaintVar import TaintVar
from TraceTrackTest import TraceTrackTest
class Test_mcrypt_salt_size:
    def test(self):
        passed_message="MCRYPT-2.6.5 '*salt_size' TEST PASSED!"
        not_pass_message="ERRORS FOUND DURING MCRYPT-2.6.5 'i' in '*salt_size' TEST!"
        answer_path='answers/mcrypt/mcrypt-2.6.5/'
        name='mcrypt-2.6.5_salt_size'
        logfile_path="gdb_logs/mcrypt/mcrypt-2.6.5/gdb-mcrypt-2.6.5_salt_size.txt"
        c_proj_path='gdb_logs/mcrypt/mcrypt-2.6.5/mcrypt-2.6.5'
        taintVars=[TaintVar("salt_size",['*'])]
        test=TraceTrackTest(answer_path,name,logfile_path,taintVars,passed_message,not_pass_message)
        test.set_c_proj_path(c_proj_path)
        passed=test.test()
        return passed

if __name__ == '__main__':
    test=Test_mcrypt_salt_size()
    test.test()

