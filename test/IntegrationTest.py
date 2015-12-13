'''
Created on Dec 13, 2015

@author: yangke
'''
from Test_libsndfile_bytes import Test_libsndfile_bytes
from Test_libsndfile_most import Test_libsndfile_most
from test.Test_libsndfile_wav_fmt__min_blockalign import Test_libsndfile_wav_fmt__min_blockalign
from Test_memcpy_dst import Test_memcpy_dst
from Test_memcpy_src import Test_memcpy_src
from Test_swfdump_i import Test_swfdump_i
from Test_swfdump_t__data import  Test_swfdump_t__data
from Test_swfmill_length import Test_swfmill_length

class IntegrationTest:

    def test(self):
        print "Start integeration testing..."
        result_array=[]
        test=Test_libsndfile_bytes()
        result_array.append(('libsndfile_bytes',test.test()))
        test=Test_libsndfile_most()
        result_array.append(('libsndfile_most',test.test()))
        test=Test_libsndfile_wav_fmt__min_blockalign()
        result_array.append(('libsndfile_wav_fmt->min.blockalign',test.test()))
        test=Test_memcpy_dst()
        result_array.append(('memcpy_dst',test.test()))
        test=Test_memcpy_src()
        result_array.append(('memcpy_src',test.test()))
        test=Test_swfdump_i()
        result_array.append(('swfdump_i',test.test()))
        test=Test_swfdump_t__data()
        result_array.append(('swfdump_t->data',test.test()))
        test=Test_swfmill_length()
        result_array.append(('swfmill_length',test.test()))
        for r in result_array:
            print r[0],":\t",r[1]
        print "Integeration testing ended."
        
        
        
if __name__ == '__main__':
    test=IntegrationTest()
    test.test()    