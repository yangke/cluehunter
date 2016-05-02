'''
Created on Apr 29, 2016

@author: yangke
'''
import re
from utils.Filter import Filter

class ConditionalExpressionHandler(object):
    '''
    Handle conditional expression like this:
    #e.g.
    #1      a>b?x:y
    '''

    def __init__(self, right, pp, rfl):
        self.right=right
        self.pp=pp
        self.rfl=rfl
        self.m_cond_exp=None
        
    def match(self):
        self.m_cond_exp=re.compile(r'^[^\?:]*\?[^\?:]*:[^\?:]*$').match(self.right)
        return self.m_cond_exp is not None
    
    def generate_candidate_vars(self):
        if self.m_cond_exp:
            #FIX ME:
            #CAN HANDLE: int i,m=t->len>10?10:t->len;
            #CANNOT HANDLE: m=q+((t->len>10?10:t->len)?a:b);
            array=self.right.split('?')[1].split(':')
            choice1=Filter.expression2vars(array[0])
            choice2=Filter.expression2vars(array[1])
            symbols=choice1+choice2
            return symbols