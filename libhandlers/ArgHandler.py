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
        while i<len(codestr):
            if codestr[i]==',':
                if stack==[]:
                    return i,False#still have following arguments.
            elif codestr[i]=='(':
                stack.append('(')
            elif codestr[i]==')':
                if stack!=[]:
                    stack.pop()
                else:
                    return i,True#reach the last argument
            i+=1
        return None,True #can't find argument
    
    @staticmethod
    def arglist(rightstr):
        args=[]
        start_pos=0
        end_pos,islast=ArgHandler.nextarg(rightstr,start_pos)
        if end_pos is not None:
            args.append(rightstr[start_pos:end_pos])
        while not islast:
            start_pos=end_pos+1
            end_pos,islast=ArgHandler.nextarg(rightstr,start_pos)
            if end_pos is None:break
            args.append(rightstr[start_pos:end_pos])
            
        return [arg.strip() for arg in args]
    
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
        