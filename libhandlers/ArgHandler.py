'''
Created on Dec 13, 2015

@author: yangke
'''
from utils.Filter import Filter
import re
class ArgHandler(object):
    @staticmethod
    def nextarg(codestr,start_pos):
        i=start_pos
        stack=[]
        while codestr[i]!=',':
            if codestr[i]=='(':
                stack.append('(')
            elif codestr[i]==')':
                if stack!=[]:
                    stack.pop()
                else:
                    break
            i+=1
        return i
    @staticmethod
    def vars_in_pointer_offset_style(expstr):
        m=re.search(r'\+|\-[^>]',expstr)
        if m:
            first_op=m.span()[0]#first + or - operation for case: 'psf->header+psf->headerindex'
            former_vars=Filter.expression2vars(expstr[:first_op])
            follow_vars=Filter.expression2vars(expstr[first_op+1:])
            return former_vars,follow_vars
        else:
            former_vars=[''.join(expstr.split())]
            return former_vars,None
        