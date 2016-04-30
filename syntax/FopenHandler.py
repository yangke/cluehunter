'''
Created on Apr 29, 2016

@author: yangke
'''
import re
from syntax import Syntax
from model.TaintVar import TaintVar
from libhandlers.ArgHandler import ArgHandler
class FopenHandler(object):
    '''
    "Handle type convert right part like this:"
    #e.g.
    #619      const bfd_byte *addr = (const bfd_byte *) p;
    '''
    
    def __init__(self,right):
        self.right=right
        self.m_fopen=None
        
    def match(self):
        self.m_fopen=re.search(r"\s*fopen\s*\(",self.right)
        return self.m_fopen is not None
        
    def generate_vars(self):
        if self.m_fopen:
            start_pos=self.m_fopen.span()[1]
            end_pos,reachend=ArgHandler.nextarg(self.right, start_pos)
            if reachend:
                print "Fatal Error fopen() has only one argument!"
                1/0
            if re.search("\[|\+|\-(?!>)", self.right):
                print "Fatal Error cannot handle expression filename now!"
                1/0
            v=self.right[start_pos:end_pos].strip()
            return set([TaintVar(v,['*'])])