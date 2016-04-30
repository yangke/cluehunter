'''
Created on Apr 27, 2016

@author: yangke
'''
from parse.RecordManager import RecordManager
from parse.MacroInspector import MacroInspector
if __name__ =="__main__":
    manager=RecordManager("gdb_logs/libsndfile/libsndfile-1.0.25/gdb-libsndfile-1.0.25_wav_fmt->min.blockalign.txt")
    c_proj_dir="gdb_logs/libsndfile/libsndfile-1.0.25/libsndfile-1.0.25"
    m=MacroInspector(c_proj_dir)
    manager.set_macro_inspector(m)
    print manager.get(-1)
    for line in manager.l:
        print line
    manager.write2File("trace.txt")  