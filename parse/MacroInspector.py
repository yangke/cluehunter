'''
Created on Dec 24, 2015

@author: yangke
'''
import os
import re
class MacroInspector(object):
    '''
    Finde the macro expanded result of one line of C code.
    '''
    def __init__(self,project_dir):
        self.project_dir=project_dir
        
    def search(self,dstDir,fileName):
        for y in os.listdir(dstDir):
            absPath = os.path.join(dstDir,y)
            if os.path.isdir(absPath):
                try:
                    target=self.search(absPath,fileName)
                    if target is not None:
                        return target
                except BaseException, e:
                    continue
            elif (os.path.isfile(absPath) and os.path.split(absPath)[1]==fileName):
                return absPath
                #print('found %s '%absPath.decode('gbk').encode('utf-8'))

    def getExpanded(self,c_cpp_file_name, line_num):
        i_file_name=self.removeSuffix(c_cpp_file_name).strip()+".i"
        i_file_path=self.search(self.project_dir,i_file_name)
        if i_file_path is None:return None 
        i_file=open(i_file_path)
        lines=i_file.readlines()
        pat=re.compile('^# ([0-9]+) "archive.c"$')#There are source line info in *.i files 
        up=(0,1)
        for line in lines:
            m=pat.match(line)
            if m:
                source_line_num_str=m.group(1)
                if int(source_line_num_str)<line_num:
                    up=(lines.index(line)+1,int(source_line_num_str))
                elif int(source_line_num_str)==line_num:
                    return lines[lines.index(line)+1]
                else:
                    break
        return lines[up[0]+line_num-up[1]]

    def removeSuffix(self,file_name):
        a=file_name.split(".")
        if "." in file_name:
            a.pop()
        return ".".join(a)
        
if __name__ =="__main__":
    inspector=MacroInspector('/home/yangke/Program/Fabian-Yamaguchi/evdata/binutils/binutils-2.23')
    r=inspector.getExpanded('archive.c',927)
    print r   