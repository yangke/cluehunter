'''
Created on Sep 9, 2015

@author: yangke
'''
import re
import subprocess
from model.TaintGraph import TaintGraph
from parse.parse import LogParser
from model.TaintJob import TaintJob
from model.TaintVar import TaintVar
from parse.FunctionCallInfo import FunctionCallInfo
from parse.LineOfCode import LineOfCode
from utils.Filter import Filter
from syntax.syntax import Syntax
#===============================================================================
# FIX ME: We need to define two colors for control and data dependency:
# "BLUE" for control dependency and "RED" for data dependency.
# Define them like the following:
# BLUE=0x1
# RED=0x2
# BOTH=BLUE&RED=0x3
#===============================================================================

class Tracker:
    def __init__(self,l):
        self.l=l 
          
    def track(self):
        self.createTaintGraph()
        return self.TG
    
    def setStartJobs(self,traceIndex,varset):
        self.start_jobs=[]
        for var in varset:
            self.start_jobs.append(TaintJob(traceIndex,var))
        
    def createTaintGraph(self):
        self.TG=TaintGraph(self.l)
        c = self.taintUp(self.start_jobs)
        while(c!=[]):
            c = self.taintUp(c)
    def findPositions(self,P,funcInfo):
        positions=set()#get param positions
        for p in P:
            find_this=0
            print "param var:",p
            for i,param in enumerate(funcInfo.param_list.split(',')):
                print "index,paramstr:",i,param
                if "=" not in param:
                    find_this+=1
                if "this=this@entry" not in param:
                    if p.var.v in param:
                        positions.add((i-find_this,p.var))
                else:
                    find_this+=1
        print "positions:"
        for pos in positions:print str(pos[0])
        return positions
    def getCallSiteArgs(self,positions,upperIndex,funcInfo):
        func_name_to_search=funcInfo.get_func_name().split("::")[-1].strip()
        p=r"^.*"+func_name_to_search+r"\s*\("
        print "The function name to search:",func_name_to_search
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
        print "Search for line that match syntax:",p
        print "upper line:",self.l[upperIndex]
        print "group:",m.group()
        rightstr=self.l[upperIndex].codestr.replace(m.group(),"")#not use lstrip, it may cause wrong answer
        print "rightstr:",rightstr
        stack=[]
        i=0
        while i<len(rightstr):
            if rightstr[i]==")":
                if len(stack)==0:
                    print "normal match arglist"
                    break
                else:
                    stack.pop()
            elif rightstr[i]=="(":
                stack.append("(")
            i+=1
        print "rightstr:",rightstr
        args=rightstr[:i].split(',')#not strip yet
        print "arguments:",args
        return args,upperIndex
    def taintUp(self,jobs):
        if jobs ==[]:return []
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
            print "****",funcInfo
            positions=self.findPositions(P,funcInfo)
            print "The inter point and the Old line:",self.l[traceIndex]
            upperIndex=traceIndex-1#try to find last call site
            args,upperIndex=self.getCallSiteArgs(positions,upperIndex,funcInfo)
            cjobs=set()
            #===================================================================
            # if upperIndex==175:
            #     print upperIndex,"#",self.l[upperIndex]
            #===================================================================
            for pos,param in positions:
                arg=args[pos].strip()
                self.TG.linkInterEdges(traceIndex,upperIndex,param,arg,pos)
                print "arg expression:",arg
                identifiers=Filter.expression2vars(arg)
                print "variables in arg expression",identifiers
                first=True
                for identifier in identifiers:
                    print "identifier in call site:",identifier
                    accessp=[e for e in param.p]
                    print "param_pattern:",param.p
                    if arg[0]=="&" and first and len(param.p)>0:
                        if param.p[-1]=="*":
                            accessp=param.p[:-1]
                        first=False
                    #if not Filter.isConstants(identifier):
                    job=TaintJob(upperIndex,TaintVar(identifier,accessp))
                    cjobs.add(job)
            return cjobs
    def taintOneStepUp(self,jobs):
        newjobs=set()
        for job in jobs:
            jbs=self.lastModification(job)
            nj=set(jbs)
            for jj in nj:
                if jj.var.v=="1":
                    print "hell"
                    print job.var.v
            newjobs=newjobs|nj
        paramjobs=set()
        normaljobs=set()
        for job in newjobs:
            if job.isParamJob(self.l):
                paramjobs.add(job)
            else:
                normaljobs.add(job)
        return paramjobs,normaljobs
    #===========================================================================
    # def getUpperBound(self,job):
    #     i=job.trace_index
    #     if isinstance(self.l[job.trace_index],FunctionCallInfo):
    #         print "Fatal Error: PARAM JOB should not be passed to lastModification()!!!!!!!!!!!!"
    #         return -1
    #     while i>0:
    #         if isinstance(self.l[i], FunctionCallInfo) and isinstance(self.l[i-1], LineOfCode):
    #             if self.l[i]==self.l[job.trace_index].get_func_call_info():
    #                 if self.l[i].get_func_name().split("::")[-1] in self.l[i-1].codestr:
    #                     return i-1
    #         i-=1
    #     print "Error Cannot find the same function segments in upper indexes!"
    #     return -1
    #===========================================================================
    def lastModification(self,job):
        print "Now we are checking for last definition of ",job.var
        #=======================================================================
        # BUUUUUUUUUUUG
        # Cannot handle the following case:
        # We need first time reference definition check
        # main () at foomoo.c:3
        # 3        int a=1, b=2;
        # 4        int *p = &a;
        # 5        int *q = &b;
        # 6        int *c = q;
        # 7        *q=foo(&a,&b);
        # foo (x=0xbfffe83c, y=0xbfffe840) at foomoo.c:14
        # 14        return *x%=(*x)+(*y);
        # 15    }
        # main () at foomoo.c:8
        # 8        *p=moo(p,c);
        # moo (x=0xbfffe83c, y=0xbfffe840) at foomoo.c:18
        # 18        return *x-*y;
        # 19    }
        # main () at foomoo.c:9
        # 9        moo(p,c);
        # moo (x=0xbfffe83c, y=0xbfffe840) at foomoo.c:18
        # 18        return *x-*y;
        # 19    }
        # main () at foomoo.c:10
        # 10        return 1/a;
        #=======================================================================
        i=job.trace_index-1
        jobs=[]
        needSeeBellow = False
        lowerBound=job.trace_index
        while True:
            print i,"#",self.l[i]
            print job.trace_index,"#",self.l[job.trace_index]
            if i==450:
                print "HEY"
            if isinstance(self.l[i], FunctionCallInfo):
                
                if i==0:#begin
                    if job.var.v in self.l[i].param_list:
                        self.TG.linkInnerEdges(job.trace_index,i,job.var.simple_access_str())
                    return []
                elif self.l[i].get_func_name().split("::")[-1].strip() in self.l[i-1].codestr and self.l[i]==self.l[job.trace_index].get_func_call_info():#call point
                    if job.var.v in self.l[i].param_list:
                        self.TG.linkInnerEdges(job.trace_index,i,job.var.simple_access_str())
                        return [TaintJob(i,job.var)]
                    return []
                elif i-2>0 and isinstance(self.l[i-2], LineOfCode) and self.l[i].get_func_name().split("::")[-1] in self.l[i-2].codestr and self.l[i]==self.l[job.trace_index].get_func_call_info():#call point
                        if job.var.v in self.l[i].param_list:
                            self.TG.linkInnerEdges(job.trace_index,i,job.var.simple_access_str())
                            return [TaintJob(i,job.var)]        
                else:#This is a return point after call other functions
                    lowerBound=i
                    print self.l[i]
                    i=lowerBound-1
                    print self.l[i]
                    while not self.l[i]==self.l[job.trace_index].get_func_call_info() and i>-1:#find the nearest same function segment
                        #print str(self.l[i]),"NEQ",self.l[lowerBound]
                        i-=1
                    i+=1
                    while isinstance(self.l[i],LineOfCode) and i<lowerBound:#find last statement
                        i+=1
                    needSeeBellow = True
                    print "need see bellow:",i,"#",self.l[i]
            elif job.var.v in self.l[i].codestr:
                if job.var.v=="ucptr":
                    print "teah"
                if needSeeBellow:
                    print "see bellow of the call site:",i,"#",self.l[i]
                    needSeeBellow=False
                    if i==474:
                        print "OH no!"
                    result=Syntax.isPossibleArgumentDefinition(self.l[i],job.var)
                    if result is not None:
                        rfl,p,childnum,callee=result
                        ###########################################################
                        #jobs,findIt=self.checkArgDef(i,job.trace_index,lowerBound,p,rfl,childnum,callee)
                        jobs,findIt=self.checkArgDef(i,job.trace_index,job.trace_index,p,rfl,childnum,callee)
                        if findIt:return jobs
                        print self.l[i].codestr.strip(),"does not contains arg definiton."
                def_type=Syntax.matchDefinitionType(self.l[i].codestr,job.var)
                print "still finding var:",job.var
                if def_type!=Syntax.NODEF:
                    if job.trace_index-i>1:
                        #LONG SKIP! We need to check the reference modification.
                        print 'LONG SKIP!',job.trace_index-i,". We need to check the reference modification."
                        if i==206:
                            print self.l[i]
                        if job.trace_index-i==1088:
                            print "HEY!" 
                        print job.var
                        ###############################################
                        #BUGBUUUUUUUUUUUUUUUUUUUGGGGGGGGGGGGGGGGGGGGGG!!!!
                        jobs=self.check_ref_modification(job,i,lowerBound)
                        #Try to fix the lower bound wrongly upper problem
                        if jobs is not None:
                            return jobs
                    if def_type == Syntax.FOR:
                        self.TG.linkInnerEdges(job.trace_index,i,job.var.simple_access_str())
                        jobs=Syntax.generate_for_jobs(i, self.l[i].codestr, job.var)
                        return self.taintUp(jobs)
                    elif def_type == Syntax.INC:
                        self.TG.linkInnerEdges(job.trace_index,i,job.var.simple_access_str())
                        jobs.append(TaintJob(i,job.var))
                        jobs=list(set(jobs))
                        return self.taintUp(jobs)
                    elif def_type==Syntax.RAW_DEF:
                        self.TG.linkInnerEdges(job.trace_index,i,job.var.simple_access_str())
                        return []
                    elif def_type==Syntax.SYS_LIB_DEF:
                        self.TG.linkInnerEdges(job.trace_index,i,job.var.simple_access_str())
                        return Syntax.handle_sys_lib_def(i,job.var.v,self.l[i].codestr)
                    elif def_type == Syntax.NORMAL_ASSIGN or def_type == Syntax.OP_ASSIGN:
                        print "ASSIGNMENT FOUND:", self.l[i].codestr
                        self.TG.linkInnerEdges(job.trace_index,i,job.var.simple_access_str())
                        taintvars=Syntax.getVars(job.var,self.l[i])
                        print "job.var.v now:",job.var.v
                        print "tainted right vars:"
                        for var_ in taintvars:
                            print var_
                        if def_type==Syntax.OP_ASSIGN:
                            print "OPASSIN:",self.l[i]
                            taintvars.add(job.var)
                        jobs=map(lambda x : TaintJob(i,x), taintvars)
                        return jobs
            elif needSeeBellow:
                print job.var.v, 'NOT IN', self.l[i].codestr
                needSeeBellow=False
            i-=1
            if i<0:return []
    def check_ref_modification(self,job,i,lowerBound):
        if "i" in str(job.var):
            print "haha"
        idxes=self.slice_same_func_lines(i,lowerBound)##BUG i+1
        if "t1.next = 0;" in self.l[i].codestr:
            print "GAAAAAA"
        pairs=self.findAllReferences(job.var,idxes)
        pairs.append((i+1,job.var,0,len(idxes)))
        defs=self.getDefs(pairs,idxes,i)
        for d,v in defs:
            def_type=Syntax.matchDefiniteDefinitionType(self.l[d].codestr,v)
            if def_type==Syntax.FOR:
                self.TG.linkInnerEdges(job.trace_index,d,v.simple_access_str())
                jobs=Syntax.generate_for_jobs(d, self.l[d].codestr, v)
                #return self.taintUp(jobs)
                return jobs
            if def_type==Syntax.INC:#INC
                self.TG.linkInnerEdges(job.trace_index,d,v.simple_access_str())
                jobs.append(TaintJob(d,v))
                jobs=list(set(jobs))
                #return self.taintUp(jobs)
                return jobs
            elif def_type==Syntax.RAW_DEF:#RAW_DEF
                self.TG.linkInnerEdges(job.trace_index,d,v.simple_access_str())
                return []
            elif def_type==Syntax.SYS_LIB_DEF:
                self.TG.linkInnerEdges(job.trace_index,d,v.simple_access_str())
                jobs= Syntax.handle_sys_lib_def(d,v.v,self.l[d].codestr)
                #return self.taintUp(jobs)
                return jobs
            elif def_type==Syntax.NORMAL_ASSIGN or def_type==Syntax.OP_ASSIGN:#ASSIGN
                self.TG.linkInnerEdges(job.trace_index,d,v.simple_access_str())
                taintvars=Syntax.getVars(v,self.l[d])
                if def_type==Syntax.OP_ASSIGN:
                    taintvars.add(v)
                jobs=map(lambda x : TaintJob(d, x), taintvars)
                #return self.taintUp(jobs)
                return jobs
            else:
                result=Syntax.isPossibleArgumentDefinition(self.l[d],v)
                if result is not None:
                    rfl,p,childnum,callee=result
                    jobs,b=self.checkArgDef(d,job.trace_index,lowerBound,p,rfl,childnum,callee)
                    if b:
                        #return self.taintUp(jobs)
                        return jobs
        return None
    def likeArgDef(self,v,codestr):
        if v.pointerStr():
            return re.search("\(.*"+v.pointerStr()+".*\)", codestr) or re.search("\(.*&\s*"+v.accessStr()+".*\)", codestr)
        else:
            return re.search("\(.*&\s*"+v.accessStr()+".*\)", codestr)
                        
    def getDefs(self,pairs,indexes,uppdefindex=-1):
        if indexes==[]:#BUUUUUUUUUUUUUG:please check this situation
            return []
        if uppdefindex==-1:
            uppdefindex=indexes[0]-1
        defs=[]
        for index,v,up,low in pairs[::-1]:
            if isinstance(self.l[index],LineOfCode) and index<=uppdefindex:continue
            #note that the index of downward tainting param pointer should be set to the first code line
            #Or it will be aborted as it matched the "=".
            if indexes[low-1]<=uppdefindex:continue
            for i in indexes[up:low][::-1]:
                print "Checking Def",self.l[i]
                access=v.accessStr()
                if re.search(access, self.l[i].codestr):
                    def_type=Syntax.matchDefinitionType(self.l[i].codestr,v)
                    #if def_type==Syntax.FOR or def_type==Syntax.NORMAL_ASSIGN or def_type==Syntax.OP_ASSIGN or def_type==Syntax.INC or def_type==Syntax.RAW_DEF or def_type==Syntax.SYS_LIB_DEF:#ASSIGN
                    if def_type!=Syntax.NODEF:
                        defs.append((i,v))
                        break
                    elif self.likeArgDef(v,self.l[i].codestr):
                        print "Check Possible Definitions:",self.l[i]
                        if isinstance(self.l[i+1],FunctionCallInfo):
                            if Syntax.isPossibleArgumentDefinition(self.l[i],v):
                                defs.append((i,v))
                                print "Yes,it is Possible Definitions."
                                break
                elif self.likeArgDef(v,self.l[i].codestr):
                    print "Check Possible Definitions:",self.l[i]
                    if isinstance(self.l[i+1],FunctionCallInfo):
                        if Syntax.isPossibleArgumentDefinition(self.l[i],v):
                            defs.append((i,v))
                            print "Yes,it is Possible Definitions."
                            break
        defs.sort(key=lambda x:x[0],reverse=True)#index reversed order
        return defs
    
    def findAllReferences(self,var,indexrange):
        visited=set()
        pairs=set()
        if indexrange==[]:return []
        indexrange.sort()
        V=set([(indexrange[0],var,True,0,len(indexrange))])
        #(varindex,var,left_p,upperbound,lowerbound)
        #index >lowerbound index <=upperbound
        count=0
        while len(V)>0:
            A=set()
            for index,v,left_p,upperbound,lowerbound in V:
                #if not v.pointerStr():continue
                lrp=Syntax.left_ref_propagate_pattern(v)
                rrp=Syntax.right_ref_propagate_pattern(v)
                
                if count==0:
                    print "Check bellow the first found assignment:",self.l[index]
                    print "For ref assignment:"
                    if "for( ; i<argc && command==NULL; i++ ) {" in  self.l[index].codestr:
                        print "*****EE****"
                    for aIndex in indexrange[upperbound:lowerbound][::-1]:#search from down to up
                        print self.l[aIndex]
                        if rrp:
                            if r"=" not in self.l[aIndex].codestr:
                                visited.add(aIndex)
                                continue
                            m_right_propgate=re.search(rrp,self.l[aIndex].codestr)
                            if m_right_propgate:
                                if aIndex not in visited:
                                    array=m_right_propgate.group().split("=")
                                    leftpart=array[0].strip()
                                    rightpart=array[1].strip()
                                    rightvar=rightpart.rstrip(";").strip()
                                    rfl,pat=v.matchAccessPattern(leftpart)
                                    # BUG if look downward
                                    if rfl<=0:#Not in arg definition
                                        upperbound=indexrange.index(aIndex)-1#The last(effective) right propagation of v. e.g. v=p
                                        #For the following left propagation of v (e.g. q_low=v) is usefull.
                                        #But the upper left and right propagation of v (e.g. "q_up=v;" or "v=&X") is useless.
                                        #This time we doesn't correct rfl value as it is an assignment.
                                        q=TaintVar(rightvar,pat,rfl,True)#Note that we should take ref_len in to consideration.
                                        pairs.add((aIndex,q,upperbound,lowerbound))
                                        A.add((aIndex,q,False,upperbound,lowerbound))
                                        visited.add(aIndex)
                                        break
                                    elif left_p:#rfl>0 
                                        lowerbound=aIndex
                                        #e.g p->next->data: p->next=m
                                        #we don't care p->next->data=m as m will not propagate
                print "Continue Check bellow the first found assignment:",self.l[index]
                for aIndex in indexrange[upperbound:lowerbound]:
                    if left_p and aIndex<index :continue
                    if aIndex in visited:continue
                    
                    print self.l[aIndex]
                    
                    if r"=" not in self.l[aIndex].codestr:
                        visited.add(aIndex)
                        continue
                    m_left_propgate=re.search(lrp,self.l[aIndex].codestr)
                    if m_left_propgate:
                        array=m_left_propgate.group().split("=")
                        leftpart=array[0].strip()
                        rightpart=array[1].strip()
                        rightvar=rightpart.rstrip(";").strip()
                        rfl,pat=v.matchAccessPattern(rightvar)
                        if "*"==pat[-1] or "->" in pat[-1] and aIndex>index:
                            if rfl<=0:rfl=1
                        q=TaintVar(leftpart,pat,rfl,True)#Note that we should take ref_len in to consideration.
                        pairs.add((aIndex,q,upperbound,lowerbound))
                        A.add((aIndex,q,True,upperbound,lowerbound))
                        visited.add(aIndex)
                    elif rrp:
                        print rrp
                        m_right_propgate=re.search(rrp,self.l[aIndex].codestr)
                        if m_right_propgate:
                            array=m_right_propgate.group().split("=")
                            leftpart=array[0].strip()
                            rightpart=array[1].strip()
                            rightvar=rightpart.rstrip(";").strip()
                            rfl,pat=v.matchAccessPattern(leftpart)
                            # BUG if look downward
                            if left_p and rfl>0:#v is KILLED here! Skip the following index range, and inform other left propagation
                                lowerbound=indexrange.index(aIndex)
                                break
                            if "*"==pat[-1] or "->" in pat[-1] and aIndex>=index:
                                if rfl<=0:rfl=1
                            q=TaintVar(rightvar,pat,rfl,True)#Note that we should take ref_len in to consideration.
                            pairs.add((aIndex,q,upperbound,lowerbound))
                            A.add((aIndex,q,False,upperbound,lowerbound))
                            visited.add(aIndex)
            count+=1
            V=A
        pairs=list(pairs)
        print "refrences list-------"
        for pair in pairs:
            print pair[0],pair[1],pair[2],pair[3]
        pairs.sort(lambda x,y:cmp(x[0],y[0]))
        return pairs
    
    def slice_same_func_lines(self,index,lowerBound):
        indexes=[]
        i=index
        while i<lowerBound:
            if isinstance(self.l[i], LineOfCode) and self.l[i].get_func_call_info()==self.l[index].get_func_call_info():
                print self.l[i]
                indexes.append(i)
            elif  isinstance(self.l[i], FunctionCallInfo):
                print self.l[i]
            i+=1
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
            print "Now lowerBound is Unlimited."
        else:
            print self.l[lowerBound]
        return indexes
    def check_va_arg_style(self,skip_va_arg_nums,indexes):
        skip=skip_va_arg_nums
        for i in indexes:
            m = re.search(r"(?<![A-Za-z0-9_])va_arg\s*\(",self.l[i].codestr)
            if m:
                if skip == 0:
                    left_var = self.l[i].codestr[:m.span()[0]].strip().rstrip('=').split()[-1]
                    idx=indexes.index(i)
                    return left_var,indexes[idx:]
                skip-=1
        return None       
                
        
    def checkArgDef(self,callsiteIndex,beginIndex,lowerBound,p,rfl,childnum,callee):
        if p==[] or isinstance(self.l[callsiteIndex+1],LineOfCode):#Abort non-ponter variable.
            return [],False
        if callee.strip()!=self.l[callsiteIndex+1].get_func_name().strip(): #function name of callsite and callee must match.
            return [],False
        if callsiteIndex==474:#2716:
            print "FIND GAGAG!",self.l[callsiteIndex+1].get_param_list()
         
        indexes=self.slice_same_func_lines(callsiteIndex+2,lowerBound)#PlUS TWO("callsiteIndex+2")means start from the first line of callee function.
        params=self.l[callsiteIndex+1].get_param_list().split(",")
        if len(params)-1<childnum:
            skip_va_arg_nums=childnum-len(params)
            res=self.check_va_arg_style(skip_va_arg_nums,indexes)
            if not res:
                print "BAD arg--->param number match!"
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
            if rfl==1 or varname=="swf":
                print "yesss"
            var=TaintVar(varname,p,rfl)
            #---------------------------------------------------------------------------------------#
        
        pairs=self.findAllReferences(var,indexes)
        pairs.append((callsiteIndex+1,var,0,len(indexes)))
        defs=self.getDefs(pairs,indexes)
        for d,v in defs:
            print "%%%",self.l[d]
        for d,v in defs:
            ####BUUUUUUUUUUUUUUUUUUUG
            def_type=Syntax.matchDefinitionType(self.l[d].codestr,v)
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
            elif def_type==Syntax.SYS_LIB_DEF:
                self.TG.linkCrossEdges(beginIndex,d,v.simple_access_str())
                jobs= Syntax.handle_sys_lib_def(d,v.v,self.l[d].codestr)
                return self.taintUp(jobs),True
            elif def_type==Syntax.NORMAL_ASSIGN or def_type==Syntax.OP_ASSIGN:#ASSIGN
                self.TG.linkCrossEdges(beginIndex,d,v.simple_access_str())
                taintvars=Syntax.getVars(v,self.l[d])
                if def_type==Syntax.OP_ASSIGN:
                    taintvars.add(v)
                jobs=map(lambda x : TaintJob(d, x), taintvars)
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
                    rfl,p,childnum,callee=result
                    if "->headindex" in p and "header_read"==callee:
                        print callee
                    jobs,b=self.checkArgDef(d,beginIndex,lowerBound,p,rfl,childnum,callee)
                    if b:return self.taintUp(jobs),True
        return [],False
            
if __name__=="__main__":
    parser=LogParser()
    l=parser.parse("test/gdb_logs/swfmill-0.3.3/gdb-swfmill-0.3.3.txt")
    #tracker=Tracker(l,argv[1])
    tracker=Tracker(l)
    traceIndex=len(l)-1
    #tracker.setStartJobs(traceIndex, [TaintVar("dst",['*'])])
    tracker.setStartJobs(traceIndex, [TaintVar("length",[])])
    #tracker.setStartJobs(traceIndex, [TaintVar("ptr",["*"]),TaintVar("bytes",[]),TaintVar("most",[])])
    #tracker.setStartJobs(traceIndex, [TaintVar("most",[])])
    TG=tracker.track()
    output=file("baby", 'w')
    print TG.serialize2dot()
    output.write(TG.serialize2dot())
    output.close()
    subprocess.call("dot -Tpng baby -o b1.png", shell = True)
    #print str(TG)
    
