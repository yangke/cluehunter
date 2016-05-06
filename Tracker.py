'''
Created on Sep 9, 2015

@author: yangke
'''
import re
import subprocess
from model.TaintGraph import TaintGraph
from model.TaintJob import TaintJob
from model.TaintVar import TaintVar
from parse.FunctionCallInfo import FunctionCallInfo
from parse.LineOfCode import LineOfCode
from utils.Filter import Filter
from syntax.syntax import Syntax
from libhandlers.ArgHandler import ArgHandler
from parse.RecordManager import RecordManager
from parse.MacroInspector import MacroInspector
from syntax.AssignmentHandler import AssignmentHandler
#===============================================================================
# FIX ME: We need to define two colors for control and data dependency:
# "BLUE" for control dependency and "RED" for data dependency.
# Define them like the following:
# BLUE=0x1
# RED=0x2
# BOTH=BLUE&RED=0x3
#===============================================================================

class Tracker:
    def __init__(self,l,macro_inspector=None):
        self.record_manager=l
        self.l=self.record_manager.l
        self.macro_inspector=self.record_manager.macro_inspector
    def get(self,i):
        self.record_manager.get(i)
        self.l=self.record_manager.l
        return self.l[i]
    def track(self):
        self.createTaintGraph()
        self.record_manager.write2File()
        return self.TG
    
    def setStartJobs(self,traceIndex,varset):
        self.start_jobs=[]
        for var in varset:
            self.start_jobs.append(TaintJob(traceIndex,var))
        
    def createTaintGraph(self):
        self.TG=TaintGraph(self.record_manager)
        c = self.taintUp(self.start_jobs)
        while(c!=[]):
            c = self.taintUp(c)
    def findPositions(self,P,funcInfo):
        positions=set()#get param positions
        for p in P:
            if p.corresponding_arg_pos is not None:
                positions.add((p.corresponding_arg_pos,p.var))
                continue
            find_this=0
            findIt=False
            print "param var:",p
            for i,param in enumerate(funcInfo.param_list.split(',')):
                print "index, paramstr:",i,param
                if "=" not in param:
                    find_this+=1
                if "this=this@entry" not in param:#param is like:m=m@entry=0xbfffe4a8
                    if p.var.v in param.split('=')[0]:#FIX me there may be mismatch cases 
                        positions.add((i-find_this,p.var))
                        findIt=True
                        break
                else:
                    find_this+=1
            if not findIt:
                print "Can't find the param by the paramjob!"
                print 1/0
        print "positions:"
        for pos in positions:print str(pos[0])
        return positions
    
    def normal_right_str(self,upperIndex,funcInfo):
        #right_str is the string in the right of "(" which contains the argument list.
        func_name_to_search=funcInfo.get_func_name().split("::")[-1].strip()
        p=r"^.*"+func_name_to_search+r"\s*\("
        print "The function name to search:",func_name_to_search
        print "The under check line:",self.l[upperIndex].codestr
        # Need Fix:
        # func(a,b\
        #    c,d,e)
        m = re.search(p, self.l[upperIndex].codestr)
        while not m:#FIX ME:this may cause out of bound error
            print "skip:",self.l[upperIndex]
            upperIndex-=1
            if upperIndex<0 or isinstance(self.l[upperIndex], FunctionCallInfo):
                print "Bad Case in 'TaintUp':FIX ME."
                return []
            print "check next:",self.l[upperIndex]
            m = re.search(p, self.l[upperIndex].codestr)
        rightstr=self.l[upperIndex].codestr[m.span()[1]:]
        print "rightstr:",rightstr
        return rightstr,upperIndex
    
    def macro_call_right_str(self,upperIndex):
        filename=self.l[upperIndex].get_func_call_info().get_file_name()
        linenum=self.l[upperIndex].get_linenum()
        print filename,linenum
        expanded_str=self.macro_inspector.getExpanded(filename,linenum)
        print "expanded str:",expanded_str
        if "temp = (((abfd)->xvec->_bfd_check_format[(int) ((abfd)->format)]) (abfd));" in expanded_str:
            print "Find It!"
        call_patttern=Syntax.lt+Syntax.identifier+Syntax.water+r"[\)\]]*"+Syntax.water+r"\("
        for m in re.finditer(call_patttern,expanded_str):
            print "matched candidate function name:",m.group(1)
            if not Syntax.isKeyWord(m.group(1)) and not Syntax.isLibFuncName(m.group(1)):
                span=m.span()
                #FIX ME this is wrong when handling cases like: MAZE(a,b)-->'call1(a)+call2(b)".
                #Then when handling the second call site, it returns 'a' as the detected argument.  
                return expanded_str[span[1]:]
        print "Fatal Error treat 'sizeof' as a function call or other ERROR!! Please check the macro_call_right_str()"
        x=1/0
        
    def isMacroCall(self,callsite_index):
        if self.macro_inspector is None:
            return False
        if self.macro_inspector.project_dir is None:
            return False
        print "Checking Macro Call..."
        print "UPPER:",self.l[callsite_index]
        print "CALLINFO:",self.l[callsite_index+1]
        for m in re.finditer(Syntax.lt+Syntax.identifier+Syntax.water+r"\(",self.l[callsite_index].codestr):
            funcname=m.group().rstrip("(").strip()
            if Syntax.isKeyWord(funcname):
                continue
            #Note that the second argument of getExpanded is the line_num of the call site code.
            #So should be callsite_index+1
            print "Find Macro Call:",self.l[callsite_index]
            filename=self.l[callsite_index].get_func_call_info().get_file_name()
            linenum=self.l[callsite_index].get_linenum()
            print filename,linenum
            expanded_str=self.macro_inspector.getExpanded(filename,linenum)
            if expanded_str is None:
                return False
            print "expanded str:",expanded_str
            if "temp = (((abfd)->xvec->_bfd_check_format[(int) ((abfd)->format)]) (abfd));" in expanded_str:
                print "Find IT!"
            call_patttern=Syntax.lt+Syntax.identifier+Syntax.water+r"[\)\]]*"+Syntax.water+r"\("
            for m in re.finditer(call_patttern,expanded_str):
                if ']' in m.group():
                    return True
                cleaner=''.join(m.group().split())
                clean=cleaner.rstrip('(').rstrip(')')
                if not Syntax.isKeyWord(clean) and not Syntax.isLibFuncName(m.group(1)):
                    return True
        return False
    def taintUp(self,jobs):
        if len(jobs) ==0 :return []
        P=[]
        paramJobs,newJobs=self.taintOneStepUp(jobs)
        P.extend(paramJobs)
        while len(newJobs)>0:
            paramJobs,newJobs=self.taintOneStepUp(newJobs)
            P.extend(paramJobs)
        if P==[]:
            return []
        else:
            traceIndex=P[0].trace_index
            if traceIndex==0:return []
            funcInfo=self.l[traceIndex]
            print "FunctionCallInfo:",funcInfo
            positions=self.findPositions(P,funcInfo)
            print "The inter point and the old line:",self.l[traceIndex]
            upperIndex=traceIndex-1#try to find last call site
            self.get(upperIndex)
            funcname=self.l[traceIndex].get_func_name().split("::")[-1].strip()
            if re.search(Syntax.lt+funcname+r"\s*\(",self.l[upperIndex].codestr):
                rightstr,upperIndex=self.normal_right_str(upperIndex, funcInfo)
            elif self.isMacroCall(upperIndex):
                rightstr=self.macro_call_right_str(upperIndex)
            else:
                print "Malformed call site! Cannot find the arglist of the call site!"
                print 1/0
            args = ArgHandler.arglist(rightstr)
            cjobs=set()
            for pos,param in positions:
                print "args:",args
                print "pos,param:",pos,param
                arg=args[pos].strip()
                self.TG.linkInterEdges(traceIndex,upperIndex,param,arg,pos)
                print "arg expression:",arg
                identifiers=Filter.expression2vars(arg)
                print "variables in arg expression",identifiers
                #handle the 'header->index+offset' and '&op' pattern
                #NOTE: We let the TaintVar to help us handle variables with '&' or '->'.
                #It will automatically performs dereference and reference action.
                #FIXME: patterns like '&argv[i]' '*p' has not been handled soundly now.  
                accessp=[e for e in param.p]
                if len(identifiers)==0:
                    print "ARG:",arg
                    print "Arg of callsite doesn't contains variable! Maybe all is constant."
                elif len(identifiers)==1:
                    print 'Unique variable argument:',identifiers[0]
                    job=TaintJob(upperIndex,TaintVar(identifiers[0],accessp))
                    cjobs.add(job)
                else:
                    find_base_pointer=False
                    for identifier in identifiers:
                        if not find_base_pointer:
                            m=re.search(identifier+r'\s*[\+\-]',arg)
                            if m and m.span()[0]==0:
                                job=TaintJob(upperIndex,TaintVar(identifier,accessp))
                                find_base_pointer=True
                            else:
                                m=re.search(identifier+r'\s*\[',arg)
                                if m:
                                    job=TaintJob(upperIndex,TaintVar(identifier,['*']))
                                else:
                                    job=TaintJob(upperIndex,TaintVar(identifier,[]))
                        else:
                            m=re.search(identifier+r'\s*\[',arg)
                            if m:
                                job=TaintJob(upperIndex,TaintVar(identifier,['*']))
                            else:
                                job=TaintJob(upperIndex,TaintVar(identifier,[]))
                        cjobs.add(job)
            return cjobs
    def taintOneStepUp(self,jobs):
        newjobs=set()
        for job in jobs:
            print job
            jbs=self.lastModification(job)
            print jbs
            newjobs=newjobs|set(jbs)
        paramjobs=set()
        normaljobs=set()
        for job in newjobs:
            if job.isParamJob(self.l):
                paramjobs.add(job)
            else:
                normaljobs.add(job)
        return paramjobs,normaljobs
    def up_slice(self,job):
        #put the upper same function-surface statements together
        indexes=[]
        i=job.trace_index-1
        while abs(i)<len(self.l):
            self.get(i)
            if isinstance(self.l[i], LineOfCode) and self.l[i].get_func_call_info()==self.l[job.trace_index].get_func_call_info():
                indexes.append(i)
            if isinstance(self.l[i], FunctionCallInfo) and self.l[i] == self.l[job.trace_index].get_func_call_info():
                if isinstance(self.l[i-1], LineOfCode):
                    if self.l[i].get_func_name().split("::")[-1] in self.l[i-1].codestr:
                        break
                    elif self.isMacroCall(i-1):
                        break
                elif i-2>=0 and isinstance(self.l[i-2], LineOfCode):
                    if self.l[i].get_func_name().split("::")[-1] in self.l[i-2].codestr:
                        break
                    elif self.isMacroCall(i-2):
                        break
            i-=1
        return indexes
    
    def lastModification(self,job):
        if job.trace_index==-2:#1293:
            print "FInd you!"
        if "count = va_arg (argptr, int) ;" in str(self.l[job.trace_index]):
            print "HEY"
        if job.trace_index==0:
            return []
        if isinstance(self.l[job.trace_index], FunctionCallInfo):
            return None#The input should not be a job in FunctionCallInfo
        if job.trace_index==1:#begin
            if job.var.v in self.l[job.trace_index-1].param_list:
                self.TG.linkInnerEdges(job.trace_index,job.trace_index-1,job.var.simple_access_str())
            return []
        indexes=self.up_slice(job)
        if len(indexes)>0:
            pairs=self.findAllReferences(job.var,indexes,False)
            pairs.append((indexes[0]-1,job.var,False,0,len(indexes)))
            #(aIndex,q,True,idx+1,lb)
            defs=self.getDefs(pairs,indexes)
            for d,v in defs:
                print "In list definition:",d,self.l[d]
            for d,v in defs:
                def_type=self.matchDefinitionType(d,v)
                if def_type==Syntax.FOR:
                    self.TG.linkInnerEdges(job.trace_index,d,v.simple_access_str())
                    jobs=Syntax.generate_for_jobs(d, self.l[d].codestr, v)
                    return list(set(jobs))
                if def_type==Syntax.INC:#INC
                    self.TG.linkInnerEdges(job.trace_index,d,v.simple_access_str())
                    return [TaintJob(d,v)]
                elif def_type==Syntax.RAW_DEF:#RAW_DEF
                    self.TG.linkInnerEdges(job.trace_index,d,v.simple_access_str())
                    return []
                elif def_type==Syntax.NORMAL_ASSIGN:
                    self.TG.linkInnerEdges(job.trace_index,d,v.simple_access_str())
                    assign_handler=AssignmentHandler(self.l,self.TG)
                    jobs=assign_handler.getJobs(v,d,indexes)
                    return jobs
                elif def_type==Syntax.OP_ASSIGN:
                    self.TG.linkInnerEdges(job.trace_index,d,v.simple_access_str())
                    assign_handler=AssignmentHandler(self.l,self.TG)
                    jobs=assign_handler.getJobs(v,d,indexes)
                    jobs.append(TaintJob(d, v))
                    return jobs
                elif def_type == Syntax.RETURN_VALUE_ASSIGN:
                    self.TG.linkInnerEdges(job.trace_index,d,v.simple_access_str())
                    jobs=self.handleReturnAssignDirect(job.trace_index,d,v)
                    return jobs
                elif def_type==Syntax.SYS_LIB_DEF:
                    self.TG.linkInnerEdges(job.trace_index,d,v.simple_access_str())
                    jobs= Syntax.handle_sys_lib_def(d,v,self.l[d].codestr)
                    return list(set(jobs))
                else:
                    #job.traceIndex-->l.index(line)
                    #f(t->q) variable:t syntax:*(t->q)
                    #track the access variable t->q
                    #truncate the outter syntax (->q,*) minus ( ->q)= (*)
                    #use new syntax to checkArgDef----- var:t->q,syntax:*
                    #----------------
                    result=Syntax.isPossibleArgumentDefinition(self.l[d],v)
                    if result is not None:
                        rfl,p,childnum,callee,arg=result
                        if "->headindex" in p and "header_read"==callee:
                            print callee
                        jobs,b=self.checkArgDef(d,job.trace_index,job.trace_index,p,rfl,childnum,callee)
                        if b:
                            return jobs
        if len(indexes)>0:
            i=indexes[0]-1
        else:
            i=job.trace_index-1
        
        print self.l[i]
        #l[i] must be an instance of FunctionCallInfo
        if abs(i) % len(self.l)==0 and abs(self.record_manager.i)==len(self.record_manager.lines):#begin
            if job.var.v in self.l[i].param_list:
                self.TG.linkInnerEdges(job.trace_index,i,job.var.simple_access_str())
            return []
        print self.get(i-1) #fetchSome to contain i-1
        if self.l[i].get_func_name().split("::")[-1].strip() in self.l[i-1].codestr and self.l[i]==self.l[job.trace_index].get_func_call_info():#call point
            if job.var.v in self.l[i].param_list:
                self.TG.linkInnerEdges(job.trace_index,i,job.var.simple_access_str())
                return [TaintJob(i,job.var)]
            return []
        elif self.isMacroCall(i-1):
            if job.var.v in self.l[i].param_list:
                self.TG.linkInnerEdges(job.trace_index,i,job.var.simple_access_str())
                return [TaintJob(i,job.var)]
            return []
        return []

    def handleReturnAssignDirect(self,beginIndex,i,var):
        leftvar=self.l[i].codestr.split('=')[0].strip()
        variable_pat=re.compile(Syntax.variable)
        if variable_pat.match(leftvar):
            accesspattern=var.matchAccessPattern(leftvar)
            return self.handleReturnAssgin(beginIndex,i,accesspattern,var)
        else:
            print "Fatal Error! the return assginment is wrongly recognized! Please check the matchDefinitionType"  
            print 1/0
                  
    def handleReturnAssgin(self,job_trace_index,i,accesspattern,var):
        if i+2+1<len(self.l) and isinstance(self.l[i+1],FunctionCallInfo) and isinstance(self.l[i+2],LineOfCode):
            if self.l[i+1].get_func_name().split("::")[-1].strip() in self.l[i].codestr or self.isMacroCall(i):
                indexes=self.slice_same_func_lines(i+2, job_trace_index)
                count=0
                print "accesspattern:",accesspattern
                for idx in indexes[::-1]:
                    print "check return line:",self.l[idx]
                    if 'return ' in self.l[idx].codestr:
                        self.TG.linkExpandEdges(job_trace_index,idx,"return dependency:"+var.simple_access_str())
                        #self.TG.linkTraverseEdges(i,idx,"ref:"+var.simple_access_str())
                        start=re.search(r'return\s*',self.l[idx].codestr).span()[1]
                        rightpart=self.l[idx].codestr[start:].strip().rstrip(';').strip()
                        if Syntax.isUniqueNonLibCall(rightpart):
                            jobs=self.handleReturnAssgin(job_trace_index,idx,accesspattern,var)
                            return self.taintUp(jobs)
                        else:
                            variable_pat=re.compile('^'+Syntax.variable+'$')
                            m=variable_pat.match(rightpart)
                            if m:
                                rfl,p=accesspattern
                                return self.taintUp([TaintJob(idx,TaintVar(rightpart,p,rfl))])
                            else:
                                taint_v_strs = Filter.expression2vars(rightpart)
                                jobs=map(lambda x : TaintJob(idx,x),[TaintVar(tv,[]) for tv in taint_v_strs])
                                return self.taintUp(jobs)
                    count+=1
                    if count == 3:break
                return []
        print "Fatal Error! the malformed call detail lines after return value assignment!"  
        print 1/0            
    
    def likeArgDef(self,v,codestr):
        if v.pointerStr():
            return re.search("\(.*"+v.pointerStr()+".*\)", codestr) or re.search("\(.*&\s*"+v.accessStr()+".*\)", codestr)
        else:
            return re.search("\(.*&\s*"+v.accessStr()+".*\)", codestr)
                        
    def getDefs(self,pairs,indexes,uppdefindex=-1):
        if indexes==[]:#BUG:please check this situation
            return []
        if uppdefindex==-1:
            uppdefindex=indexes[0]-1
        defs=[]
        for index,v,left_propa,up,low in pairs[::-1]:
            if isinstance(self.l[index],LineOfCode) and index<=uppdefindex:continue
            #note that the index of downward tainting param pointer should be set to the first code line
            #Or it will be aborted as it matched the "=".
            if indexes[low-1]<=uppdefindex:continue
            for i in indexes[up:low][::-1]:
                print "getDefs():Checking Def:",self.l[i]
                access=v.accessStr()
                if re.search(access, self.l[i].codestr):
                    maybe_def=True
                else:
                    maybe_def=False
                    pointerstr=v.pointerStr()
                    if pointerstr is not None:
                        if re.search(pointerstr, self.l[i].codestr):
                            maybe_def=True
                    
                if maybe_def:
                    def_type=self.matchDefinitionType(i,v)
                    #if def_type==Syntax.FOR or def_type==Syntax.NORMAL_ASSIGN or def_type==Syntax.OP_ASSIGN or def_type==Syntax.INC or def_type==Syntax.RAW_DEF or def_type==Syntax.SYS_LIB_DEF:#ASSIGN
                    if def_type!=Syntax.NODEF:
                        defs.append((i,v))
                        print "Find the 100% definition."
                        break
                    elif self.likeArgDef(v,self.l[i].codestr):
                        print "Check Possible Definitions:",self.l[i]
                        if isinstance(self.l[i+1],FunctionCallInfo):
                            if Syntax.isPossibleArgumentDefinition(self.l[i],v):
                                defs.append((i,v))
                                print "Yes,it is Possible Definitions."
                                print "But just possible,maybe 10%. We should continue search at least another 100% definition for assurance."
                elif self.likeArgDef(v,self.l[i].codestr):
                    print "Check Possible Definitions:",self.l[i]
                    if isinstance(self.l[i+1],FunctionCallInfo):
                        if Syntax.isPossibleArgumentDefinition(self.l[i],v):
                            defs.append((i,v))
                            print "Yes,it is Possible Definitions."
                            print "But just possible,maybe 10%. We should continue search at least another 100% definition for assurance."
        defs.sort(key=lambda x:x[0],reverse=True)#index reversed order
        return defs
    
    def isLeftPropagate(self,v,codestr):
        declare_pat=Syntax.declaration_left_propagate_pattern(v)
        variable_pat=Syntax.variable_left_propagate_pattern(v)
        print "Left Propagation Pattern:\n",declare_pat,'\n',variable_pat
        vp_m=re.search(variable_pat,codestr)
        if vp_m:
            return vp_m
        else:
            dp_m=re.search(declare_pat,codestr)
            if dp_m:
                return dp_m
            else:
                return None
    def findAllReferences(self, var, indexrange, left_propa):
        visited=set()
        pairs=set()
        if indexrange==[]:return []
        indexrange.sort()
        V=set([(indexrange[0],var,left_propa,0,len(indexrange))])
        if left_propa:
            for temp_lb in range(0,len(indexrange)):
                temp_index=indexrange[temp_lb]
                print var.pointerStr()
                print temp_index,self.l[temp_index]
                m=re.search(r'(?<![A-Za-z0-9_])'+var.pointerStr()+r"\s*=(?!=)",self.l[temp_index].codestr)
                if m:
                    result=Syntax.isPossibleArgumentDefinition(self.l[temp_index],var)
                    leftpart=m.group()[:-1].strip()
                    rfl,pat=var.matchAccessPattern(leftpart)
                    if rfl>0 or result is not None:
                        lb=temp_lb+1
                    else:
                        lb=temp_lb
                    V=set([(indexrange[0],var,left_propa,0,lb)])
                    break
        count=0
        while len(V)>0:
            A=set()
            for index,v,left_p,upperbound,lowerbound in V:
                #if not v.pointerStr():continue
                #lp=Syntax.left_ref_propagate_pattern(v)
                rp=Syntax.right_ref_propagate_pattern(v)
                print "Continue Check bellow the first found assignment:",self.l[index]
                for idx in range(upperbound,lowerbound):
                    aIndex=indexrange[idx]
                    if left_p and aIndex<index:
                        print "pass(accelerate)",v.simple_access_str()
                    elif aIndex in visited:
                        print "pass(accelerate)",v.simple_access_str()
                    elif re.search(r"[^=]=[^=]",self.l[aIndex].codestr) is None:
                        print "pass",v.simple_access_str()
                        visited.add(aIndex) 
                    else:
                        print "Line Under Check:",aIndex,"#",self.l[aIndex]
                        if "&hdr;" in self.l[aIndex].codestr:
                                print "Find IT!"
                        match=self.isLeftPropagate(v,self.l[aIndex].codestr)
                        if match is not None:
                            m_left_propgate=match
                            print "find left propagate:",self.l[aIndex]
                            array=m_left_propgate.group().split("=")
                            leftpart=array[0].split()[-1].lstrip("*")
                            rightpart=array[1].strip()
                            rightvar=rightpart.rstrip(";").strip()
                            if rightvar[0]=="(":
                                stack=[]
                                i=1
                                while i<len(rightvar):
                                    if rightvar[i]=="(":
                                        stack.append("(")
                                    elif rightvar[i]==")":
                                        if len(stack)>0:
                                            stack.pop()
                                        else:
                                            rightvar=rightvar[i+1:].strip().lstrip("(").rstrip(")").strip()
                                            break
                                    i+=1
                            rfl,pat=v.matchAccessPattern(rightvar)
                            if "*"==pat[-1] or "->" in pat[-1] and aIndex>index:
                                if rfl<=0:rfl=1
                            q=TaintVar(leftpart,pat,rfl,True)#Note that we should take ref_len in to consideration.
                            lb=lowerbound
                            if idx+1<lowerbound:
                                for temp_lb in range(idx+1,lowerbound):
                                    temp_index=indexrange[temp_lb]
                                    print v.pointerStr()
                                    print q.pointerStr()
                                    print temp_index,self.l[temp_index]
                                    if re.search(q.pointerStr()+r"\s*[^=]=[^=]",self.l[temp_index].codestr):
                                        result=Syntax.isPossibleArgumentDefinition(self.l[temp_index],q)
                                        if result is not None:
                                            lb=temp_lb+1
                                        else:
                                            lb=temp_lb
                                        break     
                            pairs.add((aIndex,q,True,idx+1,lb))
                            A.add((aIndex,q,True,idx+1,lb))
                            visited.add(aIndex)
                        elif rp:
                            print rp
                            m_right_propgate=re.search(rp,self.l[aIndex].codestr)
                            if m_right_propgate:
                                array=m_right_propgate.group().split("=")
                                leftpart=array[0].strip()
                                rightpart=array[1].strip()
                                rightvar=rightpart.rstrip(";").strip()
                                rfl,pat=v.matchAccessPattern(leftpart)
                                # BUG if look downward
                                if rfl==0:
                                    print "HEY"
                                if left_p and rfl>0:#v is KILLED here! Skip the following index range, and inform other left propagation
                                    lowerbound=indexrange.index(aIndex)
                                    #Stop find other references
                                    #Because it's killed here. LOWER statements that use it is meaningless
                                    break
                                if "*"==pat[-1] or "->" in pat[-1] and aIndex>=index:
                                    if rfl<=0:rfl=1
                                q=TaintVar(rightvar,pat,rfl,True)#Note that we should take ref_len in to consideration.
                                print aIndex,self.l[aIndex]
                                print q
                                print v
                                pairs.add((aIndex,q,False,upperbound,lowerbound))
                                A.add((aIndex,q,False,upperbound,lowerbound))
                                visited.add(aIndex)
            count+=1
            V=A
        pairs=list(pairs)
        print "refrences list-------"
        for pair in pairs:
            print pair[0],pair[1],pair[2],pair[3],pair[4]
        pairs.sort(lambda x,y:cmp(x[0],y[0]))
        return pairs
    
    def slice_same_func_lines(self,index,lowerBound):
        indexes=[]
        #find lower same function lines
        tail_bracket_pattern=re.compile(r'^\s*\}\s*$')
        i=index
        while i<lowerBound:
            print "Checking Same Function Line:", self.l[i]
            if isinstance(self.l[i], LineOfCode) and self.l[i].get_func_call_info()==self.l[index].get_func_call_info():
                indexes.append(i)
                print "Same Function!"
            elif  isinstance(self.l[i], FunctionCallInfo):
                if isinstance(self.l[i-1], LineOfCode) and self.l[i-1].get_func_call_info()==self.l[index].get_func_call_info():
                    print self.l[i-1].codestr
                    if tail_bracket_pattern.match(self.l[i-1].codestr) is not None:
                        break
            i+=1
        
        #find upper same function lines
        i=index
        while i>0:
            if isinstance(self.l[i], LineOfCode) and self.l[i].get_func_call_info()==self.l[index].get_func_call_info():
                print self.l[i]
                indexes.append(i)
            if isinstance(self.l[i], FunctionCallInfo) and self.l[i] == self.l[index].get_func_call_info():
                if isinstance(self.l[i-1], LineOfCode):
                    if self.l[i].get_func_name().split("::")[-1] in self.l[i-1].codestr:
                        break
                elif isinstance(self.l[i-2], LineOfCode):
                    if self.l[i].get_func_name().split("::")[-1] in self.l[i-2].codestr:
                        break
            i-=1
        if lowerBound==len(self.l):
            print "Now lowerBound is unlimited."
        else:
            print "lowerBound line is:",self.l[lowerBound]
        indexes=list(set(indexes))
        indexes.sort()
        return indexes#[i for i in indexes if i!=index]
    
    def check_va_arg_style(self,skip_va_arg_nums,indexes):
        skip=skip_va_arg_nums
        for i in indexes:
            m = re.search(Syntax.lt+r"va_arg"+Syntax.water+r"\(",self.l[i].codestr)
            if m:
                if skip == 0:
                    left_var = self.l[i].codestr[:m.span()[0]].strip().rstrip('=').split()[-1]
                    idx=indexes.index(i)
                    return left_var,indexes[idx:]
                skip-=1
        return None       
  
    def checkArgDef(self,callsiteIndex,beginIndex,lowerBound,p,rfl,childnum,callee):
        if p==[] or isinstance(self.l[callsiteIndex+1],LineOfCode):#Abort non-pointer variable.
            return [],False
        #Note: funciton name and callee name may not be equal as there exist macro and function pointer
        #e.g. nread = abfd->iovec->bread (abfd, ptr, size);          
        indexes=self.slice_same_func_lines(callsiteIndex+2,lowerBound)#PlUS TWO("callsiteIndex+2")means 
        #start from the first line of callee function.
        params=self.l[callsiteIndex+1].get_param_list().split(",")
        if len(params)-1<childnum:
            skip_va_arg_nums=childnum-len(params)
            res=self.check_va_arg_style(skip_va_arg_nums,indexes)
            if not res:
                print "BAD arg-->param number match!"
                print 1/0
            varname,indexes=res
            var= TaintVar(varname,p,rfl)
        else:
            #FIX ME following part should change for va_arg case
            #----------------------------------------------------------------------------------------#
            varname=params[int(childnum)].split("=")[0]
            #handle "=" cases like:
            #args_callback_command (name=0xbfffeb26 "swfdump0.9.2log/exploit_0_0", val=val@entry=0x0) at swfdump.c:200
            print self.l[callsiteIndex+1]
            var=TaintVar(varname,p,rfl)
            #---------------------------------------------------------------------------------------#
        
        pairs=self.findAllReferences(var,indexes,True)
        pairs.append((callsiteIndex+1,var,True,0,len(indexes)))
        defs=self.getDefs(pairs,indexes)
        for d,v in defs:
            print "%%%",self.l[d]
        for d,v in defs:
            #BUG
            def_type=self.matchDefinitionType(d,v)
            if def_type==Syntax.FOR:
                self.TG.linkCrossEdges(beginIndex,d,v.simple_access_str())
                jobs=Syntax.generate_for_jobs(d, self.l[d].codestr, v)
                return self.taintUp(jobs),True
            if def_type==Syntax.INC:#INC
                self.TG.linkCrossEdges(beginIndex,d,v.simple_access_str())
                jobs.append(TaintJob(d,v))
                jobs=list(set(jobs))
                return self.taintUp(jobs),True
            elif def_type==Syntax.RAW_DEF:#RAW_DEF
                self.TG.linkCrossEdges(beginIndex,d,v.simple_access_str())
                return [],True
            elif def_type==Syntax.NORMAL_ASSIGN:
                self.TG.linkCrossEdges(beginIndex,d,v.simple_access_str())
                assign_handler=AssignmentHandler(self.l,self.TG)
                jobs=assign_handler.getJobs(v,d,indexes)
                return self.taintUp(jobs),True
            elif def_type==Syntax.OP_ASSIGN:
                self.TG.linkCrossEdges(beginIndex,d,v.simple_access_str())
                assign_handler=AssignmentHandler(self.l,self.TG)
                jobs=assign_handler.getJobs(v,d,indexes)
                jobs.append(TaintJob(d, v))
                return self.taintUp(jobs),True
            elif def_type == Syntax.RETURN_VALUE_ASSIGN:
                self.TG.linkCrossEdges(beginIndex,d,v.simple_access_str())
                jobs=self.handleReturnAssignDirect(beginIndex,d,v)
                return jobs
            elif def_type==Syntax.SYS_LIB_DEF:
                self.TG.linkCrossEdges(beginIndex,d,v.simple_access_str())
                jobs= Syntax.handle_sys_lib_def(d,v,self.l[d].codestr)
                return self.taintUp(jobs),True
            else:
                #job.traceIndex-->l.index(line)
                #f(t->q) variable:t syntax:*(t->q)
                #track the access variable t->q
                #truncate the outter syntax (->q,*) minus ( ->q)= (*)
                #use new syntax to checkArgDef----- var:t->q,syntax:*
                #----------------
                result=Syntax.isPossibleArgumentDefinition(self.l[d],v)
                if result is not None:
                    rfl,p,childnum,callee,arg=result
                    jobs,b=self.checkArgDef(d,beginIndex,lowerBound,p,rfl,childnum,callee)
                    if b:
                        return self.taintUp(jobs),True
                            
        return [],False
    
    def matchDefinitionType(self,i,var):
        codestr=self.l[i].codestr
        if var.v=='i':
            print "GotIt!!"
        access=var.accessStr()
        print "Checking Definition Type for:",access
        print "codestr:",codestr
        
        if Syntax.isForStatement(codestr):
            if re.search(access+r"\s*=[^=]",codestr) or re.search(access+r"(\+\+|--)",codestr):
                return Syntax.FOR
        if Syntax.isIncDef(var.v, codestr):
            return Syntax.INC
        
        #inc operation detection must be before the assignment.
        #because when detecting variable (i) in case such as: "for (int i=-1;i<m;i++){",
        #INC result must be returned as ForJobGenerator is only called in handle branch of INC operation
        #in "lastModification" and "CheckingArgDefinition" function.
        #This weird behavior need be fixed in future. 
        
        normal_assginment=Syntax.normal_assignment_pattern(access)
        match=re.search(normal_assginment,codestr)
        if match:
            rightstr=codestr[match.span()[1]:].rstrip(';')
            if Syntax.isUniqueNonLibCall(rightstr):
                if i+2+1<len(self.l) and isinstance(self.l[i+1],FunctionCallInfo) and isinstance(self.l[i+2],LineOfCode):
                    if self.l[i+1].get_func_name().split("::")[-1].strip() in self.l[i].codestr:
                        return Syntax.RETURN_VALUE_ASSIGN
                    elif self.isMacroCall(i):
                        return Syntax.RETURN_VALUE_ASSIGN
            return Syntax.NORMAL_ASSIGN
        op_assignment=Syntax.op_assignment_pattern(access)
        if re.search(op_assignment,codestr):
            return Syntax.OP_ASSIGN
        raw_definition=r"^\s*\{\s*[A-Za-z_][A-Za-z0-9_]+\s+(\*\s*)*([A-Za-z_][A-Za-z0-9_]+\s*,\s*)*"+var.v+"\s*;"
        if re.search(raw_definition, codestr):
            print "Raw definition:",codestr
            return Syntax.RAW_DEF
        if Syntax.isLibArgDef(var,codestr):
            return Syntax.SYS_LIB_DEF
        return  Syntax.NODEF
            
if __name__=="__main__":
    #m=MacroInspector("test/gdb_logs/swfmill-0.3.3/swfmill-0.3.3")
    #rm=RecordManager("test/gdb_logs/swfmill-0.3.3/gdb-swfmill-0.3.3__new_unsigned_char[length]_exploit_0_0.txt")
    m=MacroInspector("test/gdb_logs/swftools-0.9.2/swftools-0.9.2/")
    rm=RecordManager("test/gdb_logs/swftools-0.9.2/swfstrings/gdb-swfstrings_fonts_t.txt",m)
    rm.fetchSome()
    tracker=Tracker(rm)
    traceIndex=-1
    #tracker.setStartJobs(traceIndex, [TaintVar("length",[])])
    taintVars=[TaintVar("fonts",['*']),TaintVar("t",[])]
    tracker.setStartJobs(traceIndex,taintVars)
    TG=tracker.track()
    output=file("output.dot", 'w')
    print TG.serialize2dot()
    output.write(TG.serialize2dot())
    output.close()
    subprocess.call("dot -Tpng output.dot -o output.png", shell = True)
    #print str(TG)