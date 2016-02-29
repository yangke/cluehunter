'''
Created on Dec 19, 2015

@author: yangke
'''
import re
from FunctionCallInfo import FunctionCallInfo
from LineOfCode import LineOfCode
class RedundancyFixer(object):
    REMOVE_INLINE_REDUNDANT=0
    REMOVE_INTERPROCEDURAL_REDUNDANT=1
    '''
    RedundancyFixer fix the redundant problem in Trace list
    '''
    def __init__(self,l,redundancy_level=1):
        self.l=l
        self.redundancy_level=redundancy_level
    def fix(self):
        self.func_fix_redundancy()
        self.filter_complains()
        self.merge_multiline_for()
        return self.l    
    def filter_complains(self):
        new_list=[]
        complains_pattern=r"^[0-9]+\s*in .*\.[c,S]$"
        pat=re.compile(complains_pattern)
        for line in self.l:
            s=str(line)
            if not isinstance(line, FunctionCallInfo):
                if pat.match(s) or "No such file or directory." in s:
                    if len(new_list)>0 and isinstance(new_list[-1], FunctionCallInfo):
                        new_list=new_list[:-1]
                else:
                    new_list.append(line)
            else:
                new_list.append(line)   
        self.l=new_list
    def func_fix_redundancy(self):
        new_list=[]
        i=0
        while i< len(self.l):
            if isinstance(self.l[i], FunctionCallInfo):
                j=self.check_I(i)
                while j>i:
                    #print "Caught IT!",l[i]
                    i=j
                    j=self.check_I(i)
            #print "add:",i
            new_list.append(self.l[i]) 
            i+=1
        self.l=new_list
    def merge_multiline_for(self):
        #=======================================================================
        #Test case:
        #-----------------------------------------------------------------------
        # 922      for (counter = 0, set = ardata->symdefs;
        # 923           counter < ardata->symdef_count;
        # 924           counter++, set++, rbase += BSD_SYMDEF_SIZE)
        #=======================================================================
        p1=re.compile("^for\([^,;\)]+(,[^,;\)]+)*;$")
        p2=re.compile("^[^,;\)]+;$")
        p3=re.compile("^[^,;\)]+(,[^,;\)]+)*\)$")
        newlist=[]
        i=0
        while i <len(self.l)-2:
            x=None
            if isinstance(self.l[i], LineOfCode):
                if "for" in self.l[i].codestr:
                    if isinstance(self.l[i+1], LineOfCode) and isinstance(self.l[i+2], LineOfCode):
                        code1=''.join(self.l[i].codestr.split())
                        code2=''.join(self.l[i+1].codestr.split())
                        code3=''.join(self.l[i+2].codestr.split())
                        if p1.match(code1) and p2.match(code2) and p3.match(code3):
                            print self.l[i]
                            print self.l[i+1]
                            print self.l[i+2] 
                            x=self.l[i]
                            print self.l[i].codestr+code2+code3
                            x.codestr=self.l[i].codestr.rstrip()+code2+code3+"\n"
                            
            if x is not None:
                newlist.append(x)
                i+=3
            else:
                newlist.append(self.l[i])
                i+=1
        if i<len(self.l):
            newlist.append(self.l[i])
        if i+1<len(self.l):
            newlist.append(self.l[i+1])
        self.l=newlist    
    
    #Only check for FunctionCallInfo          
    def check_I(self,i):
        m=1
        while i+m<len(self.l) and str(self.l[i])!=str(self.l[i+m]):
            if self.redundancy_level==RedundancyFixer.REMOVE_INTERPROCEDURAL_REDUNDANT:
                if isinstance(self.l[i], FunctionCallInfo) and isinstance(self.l[i+m], FunctionCallInfo):
                    if re.sub(r'0x[a-fA-F0-9]+','',str(self.l[i]))==re.sub(r'0x[a-fA-F0-9]+','',str(self.l[i+m])):
                        break
            m+=1
        if i+m==len(self.l):
            return 0
        else:
            for j in range(0,m):
                if i+m+j==len(self.l):
                    return i
                if str(self.l[i+j])!=str(self.l[i+m+j]):
                    if self.redundancy_level==RedundancyFixer.REMOVE_INTERPROCEDURAL_REDUNDANT:
                        if isinstance(self.l[i+j], FunctionCallInfo) and isinstance(self.l[i+m+j], FunctionCallInfo):
                            if re.sub(r'0x[a-fA-F0-9]+','',str(self.l[i+j]))==re.sub(r'0x[a-fA-F0-9]+','',str(self.l[i+m+j])):
                                continue
                    return i
            return i+m 