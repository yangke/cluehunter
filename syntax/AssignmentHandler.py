'''
Created on Apr 29, 2016

@author: yangke
'''
import re
from syntax import Syntax
from libhandlers.ArgHandler import ArgHandler
from model.TaintVar import TaintVar
from model.TaintJob import TaintJob
from utils.Filter import Filter
from ConditionalExpressionHandler import ConditionalExpressionHandler
from TypeConvertHandler import TypeConvertHandler
from FopenHandler import FopenHandler
from Va_argHandler import Va_argHandler
class AssignmentHandler(object):
    '''
    Handle ASSIGNMENT or OPERATOR BASED ASSIGNMENT
    '''
    def __init__(self, l,TG):
        self.l=l
        self.TG=TG
        
    def getJobs(self, var, index,sliced_indexes,expanded_str):
        line =self.l[index]
        if expanded_str:
            codestr=expanded_str
        else:
            codestr=line.codestr
        str_pat=var.accessStr()+r"\s*(\[[^\[\]]+\])*\s*[\+\-\*/%&\|]?\s*=(?!=)"
        print "CHECKING CODE:",codestr
        m=re.search(str_pat,codestr)#const bfd_byte *addr = (const bfd_byte *) p;
        if m:
            span=m.span()
            it=m.group()#left="*addr ="
            i=0
            while re.search(r"[A-Za-z0-9_\.\*\->\s]",it[i]):
                i+=1
            name="".join(it[:i].split())
            left_type = codestr[:span[0]].strip()#"const bfd_byte "
            is_type_conv=False
            is_type_declare=False
            if len(left_type)>0 and re.sub(r"[_A-Za-z\s\(\)]","",left_type)=="": #type declaration:  "const bfd_byte "
                name=re.sub(r"[\*&\s]","",name)
                is_type_declare=True
            rfl,pp=var.matchAccessPattern(name)
            right=codestr[span[1]:]
            right=right.split(';')[0].strip() #strip out ";"
            va_arg_handler=Va_argHandler(right,pp, rfl, index, sliced_indexes, self.l, self.TG)
            fopen_handler=FopenHandler(right)
            type_conv=TypeConvertHandler(right,pp,rfl)
            cond_exp=ConditionalExpressionHandler(right,pp,rfl)
            if Syntax.isVariable(right):
                if pp is None:
                    print "Fatal Error!!!",1/0
                    return None
                else:
                    print pp
                    return [TaintJob(index,TaintVar(right, pp, rfl))]
            elif va_arg_handler.match():
                return va_arg_handler.generate_jobs()
            elif fopen_handler.match():
                taintvars= fopen_handler.generate_vars()
                jobs=map(lambda x : TaintJob(index, x), taintvars)
                return jobs
            elif cond_exp.match():
                symbols=cond_exp.generate_candidate_vars()#BUG when: const bfd_bye *addr= b>0 ? mm->addr1:mm->addr2;
            elif type_conv.match():
                symbols=type_conv.generate_candidate_vars()
                is_type_conv=True
            else:    
                symbols=Filter.expression2vars(right)
            print symbols
            varstrs=Filter.filterOutFuncNames(symbols,line.codestr)
            print "Right variables in assignment:",varstrs
            taintvars=[]
            for v in varstrs:
                if re.search(v.replace('*','') +r'\s*\[',line.codestr):
                    taintvars.append(TaintVar(v, ['*']))
                elif is_type_declare and is_type_conv:
                    taintvars.append(TaintVar(v, pp))
                else:
                    taintvars.append(TaintVar(v, []))
                    
            jobs=map(lambda x : TaintJob(index, x), taintvars)
            return jobs