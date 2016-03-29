'''
Created on Dec 19, 2015

@author: yangke
'''
import re
from FunctionCallInfo import FunctionCallInfo
from LineOfCode import LineOfCode
import datetime
class RedundancyFixer(object):
    REMOVE_INLINE_REDUNDANT=0
    REMOVE_INTERPROCEDURAL_REDUNDANT=1
    '''
    RedundancyFixer fix the redundant problem in Trace list
    '''
    def fixBlock(self,blockOfNormalLines):
        if blockOfNormalLines==[]:
            return []
        linenum = blockOfNormalLines[-1].get_linenum()
        lines=sorted(list(set(blockOfNormalLines)),key=lambda line:line.get_linenum(),reverse=False)
        return [ x for x in lines if x.get_linenum()<=linenum]
    def fixCodeBlock(self):
        new_list=[]
        i=0
        while i<len(self.l):
            new_list.append(self.l[i])
            i+=1
            block=[]
            while i<len(self.l) and  isinstance(self.l[i], LineOfCode):
                block.append(self.l[i])
                i+=1
            new_list.extend(self.fixBlock(block))
        self.l=new_list
    def __init__(self,l,redundancy_level=1):
        self.l=l
        self.d=dict()
        self.funcInfoIndexes=[]
        self.redundancy_level=redundancy_level
    def fix(self):
        self.func_fix_redundancy()
        now0 = datetime.datetime.now()
        self.filter_complains()
        now1 = datetime.datetime.now()
        print "filter complains time:",now1-now0
        self.merge_multiline_for()
        now2 = datetime.datetime.now()
        print "merge_multiline time:",now2-now1
        self.fixCodeBlock()
        now3 = datetime.datetime.now()
        print "fixCodeBlock time:",now3-now2
        return self.l
    def createIndex(self):
        for i,line in enumerate(self.l):  
            if isinstance(line, FunctionCallInfo):
                key_str=line.ignore_param_value_str()
                if key_str not in self.d:
                    self.d[key_str]=set()
                self.d[key_str].add(i)
                self.funcInfoIndexes.append(i)
        for key_str in self.d.keys():
            self.d[key_str]=sorted(list(self.d[key_str]))
    def filter_complains(self):
        new_list=[]
        complains_pattern=r"^[0-9]+\s*in .*\.[c,S]$"
        pat=re.compile(complains_pattern)
        for i,line in enumerate(self.l):
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
    def bsearch(self,a,m):  
        low = 0   
        high = len(a) - 1   
        while(low <= high):  
            mid = (low + high)/2  
            midval = a[mid]
            if midval < m:  
                low = mid + 1   
            elif midval > m:  
                high = mid - 1   
            else: 
                return mid   
        print 1/0  
        return -1
    def check_func_info_same(self,nxt,x,idxes):
        m=idxes[x]-idxes[nxt-1]
        interval=x-(nxt-1)
        for i in range(nxt,x):
            former=idxes[i]
            latter=idxes[i+interval]
            if latter-former!=m:
                return False
            elif latter+m>len(self.l)-1:
                return False
            #===================================================================
            # former=idxes[i]
            # latter=idxes[i]+m
            # if latter>len(self.l)-1:
            #     return False
            # if not isinstance(self.l[latter],FunctionCallInfo):
            #     return False
            #===================================================================
            elif str(self.l[former])!=str(self.l[latter]):
                if self.redundancy_level==RedundancyFixer.REMOVE_INTERPROCEDURAL_REDUNDANT:
                    if not isinstance(self.l[former],FunctionCallInfo):
                        print 1/0
                    if self.l[former].ignore_param_value_str()==self.l[latter].ignore_param_value_str():
                        continue
                return False
        return True       
    def func_fix_redundancy(self):
        now0 = datetime.datetime.now()
        self.createIndex()
        now1 = datetime.datetime.now()
        print "index creation time:",now1-now0
        new_list=[]
        start=0
        j=-1
        k=0
        
        while k<len(self.funcInfoIndexes)-1:
            index=self.funcInfoIndexes[k]
        #=======================================================================
        # for index in self.funcInfoIndexes:
        #     if index < start:
        #         continue
        #=======================================================================
            key_str=self.l[index].ignore_param_value_str()
            idxes = self.d[key_str]#increase order
            if index==idxes[-1]:
                k+=1
                continue
            nxt = self.bsearch(idxes,index)+1
            for x in range(nxt,nxt+(len(idxes)-nxt+1)/2):
                if x == nxt and nxt < len(idxes)-1 and idxes[nxt]-index > idxes[nxt+1]-idxes[nxt]:
                    continue
                if not self.check_func_info_same(nxt,x,idxes):
                    continue
                j=self.check_same(index,idxes[x]-index)
                if j>index:
                    break 
            if j>index:
                print "a jump from ",index, "to", j
                for i in range(start,index):#start#...#index#......#j#......
                    new_list.append(self.l[i])
                start=j
                k=self.bsearch(self.funcInfoIndexes, j)
                print "jump",k
                if k==-1:
                    print 1/0
            else:
                k+=1
                print "inc+1",k
                
        for i in range(start,len(self.l)):
            new_list.append(self.l[i])    
        self.l=new_list
        now2 = datetime.datetime.now()
        print "fix redundancy time:",now2-now1
    def check_same(self,i,m):
        if len(self.l)-i>2*m:#optimization
            for j in range(0,m)[::-1]:
                former=i+j
                latter=i+m+j
                if str(self.l[former])!=str(self.l[latter]):
                    if self.redundancy_level==RedundancyFixer.REMOVE_INTERPROCEDURAL_REDUNDANT:
                        #have a weak equal check when removing interprocedural redundancy 
                        if isinstance(self.l[former], FunctionCallInfo) and isinstance(self.l[latter], FunctionCallInfo):
                            #if re.sub(r'0x[a-fA-F0-9]+','',str(self.l[former]))==re.sub(r'0x[a-fA-F0-9]+','',str(self.l[latter])):
                            if self.l[former].ignore_param_value_str()==self.l[latter].ignore_param_value_str():
                                continue
                    return i
            i=i+m
        return i
                     
    def func_fix_redundancy2(self):
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
                #have a weak equal check when removing interprocedural redundancy 
                if isinstance(self.l[i], FunctionCallInfo) and isinstance(self.l[i+m], FunctionCallInfo):
                    #if re.sub(r'0x[a-fA-F0-9]+','',str(self.l[i]))==re.sub(r'0x[a-fA-F0-9]+','',str(self.l[i+m])):
                    if self.l[i].ignore_param_value_str()==self.l[i+m].ignore_param_value_str():
                        break
            m+=1
            if len(self.l)-i<2*m:#optimization
                return i
        while len(self.l)-i>2*m:#optimization
            for j in range(0,m)[::-1]:
                former=i+j
                latter=i+m+j
                #===============================================================
                # if latter==len(self.l):
                #     return i
                #===============================================================
                if str(self.l[former])!=str(self.l[latter]):
                    if self.redundancy_level==RedundancyFixer.REMOVE_INTERPROCEDURAL_REDUNDANT:
                        #have a weak equal check when removing interprocedural redundancy 
                        if isinstance(self.l[former], FunctionCallInfo) and isinstance(self.l[latter], FunctionCallInfo):
                            #if re.sub(r'0x[a-fA-F0-9]+','',str(self.l[former]))==re.sub(r'0x[a-fA-F0-9]+','',str(self.l[latter])):
                            if self.l[former].ignore_param_value_str()==self.l[latter].ignore_param_value_str():
                                continue
                    return i
            i=i+m
        return i 
        #=======================================================================
        # if i+m==len(self.l):
        #     return i
        # else:
        #     for j in range(0,m):
        #         if i+m+j==len(self.l):
        #             return i
        #         if str(self.l[i+j])!=str(self.l[i+m+j]):
        #             if self.redundancy_level==RedundancyFixer.REMOVE_INTERPROCEDURAL_REDUNDANT:
        #                 #have a weak equal check when removing interprocedural redundancy 
        #                 if isinstance(self.l[i+j], FunctionCallInfo) and isinstance(self.l[i+m+j], FunctionCallInfo):
        #                     if re.sub(r'0x[a-fA-F0-9]+','',str(self.l[i+j]))==re.sub(r'0x[a-fA-F0-9]+','',str(self.l[i+m+j])):
        #                         continue
        #             return i
        #     return i+m
        #=======================================================================
