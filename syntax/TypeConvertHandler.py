'''
Created on Apr 29, 2016

@author: yangke
'''
import re
from syntax import Syntax
from model.TaintVar import TaintVar
class TypeConvertHandler(object):
    '''
    "Handle type convert right part like this:"
    #e.g.
    #619      const bfd_byte *addr = (const bfd_byte *) p;
    '''
    
    def __init__(self,right,pp, rfl):
        self.right=right
        self.pp=pp
        self.rfl=rfl
        self.type_convert=None
        
    def match(self):
        self.type_convert=re.compile(r'^\(.*\)\s*'+Syntax.identifier+'\s*$').match(self.right.strip())
        return self.type_convert is not None
        
    def generate_candidate_vars(self):
        if self.type_convert:
            varname=self.type_convert.group(1)
            return [varname]