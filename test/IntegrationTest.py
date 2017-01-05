'''
Created on Dec 13, 2015

@author: yangke
'''
from Test_foomoo_a import Test_foomoo_a
from Test_libsndfile_bytes import Test_libsndfile_bytes
from Test_libsndfile_most import Test_libsndfile_most
from test.Test_libsndfile_wav_fmt__min_blockalign import Test_libsndfile_wav_fmt__min_blockalign
from Test_mcrypt_salt_size import Test_mcrypt_salt_size
from Test_memcpy_dst import Test_memcpy_dst
from Test_memcpy_src import Test_memcpy_src
from Test_swfdump_i_0 import Test_swfdump_i_0
from Test_swfdump_t__data_0 import  Test_swfdump_t__data_0
from Test_swfdump_t__data_135 import  Test_swfdump_t__data_135
from Test_swfdump_t__data_137 import  Test_swfdump_t__data_137
from Test_swfdump_t__data_258 import  Test_swfdump_t__data_258
from Test_swfdump_t__data_i_0 import Test_swfdump_t__data_i_0
from Test_swfmill_length import Test_swfmill_length
from Test_objdump_addr import Test_objdump_addr
from Test_swfmill_data__pos import Test_swfmill_data__pos
from Test_png2swf_len import Test_png2swf_len
from Test_speexenc_channel import Test_speexenc_channel
from Test_speexdec_mode import Test_speexdec_mode
from Test_speexdec_modeID import Test_speexdec_modeID
from Test_catdvi_font import Test_catdvi_font
from Test_shntool_info__rate import Test_shntool_info__rate
from Test_wine_server_add_data__size import Test_wine_server_add_data__size

import datetime
class IntegrationTest:

    def test(self):
        print "Start integeration test ..."
        t0=datetime.datetime.now()
        result_array=[]
        test=Test_foomoo_a()
        result_array.append(('foomoo',test.test()))
        test=Test_libsndfile_bytes()
        result_array.append(('libsndfile_bytes',test.test()))
        test=Test_libsndfile_most()
        result_array.append(('libsndfile_most',test.test()))
        test=Test_libsndfile_wav_fmt__min_blockalign()
        result_array.append(('libsndfile_wav_fmt->min.blockalign',test.test()))
        test=Test_mcrypt_salt_size()
        result_array.append(('mcrypt *salt_size',test.test()))
        test=Test_memcpy_dst()
        result_array.append(('memcpy_dst',test.test()))
        test=Test_memcpy_src()
        result_array.append(('memcpy_src',test.test()))
        test=Test_swfdump_i_0()
        result_array.append(('swfdump_i_0',test.test()))
        test=Test_swfdump_t__data_0()
        result_array.append(('swfdump_t->data_0',test.test()))
        test=Test_swfdump_t__data_135()
        result_array.append(('swfdump_t->data_135',test.test()))
        test=Test_swfdump_t__data_137()
        result_array.append(('swfdump_t->data_137',test.test()))
        test=Test_swfdump_t__data_258()
        result_array.append(('swfdump_t->data_258',test.test()))
        test=Test_swfdump_t__data_i_0()
        result_array.append(('swfdump_t->data[i]_0',test.test()))
        test=Test_png2swf_len()
        result_array.append(('png2swf_len',test.test()))
        test=Test_swfmill_length()
        result_array.append(('swfmill_length',test.test()))
        test=Test_swfmill_data__pos()
        result_array.append(('swfmill_data[pos++]',test.test()))
        test=Test_speexenc_channel()
        result_array.append(('speexenc_channel',test.test()))
        test=Test_speexdec_mode()
        result_array.append(('speexdec_mode',test.test()))
        test=Test_speexdec_modeID()
        result_array.append(('speexdec_modeID',test.test()))
        test=Test_catdvi_font()
        result_array.append(('catdvi_font[]',test.test()))
        #test=Test_objdump_addr()
        #result_array.append(('objdump_addr',test.test()))
        test=Test_shntool_info__rate()
        result_array.append(('shntool_info->rate',test.test()))
        test=Test_wine_server_add_data__size()
        result_array.append(('wine-1.8.5 wine_server_add_data() size',test.test()))
        
        for r in result_array:
            print r[0],":\t",r[1]
        t1=datetime.datetime.now()
        print "Integeration test ended."
        print "total time:",t1-t0
        
        
        
        
if __name__ == '__main__':
    test=IntegrationTest()
    test.test()    