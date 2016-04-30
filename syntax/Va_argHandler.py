'''
Created on Apr 29, 2016

@author: yangke
'''
import re
from syntax import Syntax
from model.TaintVar import TaintVar
from model.TaintJob import TaintJob
from libhandlers.ArgHandler import ArgHandler
class Va_argHandler(object):
    '''
    "Handle va_arg definition like this:"
    #e.g.
    2218        if (psf_binheader_readf (psf, "b", &buffer, SIGNED_SIZEOF (buffer)) != SIGNED_SIZEOF (buffer))
    psf_binheader_readf (psf=0x80dc008, format=0xb7fbfad9 "b") at common.c:908
    908    {    va_list            argptr ;
    917        int                byte_count = 0, count ;
    919        if (! format)
    922        va_start (argptr, format) ;
    924        while ((c = *format++))
    925        {    switch (c)
    1036                        charptr = va_arg (argptr, char*) ;
    1037                        count = va_arg (argptr, int) ;
    1038                        if (count > 0)
    1039                            byte_count += header_read (psf, charptr, count) ;
    '''
    
    def __init__(self,right,pp, rfl, i , indexes, l, TG):
        self.right=right
        self.pp=pp
        self.rfl=rfl
        self.m_va_arg=None
        self.l=l
        self.i=i
        self.indexes=indexes
        self.pat=re.compile(r'va_arg\s*\(.*\)')
        self.TG=TG
        
    def match(self):
        self.m_va_arg=self.pat.match(self.right.strip())
        return self.m_va_arg is not None
    
    def count_va_arg_order_num(self):
        count=0
        argptr_name=[]
        for i in self.indexes:
            if i>self.i:
                continue
            print i,"#",self.l[i]
            m_argptr=re.search(r'(?<![A-Za-z_0-9])va_arg\s*\(',self.l[i].codestr)
            if m_argptr:
                start_pos=m_argptr.span()[1]
                end_pos,reachend=ArgHandler.nextarg(self.l[i].codestr, start_pos)
                if reachend:
                    print "Fatal Error! var_arg() paramlist contains only one arg!",1/0
                name=self.l[i].codestr[start_pos:end_pos].strip()
                argptr_name.append(name)
                count+=1
            i-=1
        if len(set(argptr_name))!=1:
            print "Fatal Error! The first variable of var_arg() is not same!",1/0
        self.argptr_name=argptr_name[0]
        return count
    
    def count_fix_params(self):
        call_info_index=self.indexes[0]-1
        params=self.l[call_info_index].get_param_list().split(",")
        if "this" in params[0]:
            return len(params)-1 
        else:
            return len(params)   
    def get_argptr_name(self):
        return self.argptr_name
    def generate_jobs(self):
        for id in self.indexes:
            print id,self.l[id]
        base=self.count_fix_params()
        offset=self.count_va_arg_order_num()
        call_info_index=self.indexes[0]-1
        arg_pos=base+offset-1
        print arg_pos
        print self.i
        print self.l[self.i]
        self.TG.linkInnerEdges(self.i,call_info_index,self.argptr_name+"["+str(offset-1)+"]")
        taintvar=TaintVar(self.argptr_name+"["+str(offset-1)+"]",[]) #this may cause it have access pattern:'*'
        taintvar.p=[]#remove it ('*')
        return [TaintJob(call_info_index,taintvar,arg_pos)]