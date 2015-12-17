'''
Created on Nov 1, 2015

@author: yangke
'''
import re
from libhandlers.memcpy_handler import memcpy_handler
from libhandlers.memset_handler import memset_handler
from libhandlers.fread_handler import fread_handler
from libhandlers.read_handler import read_handler
from libhandlers.strcpy_handler import strcpy_handler
from libhandlers.strncpy_handler import strncpy_handler
from model.TaintJob import TaintJob
from model.TaintVar import TaintVar
from utils.Filter import Filter
class Syntax(object):
    NORMAL_ASSIGN=128
    OP_ASSIGN=64
    REF_ASSIGN=32
    INC=16
    RAW_DEF=8
    SYS_LIB_DEF=4
    FOR=2
    NODEF=0
    keyword="if|while|switch|for|goto|return|sizeof|instanceof|label|case|class|struct|int|float|long|usigned|double|char"
    identifier=r'([_A-Za-z][_A-Za-z0-9]*)'
    water=r'\s*'
    variable=r'('+identifier+'*('+water+'(\-'+water+'>|\.)'+water+identifier+')*)'
    lt=r'(?<![_A-Za-z0-9])'
    rt=r'(?![_A-Za-z0-9])'
    number=r'([+-]?([0-9]*\.?[0-9]+|[0-9]+\.?[0-9]*)([eE][+-]?[0-9]+)?)'
    constant_variable=r'([A-Z_][A-Z0-9_]*)'
    constant=r'('+constant_variable+r'|'+number+r')'
    for_pattern=r"for\s*([^;]*;[^;]*;[^;]*)";
    @staticmethod
    def isKeyWord(codestr):
        pattern=re.compile(Syntax.keyword)
        if pattern.match(codestr.strip()):
            return True
        else:return False
    @staticmethod
    def left_ref_propagate_pattern(v):
        pstr=v.pointerStr()
        astr=v.accessStr()
        if pstr:
            pat=r"(&"+Syntax.water+astr+"|"+pstr+")"
        elif astr:
            pat=r"&"+Syntax.water+astr
        else:
            print "Fatal Error! v.accessStr() return None"
            x=1/0
            return None
        return Syntax.lt+Syntax.variable+Syntax.water+r"="+Syntax.water+pat+Syntax.water+r";"
    @staticmethod
    def right_ref_propagate_pattern(v):
        pstr=v.pointerStr()
        if pstr:
            return Syntax.lt+pstr+Syntax.water+r"="+Syntax.water+r"[&\*]?"+Syntax.water+Syntax.variable+Syntax.water+r";"
        else:
            return None
    @staticmethod
    def isVariable(varstr):
        p=re.compile(r'^'+Syntax.variable+r'$')
        return p.match(varstr.strip()) is not None
    @staticmethod
    def isForStatement(codestr):
        m=re.search(Syntax.for_pattern, codestr)
        if m:
            return True
        return False
    @staticmethod
    def matchDefiniteDefinitionType(codestr,var):
        if "fprintf" in codestr:
            print "Got it!"
        access=var.accessStr()
        print "Checking Definition Type for:",access
        #normal_assginment=r"(^|[^A_Za-z0-9_])"+access+r"\s*=[^=]"
        normal_assginment=r"(?<![A_Za-z0-9_])"+access+r"\s*(\[[^\[\]]+\])?\s*=[^=]"
        if Syntax.isForStatement(codestr):
            return Syntax.FOR
        if Syntax.isIncDef(var.v, codestr):
            return Syntax.INC
        #inc operation detection must be before the assignment.
        #because when detecting variable (i) in case such as: "for (int i=-1;i<m;i++){",
        #INC result must be returned as ForJobGenerator is only called in handle branch of INC operation
        #in "lastModification" and "CheckingArgDefinition" function.
        #This weird behavior need be fixed in future. 
        if re.search(normal_assginment,codestr):
            return Syntax.NORMAL_ASSIGN
        op_assignment=r"(?<![A_Za-z0-9_])"+access+r"\s*(\[[^\[\]]+\])?\s*[\+\-\*\/%\^\|&]\s*=[^=]"
        if re.search(op_assignment,codestr):
            return Syntax.OP_ASSIGN
        raw_definition=r"^\s*\{\s*[A-Za-z_][A-Za-z0-9_]+\s+(\*\s*)*([A-Za-z_][A-Za-z0-9_]+\s*,\s*)*"+var.v+"\s*;"
        if re.search(raw_definition, codestr):
            print "We got the raw definition!"
            return Syntax.RAW_DEF
        if Syntax.isLibArgDef(var.v,codestr):
            return Syntax.SYS_LIB_DEF
        return  Syntax.NODEF
    @staticmethod
    def matchDefinitionType(codestr,var):
        if var.v=='i':
            print "GotIt!!"
        access=var.accessStr()
        print "Checking Definition Type for:",access
        print "codestr:",codestr
        #normal_assginment=r"(^|[^A_Za-z0-9_])"+access+r"\s*=[^=]"
        normal_assginment=r"(?<![A_Za-z0-9_])"+access+r"\s*(\[[^\[\]]+\])?\s*=[^=]"
        if Syntax.isForStatement(codestr):
            return Syntax.FOR
        if Syntax.isIncDef(var.v, codestr):
            return Syntax.INC
        #inc operation detection must be before the assignment.
        #because when detecting variable (i) in case such as: "for (int i=-1;i<m;i++){",
        #INC result must be returned as ForJobGenerator is only called in handle branch of INC operation
        #in "lastModification" and "CheckingArgDefinition" function.
        #This weird behavior need be fixed in future. 
        if re.search(normal_assginment,codestr):
            pointer_def=re.compile(r"^\s*"+Syntax.identifier+r"\s*"+normal_assginment+".*")
            if pointer_def.match(codestr) and '*' in normal_assginment:
                #this is the case when finding *p=moo(p,c) where *p is the cared variable
                #because of the naive search for parameer p,c, the type infomation is losed
                #In this place we may find: int *p=&a;
                #so at this time we got the type info.
                #if there exists a long skip from the usage of p and int *p=&a;
                #then checking the reference of p is necessary as we may find a=1 in middle place;
                #just like this:
                #int *p = & a;
                #a=5
                #use(p)
                #The next search job should be 'a' relative.
                #return Syntax.REF_ASSIGN
                return Syntax.NORMAL_ASSIGN
            else:
                return Syntax.NORMAL_ASSIGN
        op_assignment=r"(?<![A_Za-z0-9_])"+access+r"\s*(\[[^\[\]]+\])?\s*[\+\-\*\/%\^\|&]\s*=[^=]"
        if re.search(op_assignment,codestr):
            return Syntax.OP_ASSIGN
        raw_definition=r"^\s*\{\s*[A-Za-z_][A-Za-z0-9_]+\s+(\*\s*)*([A-Za-z_][A-Za-z0-9_]+\s*,\s*)*"+var.v+"\s*;"
        if re.search(raw_definition, codestr):
            print "We got the raw definition!"
            return Syntax.RAW_DEF
        if Syntax.isLibArgDef(var.v,codestr):
            return Syntax.SYS_LIB_DEF
        return  Syntax.NODEF
    @staticmethod
    def isIncDef(access,codestr):
        increasement=r"("+access+r"\s*\+\+)|(\+\+\s*"+access+r")|("+access+r"\s*\-\-)|(\-\-\s*"+access+r")"
        if re.search(increasement, codestr):
            print "NORMAL INC!"
            return True
        lib_definition=r"(?<![A-Za-z0-9_])fread\s*\(\s*([^,\(]*),([^,\(]*),([^,\(]*),"+access+"([^,\(]*)\s*\)"
        if re.search(lib_definition, codestr):
            print "SYSCALL INC!"
            return True
        syscall_definition=r"(?<![A-Za-z0-9_])read\s*\(\s*"+access+"([^,\(]*),([^,\(]*),([^,\(]*)\s*\)"
        if re.search(syscall_definition, codestr):
            print "SYSCALL INC!"
            return True
        return False
    
    @staticmethod
    def isLibArgDef(varstr,codestr):
        if fread_handler.isArgDef(varstr,codestr):
            return True
        elif read_handler.isArgDef(varstr,codestr):
            return True
        elif strcpy_handler.isArgDef(varstr,codestr):
            return True
        elif strncpy_handler.isArgDef(varstr,codestr):
            return True
        elif memcpy_handler.isArgDef(varstr,codestr):
            return True
        elif memset_handler.isArgDef(varstr,codestr):
            return True
        return False
    
    @staticmethod
    def handle_sys_lib_def(i,varstr,codestr):
        jobs=[]
        yes=fread_handler.isArgDef(varstr,codestr)
        if yes:
            jobs=fread_handler.getJobs(i,varstr, codestr)
        yes=read_handler.isArgDef(varstr,codestr)
        if yes:
            jobs=read_handler.getJobs(i, varstr,codestr)
        yes=memcpy_handler.isArgDef(varstr, codestr)
        if yes:
            jobs=memcpy_handler.getJobs(i, varstr, codestr)
        yes=strncpy_handler.isArgDef(varstr, codestr)
        if yes:
            jobs=strncpy_handler.getJobs(i, varstr, codestr)
        yes=strcpy_handler.isArgDef(varstr, codestr)
        if yes:
            jobs=strcpy_handler.getJobs(i, varstr, codestr)
        yes=memset_handler.isArgDef(varstr, codestr)
        if yes:
            jobs=memset_handler.getJobs(i, varstr, codestr)
        return jobs#FIX ME: this should not happen
    
    @staticmethod
    def getVars(var,line):
        codestr=line.codestr
        str_pat=var.accessStr()+r"\s*(\[[^\[\]]+\])*\s*[\+\-\*/%&\|]?\s*=\s*(?!=)"
        print "GGGGG",str_pat
        print "CHECKING CODE:",codestr
        m=re.search(str_pat,codestr)
        if m:
            span=m.span()
            #===================================================================
            # print "hahah",codestr[:span[1]]
            # print "hahah",var
            # left=codestr[:span[1]].strip().rstrip('=').rstrip()
            # if left=="char a[2]":
            #     print "OH NO!",left
            # i=0
            # if re.search(r"[A-Za-z0-9_]+[\s|\*|\(]+[A-Za-z0-9_]+",left):
            #     while re.search(r"[A-Za-z0-9_]",left[i]):
            #         i+=1
            #     while not re.search(r"[A-Za-z0-9_]",left[i]):
            #         i+=1
            #     j=i
            #     while re.search(r"[A-Za-z0-9_]",left[j]) and j<len(left):
            #         j+=1
            #     name=left[i:j]
            # else:
            #     name=left
            # print "left var name is:",name   
            #===================================================================
            left=m.group()
            i=0
            while re.search(r"[A-Za-z0-9_\.\*\->\s]",left[i]):
                i+=1
            name="".join(left[:i].split())
            rfl,pp=var.matchAccessPattern(name)
            right=codestr[span[1]:]
            right=right.split(';')[0].strip()
            if Syntax.isVariable(right):
                if pp is None:
                    print "Fatal Error!!!"
                    return None
                else: 
                    print pp
                    return set([TaintVar(right, pp,rfl)])
            else:
                m_cond_exp=re.compile(r'^[^\?:]*\?[^\?:]*:[^\?:]*$').match(right)
                if m_cond_exp:
                    #FIX ME:
                    #CAN HANDLE: int i,m=t->len>10?10:t->len;
                    #CANNOT HANDLE: m=q+((t->len>10?10:t->len)?a:b);
                    array=right.split('?')[1].split(':')
                    choice1=Filter.expression2vars(array[0])
                    choice2=Filter.expression2vars(array[1])
                    symbols=choice1+choice2
                else:    
                    symbols=Filter.expression2vars(right)
                print symbols
                if "->id" in symbols:
                    print "------------------------"
                varstrs=Filter.filterOutFuncNames(symbols,line.codestr)
                print "Right variables in assignment:",varstrs
                return set(map(lambda x : TaintVar(x, []), varstrs))
    
    @staticmethod
    def extract_func_name(codestr,i):
        # i point to '('
        p=i-1
        while re.search("\s", codestr[p]):
            p-=1
        end=p+1
        while re.search("[_A-Za-z0-9]", codestr[p]):
            p-=1
        if p==end-1:
            return None
        return codestr[p+1:end]#func_name
    @staticmethod
    def vararg(codestr,start,end):
        if start>=end or start<0 or end>len(codestr):
            return None
        i=start
        j=end
        func_name=None
        func_name_suffix_pattern=re.compile(r".*[_A-Za-z0-9]\s*$")
        bracket=False
        while True:
            i=i-1
            if i<0:return None
            if codestr[i] == "(":
                if func_name_suffix_pattern.match(codestr[:i]):
                    pos=0
                    func_name=Syntax.extract_func_name(codestr,i)
                    if Syntax.isKeyWord(func_name):
                        return None     
                    break#The only exit port pos==1
                else:
                    bracket=True 
            elif codestr[i] == "&" or codestr[i] == "*" or re.search("\s", codestr[i]):
                if bracket:
                    bracket=False
                    #FIX ME
                    #skip "..." in "&(wav_w64...)" to find the right bracket.
                    #Note that this may ignore the wrong syntax in "..." part.
                    while codestr[j]!=")":
                        j+=1
                    if codestr[j]!=")":
                        print "Fatal Error: bracket mismatch. May be like: &(a...."
                    else:
                        j=j+1
                continue
            elif codestr[i] == ",":
                pos=1
                break#second  exit port pos>1
            else:
                return None
        var_name=codestr[i+1:j]
        return pos,i,var_name,func_name
    @staticmethod
    def isPossibleArgumentDefinition(line,var):
        
        if var.pointerStr():
            access="("+var.pointerStr()+"|"+"&\s*"+var.accessStr()+")"
        else:
            access="&\s*"+var.accessStr()
        pattern=re.compile(access)
        codestr=line.codestr.strip()
        for m in pattern.finditer(codestr):
            start,end=m.span()
            print "Argument check: the  matched string is :",m.group()
            result=Syntax.vararg(codestr,start,end)
            if not result:continue
            pos,index,arg,func_name=result
            res=var.matchAccessPattern(arg)
            if not res:continue
            rfl,p=res
            if pos==0:
                #OK arg
                
                return rfl,p,pos,func_name
            else:#pos=1
                #In actual, pos>=1 you need to calculate accurately what is it.
                j=index# index point to ','
                stack=[]
                quotation=False
                while True:
                    j-=1
                    #BOUND CHECK
                    if j<0:break
                    if quotation==False:
                        if codestr[j]==')':
                            stack.append(')')
                        elif codestr[j]=='(':
                            if len(stack)==0:
                                func_name=Syntax.extract_func_name(codestr,j)
                                if func_name:
                                    if Syntax.isKeyWord(func_name):
                                        return None
                                    return rfl,p,pos,func_name
                                break
                            else:
                                stack.pop()
                        elif codestr[j]==',':
                            if len(stack)==0:
                                pos+=1
                                                     
                    if codestr[j]=='"':
                        if j-1>=0 and codestr[j-1]=="\\":#FIX ME : maybe out of bound
                            continue
                        else:
                            quotation=not quotation
        return None
    @staticmethod
    def isPossibleArgumentDefinition2(line,var):
        access=var.pointerStr()
        pattern=re.compile(access)
        if not access:
            return None
        codestr="".join(line.codestr.split())
        resultset=[]
        for m in pattern.finditer(codestr):
            start,end=m.span()
            result=Syntax.vararg(codestr,start,end)
            if not result:continue
            pos,index,arg,func_name=result
            if pos==0:
                #OK arg
                pass
            else:#pos=1
                #In actual, pos>=1 you need to calculate accurately what is it.
                j=index# index point to ','
                stack=[]
                quotation=False
                while True:
                    j-=1
                    #BOUND CHECK
                    if j<0:break
                    if quotation==False:
                        if codestr[j]==')':
                            stack.append(')')
                        elif codestr[j]=='(':
                            if len(stack)==0:
                                func_name=Syntax.extract_func_name(codestr,j)
                                if func_name:
                                    resultset.append([pos,arg,func_name])
                                break
                            else:
                                stack.pop()
                        elif codestr[j]==',':
                            if len(stack)==0:
                                pos+=1                            
                    if codestr[j]=='"':
                        if j-1>=0 and codestr[j-1]=="\\":#FIX ME : maybe out of bound
                            continue
                        else:
                            quotation=not quotation
                    
        rs=[]
        for r in resultset:
            pos,arg,func_name=r         
            rfl,p=var.matchAccessPattern(arg)
            rs.append([rfl,p,pos,func_name])
        return rs
    
    @staticmethod
    def generate_for_jobs(num,codestr,v):
        v_access=v.accessStr()
        m=re.search(Syntax.for_pattern, codestr)
        if m is None:
            return None
        array=m.group().split(";")
        bound_var_strs=[]
        find_inc_exp=Syntax.isIncDef(v_access,array[2].rstrip(")").strip())
        if find_inc_exp:
            bound_var_strs=Filter.expression2vars(array[1])
            print "bound_var_strs:",bound_var_strs
        
        m_init= re.search(v_access+r"\s*=\s*(?!=)",array[0])
        init_var_strs=[]
        if m_init:
            left_var=m_init.group().rstrip("=").strip()
            left_var=''.join(left_var.split())
            right=array[0][m_init.span()[1]:]
            init_var_strs=Filter.expression2vars(right)
        if m_init is not None and find_inc_exp and left_var in bound_var_strs:
            bound_var_strs.remove(left_var)
        taint_vars=map(lambda x: TaintVar(x,[]),init_var_strs+bound_var_strs)
        if not m_init and find_inc_exp:
            taint_vars.append(v)
        for t_v in taint_vars:
            print 'taint var found in "for statement":',t_v
        jobs=map(lambda x:TaintJob(num,x),set(taint_vars))
        return list(set(jobs))
    