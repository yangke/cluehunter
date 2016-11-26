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
        founded_file_paths=[]
        for y in os.listdir(dstDir):
            absPath = os.path.join(dstDir,y)
            if os.path.isdir(absPath):
                try:
                    paths=self.search(absPath,fileName)
                    founded_file_paths+=paths
                except BaseException, e:
                    continue
            elif (os.path.isfile(absPath) and os.path.split(absPath)[1]==fileName):
                founded_file_paths.append(absPath)
                #print('found %s '%absPath.decode('gbk').encode('utf-8'))
        return founded_file_paths
    
    def getExpanded(self,c_cpp_file_name, line_num):
        i_file_name=self.removeSuffix(c_cpp_file_name).strip()+".i"
        i_file_paths=self.search(self.project_dir,i_file_name)
        if self.project_dir is None or i_file_paths==[]:
            return None
        for i_file_path in i_file_paths:
            i_file=open(i_file_path)
            lines=i_file.readlines()
            pat=re.compile('^# ([0-9]+) "'+c_cpp_file_name+'"')#There are source line info in *.i files 
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
            #BUG: some error conditions may pass following check
            if up[0]+line_num-up[1] < len(lines):
                return lines[up[0]+line_num-up[1]]
        return None
    def removeSuffix(self,file_name):
        a=file_name.split(".")
        if "." in file_name:
            a.pop()
        return ".".join(a)
        
if __name__ =="__main__":
    #===========================================================================
    # inspector=MacroInspector('/home/yangke/Program/Fabian-Yamaguchi/evdata/binutils/binutils-2.23')
    # r=inspector.getExpanded('archive.c',927)
    #===========================================================================
    inspector=MacroInspector('/home/yangke/Program/Fabian-Yamaguchi/evdata/speex/CVE-2008-1686/speex-1.1.12')
    r=inspector.getExpanded('speex_header.c',155)
    print r   