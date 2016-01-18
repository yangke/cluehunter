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
from libhandlers.memmove_handler import memmove_handler
from libhandlers.ArgHandler import ArgHandler
from model.TaintJob import TaintJob
from model.TaintVar import TaintVar
from utils.Filter import Filter
from parse.FunctionCallInfo import FunctionCallInfo

class Syntax(object):
    RETURN_VALUE_ASSIGN=128
    NORMAL_ASSIGN=64
    OP_ASSIGN=32
    REF_ASSIGN=16
    INC=8
    RAW_DEF=4
    SYS_LIB_DEF=2
    FOR=1
    NODEF=0
    keyword="if|while|switch|for|goto|return|sizeof|instanceof|label|case|class|struct|int|float|long|usigned|double|char"
    identifier=r'([_A-Za-z][_A-Za-z0-9]*)'
    water=r'\s*'
    assign=r'=(?!=)'
    variable=r'('+identifier+'*('+water+'(\-'+water+'>|\.)'+water+identifier+')*)'
    lt=r'(?<![_A-Za-z0-9])'
    rt=r'(?![_A-Za-z0-9])'
    number=r'([+-]?([0-9]*\.?[0-9]+|[0-9]+\.?[0-9]*)([eE][+-]?[0-9]+)?)'
    constant_variable=r'([A-Z_][A-Z0-9_]*)'
    constant=r'('+constant_variable+r'|'+number+r')'
    for_pattern=r"for\s*([^;]*;[^;]*;[^;]*)";
    memop="memcpy|memset|memchr|memmove|memcmp|malloc|calloc|alloca|realloc"
    fileop="read|write|fopen|fclose|fwprintf|fprintf|vfprintf|fscanf|fread|fwrite|fgetc|fgets|fstat|fnmatch|real_fseek|fseeko64"
    stdop="open|close|read|write|scanf|printf|stat|getc|gets"
    strop="atoi|strlen|strcat|strncat|strtol|strtok|strcmp|strncmp|strcpy|strncpy|strstr|strrchr|strchr|sprintf|snprintf|vsprintf|vsnprintf|sscanf"
    syscall="gettimeofday|fork|syscall|textdomain|setlocale|getopt_long|ENOENT|bindtextdomain|non_fatal|nonfatal|exit_status|sbrk|CONST_STRNEQ"
    other="log|error|buildin"
    lib_func_name=memop+'|'+fileop+'|'+stdop+'|'+strop+'|'+syscall+'|'+other
    
    @staticmethod
    def normal_assignment_pattern(accessstr):
        return Syntax.lt+accessstr+Syntax.water+r"(\[[^\[\]]+\])?"+Syntax.water+Syntax.assign
    @staticmethod
    def op_assignment_pattern(accessstr):
        return Syntax.lt+accessstr+Syntax.water+r"(\[[^\[\]]+\])?"+Syntax.water+r"[\+\-\*\/%\^\|&]"+Syntax.water+Syntax.assign
    @staticmethod
    def isKeyWord(codestr):
        pattern=re.compile(Syntax.keyword)
        if pattern.match(codestr.strip()):
            return True
        else:return False
    @staticmethod
    def isLibFuncName(codestr):
        pattern=re.compile(Syntax.lib_func_name)
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
            print 1/0
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
        if m is not None:
            return True
        return False
    
    @staticmethod
    def isInMultilineFor(l,i,var):
        if isinstance(l[i],FunctionCallInfo) or isinstance(l[i-1],FunctionCallInfo) or isinstance(l[i-2],FunctionCallInfo):
            return False
        p1=re.compile(r"^\s*for\s*([^;\)];$")
        p2=re.compile(r"^\s+[^;\)]+;$")
        p3=re.compile(r"^\s+[^;\)]+\)$")
        if p1.match(l[i-2].codestr) and p2.match(l[i-1].codestr) and p3.match(l[i].codestr):
            return True
    
    @staticmethod
    def isIncDef(access,codestr):
        increasement=r"("+access+r"\s*\+\+)|(\+\+\s*"+access+r")|("+access+r"\s*\-\-)|(\-\-\s*"+access+r")"
        if re.search(increasement, codestr):
            print "NORMAL INC!"
            return True
        lib_definition=Syntax.lt+r"fread\s*\(\s*([^,\(]*),([^,\(]*),([^,\(]*),"+access+"([^,\(]*)\s*\)"
        if re.search(lib_definition, codestr):
            print "SYSCALL INC!"
            return True
        syscall_definition=Syntax.lt+r"read\s*\(\s*"+access+"([^,\(]*),([^,\(]*),([^,\(]*)\s*\)"
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
        elif memmove_handler.isArgDef(varstr,codestr):
            return True
        elif memcpy_handler.isArgDef(varstr,codestr):
            return True
        elif memset_handler.isArgDef(varstr,codestr):
            return True
        return False
    
    @staticmethod
    def handle_sys_lib_def(i,variable,codestr):
        jobs=[]
        yes=fread_handler.isArgDef(variable,codestr)
        if yes:
            jobs=fread_handler.getJobs(i,variable, codestr)
        yes=read_handler.isArgDef(variable,codestr)
        if yes:
            jobs=read_handler.getJobs(i, variable,codestr)
        yes=memcpy_handler.isArgDef(variable, codestr)
        if yes:
            jobs=memcpy_handler.getJobs(i, variable, codestr)
        yes=strncpy_handler.isArgDef(variable, codestr)
        if yes:
            jobs=strncpy_handler.getJobs(i, variable, codestr)
        yes=memmove_handler.isArgDef(variable, codestr)
        if yes:
            jobs=memmove_handler.getJobs(i, variable, codestr)
        yes=strcpy_handler.isArgDef(variable, codestr)
        if yes:
            jobs=strcpy_handler.getJobs(i, variable, codestr)
        yes=memset_handler.isArgDef(variable, codestr)
        if yes:
            jobs=memset_handler.getJobs(i, variable, codestr)
        return jobs#FIX ME: this should not happen
    
    @staticmethod
    def getVars(var,line):
        codestr=line.codestr
        str_pat=var.accessStr()+r"\s*(\[[^\[\]]+\])*\s*[\+\-\*/%&\|]?\s*=(?!=)"
        print "CHECKING CODE:",codestr
        m=re.search(str_pat,codestr)
        if m:
            span=m.span()
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
            elif re.search(r"\s*fopen\s*\(",right):
                m_fopen=re.search(r"\s*fopen\s*\(",right)
                start_pos=m_fopen.span()[1]
                end_pos,reachend=ArgHandler.nextarg(right, start_pos)
                if reachend:
                    print "Fatal Error fopen() has only one argument!"
                    1/0
                if re.search("\[|\+|\-(?!>)", right):
                    print "Fatal Error cannot handle expression filename now!"
                    1/0
                print right,right[start_pos:end_pos].strip()
                return set([TaintVar(right[start_pos:end_pos].strip(), ['*'])])
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
                    break#The first exit port pos==1
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
    def isUniqueNonLibCall(callstr):
        callstr=' '.join(callstr.split()).rstrip(';')
        if callstr=='':return False
        if re.search(r"[_A-Za-z0-9]",callstr[0]) is None:
            return False
        m=re.search(Syntax.identifier+r"\s*\(",callstr)
        if m is None :
            return False
        if Syntax.isLibFuncName(m.group().rstrip('(')):
            return False
        start=m.span()[1]
        end,islast=ArgHandler.nextarg(callstr,start)
        while islast==False:
            print start,end,callstr
            start=end+1
            end,islast=ArgHandler.nextarg(callstr,start)
        if end is not None and end==len(callstr)-1:
            return True
        return False
    

    @staticmethod
    def matchDefiniteDefinitionType(codestr,var):
        if "fprintf" in codestr:
            print "Got it!"
        access=var.accessStr()
        print "Checking Definition Type for:",access
        normal_assginment=Syntax.normal_assignment_pattern(access)
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
        op_assignment=Syntax.op_assignment_pattern(access)
        if re.search(op_assignment,codestr):
            return Syntax.OP_ASSIGN
        raw_definition=r"^\s*\{\s*[A-Za-z_][A-Za-z0-9_]+\s+(\*\s*)*([A-Za-z_][A-Za-z0-9_]+\s*,\s*)*"+var.v+"\s*;"
        if re.search(raw_definition, codestr):
            print "We got the raw definition!"
            return Syntax.RAW_DEF
        if Syntax.isLibArgDef(var,codestr):
            return Syntax.SYS_LIB_DEF
        return  Syntax.NODEF
    @staticmethod
    def vars_in_for_change_part(v_access,change_str):
        change_str=''.join(change_str.split())
        changes=change_str.split(',')
        for change in changes:
            #inc
            find_inc=Syntax.isIncDef(v_access,change)
            if find_inc:
                return []
            #assignment
            #===================================================================
            # find_assign=re.search(v_access+Syntax.assign, change)
            # if find_assign:
            #     rightvars=Filter.expression2vars(change[find_assign.span()[1]:])
            #     return rightvars
            #===================================================================
            #op_assignment
            find_op_assign=re.search(Syntax.op_assignment_pattern(v_access), change)
            if find_op_assign:
                rightvars=Filter.expression2vars(change[find_op_assign.span()[1]:])
                return rightvars
        return None
    @staticmethod
    def vars_in_for_init_part(v_access,init_str): 
        init_str=' '.join(init_str.split())
        inits=init_str.split(',')
        for init in inits:
            match_init= re.search(v_access+Syntax.assign,init)
            if match_init:
                left_var=match_init.group().rstrip("=")
                rightstr=init[match_init.span()[1]:]
                right_var_strs_in_init=Filter.expression2vars(rightstr)
                return left_var,right_var_strs_in_init
        return None
    @staticmethod
    def split_for(codestr):
        codestr=' '.join(codestr.split())
        m=re.search(Syntax.for_pattern, codestr)
        if m is None:
            return None
        array=m.group().split(";")
        init=array[0].strip()
        cond=array[1].strip()
        change=array[2].rstrip(")").strip()
        return init,cond,change
    @staticmethod
    def generate_for_jobs(num,codestr,v):
        v_access=v.accessStr()
        init,cond,change=Syntax.split_for(codestr)
        #right vars in init part
        right_vars_in_change=Syntax.vars_in_for_change_part(v_access,change)
        #bound vars in cond part
        bound_var_strs=[]
        if right_vars_in_change is not None:
            bound_var_strs=Filter.expression2vars(cond)
        #right vars in change part
        init_vars=Syntax.vars_in_for_init_part(v_access,init)
        right_var_strs_in_init=[]
        if init_vars is not None:
            left_var,right_var_strs_in_init=init_vars
            if right_vars_in_change is not None and left_var in bound_var_strs:
                bound_var_strs.remove(left_var)
        taint_vars=map(lambda x: TaintVar(x,[]),right_var_strs_in_init+bound_var_strs)#+right_vars_in_change) Now we discard right increvalue because it's usually a fix value.
        if init_vars is None and right_vars_in_change is not None:
            taint_vars.append(v)
        for t_v in taint_vars:
            print 'Taint Vars found in FOR STATEMENT:',t_v
        jobs=map(lambda x:TaintJob(num,x),set(taint_vars))
        return list(set(jobs))