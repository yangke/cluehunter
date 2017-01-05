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
from libhandlers.sscanf_handler import sscanf_handler
from libhandlers.fgetc_handler import fgetc_handler
from libhandlers.ArgHandler import ArgHandler
from model.TaintJob import TaintJob
from model.TaintVar import TaintVar
from utils.Filter import Filter
from parse.FunctionCallInfo import FunctionCallInfo

class Syntax(object):
    ARRAY_ASSIGN_RETURN_VALUE_ASSIGN=10
    RETURN_VALUE_ASSIGN=9
    NORMAL_ASSIGN=8
    ARRAY_ASSIGN=7
    OP_ASSIGN=6
    REF_ASSIGN=5
    INC=4
    RAW_DEF=3
    SYS_LIB_DEF=2
    FOR=1
    NODEF=0
    keyword="if|while|switch|for|goto|return|sizeof|instanceof|label|case|class|struct|int|float|long|usigned|double|char"
    identifier=r'([_A-Za-z][_A-Za-z0-9]*)'
    water=r'\s*'
    assign=r'=(?!=)'
    variable=r'[&\*]*('+identifier+'('+water+'(\-'+water+'>|\.)'+water+identifier+')*)'
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
    other="log|error|buildin|va_arg"
    lib_func_name='^('+memop+'|'+fileop+'|'+stdop+'|'+strop+'|'+syscall+'|'+other+')$'
    @staticmethod
    def normal_assignment_pattern(accessstr):
        if len(accessstr) > 4 and '(?<!' == accessstr[0:4]: # already have $lt
            return accessstr+Syntax.water+Syntax.assign
        return Syntax.lt+accessstr+Syntax.water+Syntax.assign
        #return Syntax.lt+accessstr+Syntax.water+r"(\[[^\[\]]+\])?"+Syntax.water+Syntax.assign
    @staticmethod
    def op_assignment_pattern(accessstr):
        return Syntax.lt+accessstr+Syntax.water+r"(\[[^\[\]]+\])?"+Syntax.water+r"[\+\-\*\/%\^\|&]"+Syntax.water+Syntax.assign
    @staticmethod
    def isKeyWord(codestr):
        pattern=re.compile("^("+Syntax.keyword+")$")
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
    def declaration_left_propagate_pattern(v):
        declare_pat=r"[A-Za-z_][A-Za-z0-9_]+\s+(\*\s*)*[A-Za-z_][A-Za-z0-9_]*"
        vp=Syntax.left_ref_propagate_pattern(v)
        tail=r"\s*=\s*(\([^\(\)]*\))?\s*"+vp+r"\s*;"
        return Syntax.lt+declare_pat+tail
    @staticmethod
    def variable_left_propagate_pattern(v):
        variable_pat=Syntax.variable
        vp=Syntax.left_ref_propagate_pattern(v)
        tail=r"\s*=\s*(\([^\(\)]*\))?\s*"+vp+r"\s*;"
        return Syntax.lt+variable_pat+tail
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
        return pat
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
    def isForStatement(codestr,access_pat):
        m=re.search(Syntax.for_pattern, codestr)
        if m is not None:
            if re.search(access_pat+r"\s*=[^=]",codestr) or re.search(access_pat+r"(\+\+|--)",codestr):
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
        if fgetc_handler.isArgDef(varstr,codestr):
            return True
        elif fread_handler.isArgDef(varstr,codestr):
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
        elif sscanf_handler.isArgDef(varstr,codestr):
            return True
        return False
    
    @staticmethod
    def handle_sys_lib_def(i,variable,codestr):
        jobs=[]
        yes=fgetc_handler.isArgDef(variable,codestr)
        if yes:
            jobs=fgetc_handler.getJobs(i,variable, codestr)
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
        yes=sscanf_handler.isArgDef(variable, codestr)
        if yes:
            jobs=sscanf_handler.getJobs(i, variable, codestr)
        return jobs#FIX ME: this should not happen
    
    
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
        #=======================================================================
        # cache_bread (...,(char *) buf + nread,...)
        #                           ^  ^
        #                           start end
        #=======================================================================
        if start>=end or start<0 or end>len(codestr):
            return None
        v_start=-1
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
                        if j==len(codestr):
                            print "Fatal Error: bracket mismatch. May be like: &(a...."
                            print 1/0
                continue
            elif codestr[i] == ",":
                pos=1
                break#second  exit port pos>1
            elif codestr[i] == ")":#skip the "(char *)" in "(char *) buf + nread"
                v_start=i+1
                while codestr[i]!="(":
                    i-=1
            else:
                return None
        if v_start==-1:
            var_name=codestr[i+1:j]
        else:
            var_name=codestr[v_start:j]
        #=======================================================================
        # cache_bread (...,(char *) buf + nread,...)
        #             ^
        #             i
        #=======================================================================
              
        return pos,i,var_name,func_name,j
    @staticmethod
    def isPossibleArgumentDefinition(codestr,var):
        
        codestr=codestr.strip()
        if var.pointerStr():
            access="("+var.pointerStr()+"|"+"&\s*"+var.accessStr()+")"
        else:
            access="&\s*"+var.accessStr()
        pattern=re.compile(access)        
        for m in pattern.finditer(codestr):
            start,end=m.span()
            if codestr[end]=="." or codestr[end:end+2]=="->" :
                continue
            print "Argument check: the  matched string is :",m.group()
            result=Syntax.vararg(codestr,start,end)
            if not result:continue
            pos,index,arg,func_name,endIndex=result
            res=var.matchAccessPattern(arg)
            if not res:continue
            rfl,p=res
            j=endIndex
            while j<len(codestr) and re.search(r'\s',codestr[j]):
                j+=1
                if codestr[j]=='+':
                    for pat in p:
                        if '*' in pat or '->' in pat:
                            p=['*']
                            break
            if pos==0:
                #OK arg
                return rfl,p,pos,func_name,arg
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
                                    return rfl,p,pos,func_name,arg
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
    def remove_left_type_coversion(callstr):
        #side effect: remove out-most bracket
        #1.callstr: "(struct areltdata *) _bfd_read_ar_hdr (abfd)" => return "_bfd_read_ar_hdr (abfd)"
        #2.callstr: "(raw)" => return raw
        #3.callstr: "raw" => return raw
        #4.callstr: "raw)(" => return raw)(
        #5.callstr: "(raw" => return None
        callstr=callstr.strip()
        
        if callstr[0]=="(" :
            i=1
            stack=["("]
            while len(stack)!=0 and i<len(callstr):
                if callstr[i]=="(":
                    stack.append("(")
                elif callstr[i]==")":
                    stack.pop()
                i+=1
            
            if len(stack)!=0:
                return None    
            elif i==len(callstr):
                #side effect: remove out-most bracket
                return callstr.lstrip("(").rstrip(")")
            else:
                return callstr[i:].strip()
        else:
            return callstr
    @staticmethod
    def isUniqueNonLibCall(callstr):
        callstr=callstr.strip().rstrip(';').strip()
        #callstr=' '.join(callstr.split()).rstrip(';').rstrip()
        if callstr=='':return False
        if callstr[0]=="(":#callstr: (struct areltdata *) _bfd_read_ar_hdr (abfd)
            callstr=Syntax.remove_left_type_coversion(callstr)
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
        print    end,  len(callstr)-1
        if end is not None and end==len(callstr)-1:
            return True
        return False
    
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
            match_init= re.search(v_access+r"\s*"+Syntax.assign,init)
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
        # e.g "for (target = bfd_target_vector; *target != NULL; target++)"
        # PostCond:
        # init => "for (target = bfd_target_vector"
        # cond => "*target != NULL"
        # change => "target++)"
        #right vars in init part
        right_vars_in_change=Syntax.vars_in_for_change_part(v_access,change)
        # change = "target++)"
        # right_vars_in_change => "target"
        #bound vars in cond part
        bound_var_strs=[]
        if right_vars_in_change is not None:
            print "%%%%%",cond
            bound_var_strs=Filter.expression2vars(cond)
            # cond = "*target != NULL"
            # bound_var_strs => ["*target"] 
            print "%%", bound_var_strs
            print "%",init
        # Pre : 
        # init = "for (target = bfd_target_vector" 
        # bound_var_strs = ["*target"]
        # Post:
        # bound_var_strs => ["*target"]
        # FIX ME may cause "sre_constants.error: nothing to repeat"
        bound_var_strs=[bv for bv in bound_var_strs if bv[-1]!='*' and re.search(TaintVar(bv,[]).accessStr()+r"\s*"+Syntax.assign,init) is None];
         
        # right vars in change part
        init_vars=Syntax.vars_in_for_init_part(v_access,init)# e.g init ="for (target = bfd_target_vector" => init_vars = "target"
        print "ERROR_CHECK_POINT(${parsing 'for statement' during 'for' job generation})"
        right_var_strs_in_init=[]
        if init_vars is not None:
            # e.g. 
            # Pre: "target = bfd_target_vector"
            # Post :
            #     left_var => "target"
            #     right_var_strs_in_init => "bfd_target_vector"
            left_var,right_var_strs_in_init=init_vars
            # Pre : 
            #     left_var = "target"
            #     right_vars_in_change = "target"
            #     bound_var_strs = ["*target"]
            # Post: 
            #     bound_var_strs = []
            if right_vars_in_change is not None:#right_vars_in_change = "target"
                for bv in bound_var_strs:
                    if left_var in bv:#bound_var_strs = ["*target"]
                        bound_var_strs.remove(left_var)#bound_var_strs = []
                        break
                    
        taint_vars=map(lambda x: TaintVar(x,[]),right_var_strs_in_init+bound_var_strs)#+right_vars_in_change) Now we discard right increvalue because it's usually a fix value.
        if init_vars is None and right_vars_in_change is not None:
            taint_vars.append(v)
        for t_v in taint_vars:
            print 'Taint Vars found in FOR STATEMENT:',t_v
        jobs=map(lambda x:TaintJob(num,x),set(taint_vars))
        return list(set(jobs))