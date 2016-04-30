'''
Created on Apr 27, 2016

@author: yangke
'''
import re
from FunctionCallInfo import FunctionCallInfo
from LineOfCode import LineOfCode
from syntax.syntax import Syntax


class RecordManager(object):
    '''
    Manage the parsed trace list buffer and record lines.
    '''
    def __init__(self, start_line_num=None, log_file_path ='../gdb.txt', macro_inspector=None):
        logFile=file(log_file_path, 'r')
        self.lines = logFile.readlines()
        logFile.close()
        self.init_lines(start_line_num)
        self.init_patterns()
        self.l=[]
        self.macro_inspector=macro_inspector
        self.i=0
        #self.fetchSome()
        
        
    def set_macro_inspector(self,m):
        self.macro_inspector=m
            
    def init_lines(self,start_line_num):
        i=0
        while "Breakpoint 1," != self.lines[i][0:13] and "Temporary breakpoint 1, " != self.lines[i][0:24]:
            i+=1;
        j=-1
        while "Program received" not in self.lines[j]:
            j-=1
        j-=1
        j%=len(self.lines)
        if start_line_num is None:
            self.lines=self.lines[i:j]
        elif start_line_num % len(self.lines)<=i or start_line_num % len(self.lines)>j % len(self.lines) :
            print "Wrong line number! line number is out of the valid code range in the log file."
            print "start_line_num:",start_line_num,", but it should >",i,"and <=",j,"."
            print 1/0
        elif re.search(r"[0-9]", self.lines[start_line_num-1][0]) is None:
            print self.lines[start_line_num-1]
            print "Wrong line number! This is a function information line!"
            print 1/0
        elif re.search(r"^[0-9][1-9]*\s+in\s+", self.lines[start_line_num-1]):
            print "Wrong line number! This is a warning information line!"
            print 1/0
        else:
            self.lines=self.lines[i:start_line_num]
        print self.lines[0]
        if self.lines[0][0]=='B':
            self.lines[0]=self.lines[0].lstrip("Breakpoint 1, ")
        elif self.lines[0][0]=='T':
            self.lines[0]=self.lines[0].lstrip("Temporary breakpoint 1, ")
        
    def init_patterns(self):
        self.normalLinePattern = re.compile(r'^[0-9]+\s+.*\n')
        self.headInfoPattern = re.compile(r'^[A-Za-z_][A-Za-z0-9_]+.*\n')
        self.nullLinePattern = re.compile(r'^\s*\n')
        self.valueReturnLinePattern=re.compile(r'^(Value returned is |Run till exit from ).*')
        self.no_such_file_or_directory=r'No such file or directory.'
        self.hexHeadPattern=re.compile(r'^(0x[0-9a-f]+|[0-9][1-9]*)\s+in .*$')
        self.singleStepPattern=re.compile(r'^Single stepping until exit from function .*$')
        self.which_has_no_line_number_information=r'which has no line number information.'
        
    def get(self,i):
        #i must be a negative number
        while abs(i)>len(self.l):
            print i, len(self.l)
            print self.lines[0]
            print len(self.lines)
            self.fetchSome()
        return self.l[i]
    
    def should_ignore_and_ingore_following(self,line):
        if line[0]=='V' or line[0]=='R':#optimization
            if line[0:3]=='Val' or line[0:3]=='Run':
                if self.valueReturnLinePattern.match(line):
                    return True
        if re.search(self.no_such_file_or_directory,line):
            if re.search(r'"',line):
                return False
            return True
        if self.which_has_no_line_number_information in line:
            return True
        elif self.singleStepPattern.match(line):
            return True
        return False
    
    def fixBlock(self, blockOfNormalLines):
        if blockOfNormalLines==[]:
            return []
        linenum = blockOfNormalLines[-1].get_linenum()
        lines=sorted(list(set(blockOfNormalLines)),key=lambda line:line.get_linenum(),reverse=False)
        return [ x for x in lines if x.get_linenum()<=linenum] 
    
    def isNormalLine(self, line):
        if re.search(r'[1-9][0-9]',line[0:2]) or re.search(r'[1-9]\s',line[0:2]): 
            return True
        return False
    
    def fetchSome(self):
        firstMeetFuncInfo=None
        funcInfoStr=''
        funcInfo = None
        ignore=False
        blockOfNormalLines=[]
        i=self.i-1
        #=======================================================================
        # print "========"
        # for line in self.lines:
        #     print line
        # print "========"
        #=======================================================================
        if abs(i)>len(self.lines):
            print "OH"
        while abs(i)<=len(self.lines):
            line=self.lines[i]
            if self.should_ignore_and_ingore_following(line):
                ignore=True
                #===========================================================
                # rfx_free (ptr=0x81c3900) at mem.c:10
                # 10    {
                # 11      if(!ptr)
                # 13      free(ptr);
                # __GI___libc_free (mem=0x81c3900) at malloc.c:2912
                # 2912    malloc.c: No such file or directory.
                # 2917    in malloc.c
                # ...
                # 2946    in malloc.c
                # _int_free (av=0xb7fa7420 <main_arena>, p=0x81c38f8, have_lock=0) at malloc.c:3814
                # 3814    in malloc.c
                # ...
                # 3827    in malloc.c
                # rfx_free (ptr=0x81c3900) at mem.c:14   <---------this line should also be removed
                # 14    }
                #===========================================================
                i-=1
                continue
            
            #if self.hexHeadPattern.match(line):
                #return True
            if ignore:
                #if headInfoPattern.match(line):
                if  ('a'<=line[0] and line[0]<='z') or ('A'<=line[0] and line[0]<'Z') or line[0]=='_':
                    if not self.singleStepPattern.match(line):
                        ignore=False
                
                if '0x'==line[0:2]:#hex head line (optimization)
                    if self.singleStepPattern.match(self.lines[i+1]):
                        ignore=False
                i-=1
                continue
            
            if re.search(r"^[0-9][1-9]*$",line.strip()):#null line
                i-=1
                continue
            
            if self.isNormalLine(line):#normal line
                blockOfNormalLines.append(line)
                #LOG INFO
                print "find normal line:",line
                if "785" in line:
                    print "HEY!"
                    print self.lines[0]
            else:#func info line
                #if headInfoPattern.match(line):
                if  ('a'<=line[0] and line[0]<='z') or ('A'<=line[0] and line[0]<'Z') or line[0]=='_':
                    if i-1<len(self.lines):#look ahead
                        if  abs(i)!=len(self.lines) and self.should_ignore_and_ingore_following(self.lines[i-1]):
                            #===========================================================
                            # 3827    in malloc.c
                            # rfx_free (ptr=0x81c3900) at mem.c:14   <---------this line should also be removed
                            # 14    }
                            #===========================================================
                            ignore=True
                            i-=1
                            continue
                        else:
                            ignore=False
                            funcInfoStr=line.strip()+funcInfoStr
                            print funcInfoStr
                            funcInfo=FunctionCallInfo(funcInfoStr)
                            self.l[0:0]=[LineOfCode(aline,funcInfo) for aline in blockOfNormalLines[::-1]]
                            self.l.insert(0, funcInfo)
                            if abs(i)==len(self.lines):
                                break
                            blockOfNormalLines=[]
                            if firstMeetFuncInfo is None or funcInfo.get_func_name()==firstMeetFuncInfo.get_func_name():
                                if self.isNormalLine(self.lines[i-1]):
                                    callsite=LineOfCode(self.lines[i-1], None)
                                    print callsite
                                    funcname=funcInfo.get_func_name().split("::")[-1]
                                    if self.isObviousCallSite(funcname, callsite.codestr):    
#===============================================================================
# positive example
#===============================================================================
# 515            if (jobs & FEDTJ_CALLBACK)
# 516            callback(self, buf, advance, num, fid, fontsize, x, y, &color);<--------------callsite
# textcallback (self=0xbfffe6a8, glyphs=0xbfffde40, advance=0xbfffe240, nr=15, fontid=5, fontsize=960, startx=0, starty=1053, color=0xbfffde14) at swfstrings.c:115
# 115        SWFFONT*font = 0;
#===============================================================================
# negative example
#===============================================================================
# 43                            return mFirst = mLast = new ListItem<T>( data, NULL, user_data );<--------------not callsite
# SWF::Header::parse (this=0x83c7ab0, r=0x83c7a98, end=32780, ctx=0xbfffe724)
#     at gSWFParser.cpp:423
# 423                    if( r->getPosition() < myend || (r->getPosition()==myend && r->getBits() ))
#===============================================================================
                                        break
                                    else:
                                        filename=self.fetch_callsite_filename(i-1)
                                        if self.isMacroCall(callsite,filename,line):
                                            break
                                if firstMeetFuncInfo is None:
                                    firstMeetFuncInfo=funcInfo
                    elif 'main' in line:
                        funcInfoStr=line.strip()+funcInfoStr
                        funcInfo=FunctionCallInfo(funcInfoStr)
                        ns=[LineOfCode(aline,funcInfo) for aline in blockOfNormalLines[::-1]]
                        #ns = self.fixBlock(ns)
                        self.l[0:0]=ns
                        self.l.insert(0, funcInfo)
                        blockOfNormalLines=[]
                    else:
                        print 1/0#ERROR IMPOSSIBLE
                    
                    funcInfoStr=''
                    #LOG INFO
                    print "find head info line:",line
                else:
                    #Tail function call stack info 
                    funcInfoStr=line.strip()+funcInfoStr
                    #LOG INFO
                    print "find tail info line:",line
                    if "_ctx=_ctx@entry=0xbfffe724, filesize=filesize@entry=505) at SWFFile.cpp:34" in line:
                        print "HEY!"
            i-=1
        self.i=i
        return self.l
    def isObviousCallSite(self,funcname,codedtr):
        m=re.search("(?<![A-Za-z_0-9])([A_Za-z_][A-Za-z_0-9]*)\s*\(", codedtr)
        if m:
            callsite_name=m.group(1)
            if len(funcname)<=3:
                if funcname in callsite_name or callsite_name in funcname:
                    return True
            else:
                s1=[funcname[i:i+3] for i in range(0,len(funcname)-2)]
                s2=[callsite_name[i:i+3] for i in range(0,len(callsite_name)-2)]
                if float(len(set(s1)&set(s2)))/float(len(set(s1)|set(s2)))>0.5:
                    return True
                
        return False             
                    
                   
    def fetch_callsite_filename(self,index):
        i=index
        while self.isNormalLine(self.lines[i]):
            i-=1;
        filename=self.lines[i].split(" at ")[-1].split(":")[0].strip()
        return filename
    
    def isMacroCall(self,callsite,filename,callinfo):
        if self.macro_inspector is None:
            return False
        if self.macro_inspector.project_dir is None:
            return False
        for m in re.finditer(Syntax.lt+Syntax.identifier+Syntax.water+r"\(",callsite.codestr):
            funcname=m.group().rstrip("(").strip()
            if Syntax.isKeyWord(funcname):
                continue
            #Note that the second argument of getExpanded is the line_num of the call site code.
            #So should be callsite_index+1
            #filename=callsite.get_func_call_info().get_file_name()
            linenum=callsite.get_linenum()
            expanded_str=self.macro_inspector.getExpanded(filename,linenum)
            if expanded_str is None:
                return False
            call_patttern=Syntax.lt+Syntax.identifier+Syntax.water+r"[\)\]]*"+Syntax.water+r"\("
            for m in re.finditer(call_patttern,expanded_str):
                if ']' in m.group():
                    return True
                cleaner=''.join(m.group().split())
                clean=cleaner.rstrip('(').rstrip(')')
                if not Syntax.isKeyWord(clean) and not Syntax.isLibFuncName(m.group(1)):
                    return True
        return False    
    def write2File(self, filepath="trace.txt"):
        tra=file(filepath,"w")
        result=""
        for aline in self.l:
            result+=str(aline).rstrip()+"\n"
        tra.write(result)
        tra.close() 
       
   