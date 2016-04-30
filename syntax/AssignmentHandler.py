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
        
    def getJobs(self, var, index,sliced_indexes):
        line =self.l[index]
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
                symbols=cond_exp.generate_candidate_vars()
            elif type_conv.match():
                symbols=type_conv.generate_candidate_vars()
            else:    
                symbols=Filter.expression2vars(right)
            print symbols
            varstrs=Filter.filterOutFuncNames(symbols,line.codestr)
            print "Right variables in assignment:",varstrs
            taintvars=set(map(lambda x : TaintVar(x, []), varstrs))
            jobs=map(lambda x : TaintJob(index, x), taintvars)
            return jobs