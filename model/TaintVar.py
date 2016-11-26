'''
Created on Dec 13, 2015

@author: yangke
'''
import re
class TaintVar:
    
    def __init__(self,s,p,rfl=0,varpart_ref=False):
        if re.search(r"/|\+|\-(?!>)",s):
            print "Wrong variable string! Expression detected! Please parse it to variable!"
            print 1/0
        self.v="".join(s.split())
        if self.v=='':
            print "Variable initialization meet EMPTY STRING!"
            print 1/0
        self.p=p   #data_access_pattern
        print "Init Variable:",self.v,self.p
        if "t1.next"==self.v:
            print "IJ"
        self.ref_len=rfl#for parameter 'prev', data access pattern '*(prev->next->data)'
        #prev->next=... is valid assignment and prev=... is invalid assignment.
        #why? because the valid modifation length for prev is 1
        #Name this length as 'rfl' here        
        if rfl>0:
            varpart_ref=True
        self.make_match_easier(varpart_ref)
        self.fixNaivePointer()
    def fixNaivePointer(self):
        if not self.p or self.p==[]:
            if re.search("ptr|pointer", self.v):
                self.p=["*"]
    def make_match_easier(self,varpart_ref):
        t=self.v
        while re.search(r"&|\*|\.|\->|\(|\)",t):
            if t[0]=="(" and t[-1]==")":
                t=t[1:len(t)-1]
            elif t[0]=="&":
                t=t[1:]
                self.dereference()
            elif t[0]=="*":
                t=t[1:]
                self.reference()
            else:
                i=len(t)-1
                while re.search(r"[_A-Za-z0-9]",t[i]):
                    i-=1
                if t[i]==")":
                    print self.v
                    print "BUUUUUUUUUG! bracket missmatch!",1/0
                elif t[i]==">":
                    self.p.append("->"+t[i+1:])
                    t=t[:i-1]
                    if varpart_ref:
                        self.inc_ref_len()
                elif t[i]==".":
                    self.p.append("."+t[i+1:])
                    t=t[:i]
                    #===========================================================
                    # if varpart_ref:
                    #     self.ref_len+=1
                    #===========================================================
        if t.strip()=='':
            print 1/0
        self.v=t             
    def sandwitch(self,astr):
        return r'(?<![_A-Za-z0-9])'+astr+r'(?![_A-Za-z0-9])'
    
    def pointerStr(self):
        pp=[a for a in self.p]
        have_pointer=False
        for i,a in enumerate(pp):
            if a=="*" or "->" in a:
                if i+1<=len(pp):
                    pp=pp[i+1:]
                    have_pointer=True
                    break
                else:
                    return None
        if  have_pointer:
            access=self.extractAccessPattern(pp,self.v,0)
            return self.sandwitch(access)
        return None
    def accessStr(self):
        pp=[a for a in self.p]
        access=self.extractAccessPattern(pp,self.v,self.ref_len)
        return self.sandwitch(access)
    
    def simple_access_str(self):
        pp=[a for a in self.p]
        access=self.extract_simple_access_pattern(pp,self.v,self.ref_len)
        return access
    
    def extract_simple_access_pattern(self,pp,v,rfl):
        S=[v]
        if rfl>0:
            pattern=[]
        else:
            pattern=[v]
        if len(pp)>0:
            x = pp.pop()
            while x:
                #priority high to low . -> *
                A=[]
                for s in S:
                    if ("->" in x or "." in x) and s[0]==r"*":
                        A.append(r"\("+s+r"\)"+x)#(*a->b,->c)=>(*a->b)->c
                    elif x == "*":
                        A.append(r"*\("+s+r"\)")#(*a->b,*)=>*(*a->b)
                        A.append(r"*"+s)      #(*a->b,*)=>**a->b
                    else:
                        A.append(s+x)
                S=A
                if not "." in x:
                    rfl-=1
                if rfl>0:
                    pattern=S
                else:
                    pattern+=S
                if len(pp)==0:break
                x = pp.pop()
        if pattern==[]:
            return None
        pattern.sort(key=len,reverse=True)
        return "|".join(pattern)
    
    def extractAccessPattern(self,pp,v,rfl):
        S=[v]
        if rfl>0:
            pattern=[]
        else:
            pattern=[v]
        if len(pp)>0:
            x = pp.pop()
            while x:
                #priority high to low . -> *
                A=[]
                for s in S:
                    if ("->" in x or "." in x) and s[0:2]=="\*":
                        A.append(r"\(\s*"+s+r"\s*\)\s*"+"\\"+x)#(*a->b,->c)=>(*a->b)->c
                    elif x == "*":
                        A.append(r"\*\s*\(\s*"+s+r"\s*\)")#(*a->b,*)=>*(*a->b)
                        A.append(r"\*\s*"+s)              #(*a->b,*)=>**a->b
                        A.append(s+r"\s*\[[^\[\]]+\]")
                    else:
                        A.append(s+r"\s*"+x)
                S=A
                if not "." in x:
                    rfl-=1
                if rfl>0:
                    pattern=S
                else:
                    pattern+=S
                if len(pp)==0:break
                x = pp.pop()
        if pattern==[]:
            return None
        pattern.sort(key=len,reverse=True)
        return "(("+")|(".join(pattern)+"))"
    
    def inc_ref_len(self):
        self.ref_len+=1
        if self.ref_len>len(self.p):
            self.ref_len=len(self.p)
            print "ref_len inc overflow!","reset to:",self.ref_len#,1/0
        
    def dec_ref_len(self):
        self.ref_len-=1
        if self.ref_len<0:
            self.ref_len=0
            print "ref_len dec overflow!","reset to:",self.ref_len#,1/0
    def reference(self):
        if len(self.p)>0 and self.p[-1].strip()[0]=='.':
            self.p[-1]=self.p[-1].replace('.','->')
        else:
            self.p.append('*')
        self.inc_ref_len()
        
    def dereference(self):
        if len(self.p)>0:
            if '->' in self.p[-1]:
                self.p[-1]=self.p[-1].replace('->','.')
                self.dec_ref_len()
            elif '*' in self.p[-1]:
                self.p.pop()
                self.dec_ref_len()
            else:
                print "Dereferece Failed:",self.v,self.p
                print "BAD Case in Finding All POINTER REFERENCES maybe caught: access(c.b) c=&a; OR access(c) c=&a;"
                print 1/0
    def searchByRegexSet(self,R,identifier):
        for r in R:
            if re.search(r,identifier):
                return r
        return None
    def matchAccessPattern(self,identifier):
        #Can not handle the bracket style:*(t->b).m
        identifier="".join(identifier.split())
        pp=[a for a in self.p]
        s=self.v
        rfl=self.ref_len
        if s in identifier:
            last=s
            while s is not None and len(pp)>0:
                x = pp.pop()
                if not "." in x:
                    rfl-=1
                if ("->" in x or "." in x) and s[0:2]==r"\*":
                    A=[r"\(\s*"+s+r"\s*\)\s*"+x]
                elif x == "*":
                    A=[r"\*\s*\(\s*"+s+r"\s*\)",r"\*\s*"+s]
                else:
                    A=[s+r"\s*"+x]
                s=self.searchByRegexSet(A,identifier)
                if s:last=s
            
            span=re.search(last,identifier).span()
            right_remain=identifier[span[1]:]
            print right_remain
            suffix_remain=re.search(r"[A-Za-z0-9_]",right_remain)
            if suffix_remain:
                if s:#pp==[]
                    return 0,[]
                else:
                    return None#match candidate: a->d curent match var: a->b
            else:
                if s:
                    if identifier[0]=='&':
                        return 1,['*']
                    else:
                        return 0,[]
                else:
                    if "." not in x:
                        rfl+=1
                    if identifier[0]=='&':
                        if '.' in x:# m=&(a.b)-------->m->b
                            x=x.replace('.','->')
                            pp.append(x)
                        else:#m=&(a->b)----------->(*m)->b
                            pp.append(x)
                            pp.append('*')
                        rfl+=1
                    else:
                        pp.append(x) 
                    return rfl,pp    
        else:
            return None

    def __str__(self):
        return self.v+self.accessStr()
    def __hash__(self):
        return hash(str(self))
    def __eq__(self,obj):
        return str(self)==str(obj)