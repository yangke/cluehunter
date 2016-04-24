import re
from FunctionCallInfo import FunctionCallInfo
from LineOfCode import LineOfCode
from RedundancyFixer import RedundancyFixer
import datetime
def fixBlock(blockOfNormalLines):
    if blockOfNormalLines==[]:
        return []
    linenum = blockOfNormalLines[-1].get_linenum()
    lines=sorted(list(set(blockOfNormalLines)),key=lambda line:line.get_linenum(),reverse=False)
    return [ x for x in lines if x.get_linenum()<=linenum]   

class LogParser:
    def __init__(self):
        self.redundant_level=RedundancyFixer.REMOVE_INTERPROCEDURAL_REDUNDANT
        
    def setRedundantLevel(self,redundant_level):
        if redundant_level==RedundancyFixer.REMOVE_INLINE_REDUNDANT or redundant_level==RedundancyFixer.REMOVE_INTERPROCEDURAL_REDUNDANT:
            self.redundant_level=redundant_level

    def parse(self,log_file_path='../gdb.txt'):
        now0 = datetime.datetime.now()
        logFile=file(log_file_path, 'r')
        lines = logFile.readlines()
        normalLinePattern = re.compile(r'^[0-9]+\s+.*\n')
        headInfoPattern = re.compile(r'^[A-Za-z_][A-Za-z0-9_]+.*\n')
        nullLinePattern = re.compile(r'^\s*\n')
        valueReturnLinePattern=re.compile(r'^(Value returned is |Run till exit from ).*')
        no_such_file_or_directory=r'No such file or directory.'
        hexHeadPattern=re.compile(r'^0x[0-9a-f]+ in .*$')
        #singleStepPattern=re.compile(r'^Single stepping until exit from function .*$')
        
        nullLineNum = 0
        l = []
        isFuncInfo=True
        funcInfoStr=''
        funcInfo = None
        #errorInfo=[]
        meetBreakPoint = True
        ignore=False
        ignoreNext=False
        last_ignore=False
        blockOfNormalLines=[]
        for line in lines:
            if line[0]=='V' or line[0]=='R':
                if line[0:3]=='Val' or line[0:3]=='Run':
                    if valueReturnLinePattern.match(line):
                        ignore=False
                        continue
            if ignore:
                #if headInfoPattern.match(line):
                if  ('a'<=line[0] and line[0]<='z') or ('A'<=line[0] and line[0]<'Z') or line[0]=='_':
                    ignore=False
                    last_ignore=True #the this line should  also be removed as 
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
                else:
                    continue
            if ignoreNext:
                #if normalLinePattern.match(line):
                if re.search(r'[1-9][0-9]',line[0:2]) or re.search(r'[1-9]\s',line[0:2]) :#normal line
                    ignoreNext=False
                else:
                    continue
            #if hexHeadPattern.match(line):
            if '0x'==line[0:2]:#hex head line
                ignoreNext=True
                continue
            #if nullLinePattern.match(line):
            if line.strip()=='':#null line
                nullLineNum+=1
            elif nullLineNum == 1:
                #trace content
                #if normalLinePattern.match(line):
                if re.search(r'[1-9][0-9]',line[0:2]) or re.search(r'[1-9]\s',line[0:2]) :#normal line
                    if isFuncInfo:
                        isFuncInfo = False
                        funcInfo=FunctionCallInfo(funcInfoStr)
                        l.append(funcInfo)
                        funcInfoStr=''
                    blockOfNormalLines.append(LineOfCode(line,funcInfo))
                    #LOG INFO
                    print "find normal line:",line
                else:
                    #if headInfoPattern.match(line):
                    if  ('a'<=line[0] and line[0]<='z') or ('A'<=line[0] and line[0]<'Z') or line[0]=='_':
                        if lines.index(line)+1<len(lines):
                            if re.search(no_such_file_or_directory,lines[lines.index(line)+1]):
                                ignore=True
                                continue
                            elif last_ignore:
                                last_ignore=False
                                continue  
                        #BUG
                        #listOfLines = fixBlock(blockOfNormalLines)
                        listOfLines = blockOfNormalLines
                        l.extend(listOfLines)
                        blockOfNormalLines=[]
                        if not meetBreakPoint:
                            for aline in listOfLines:
                                aline.set_func_call_info(funcInfo)
                            funcInfo.addLines(listOfLines)
                        #Head function call stack info
                        if meetBreakPoint:
                            line = line.strip('Breakpoint 1, ')
                            meetBreakPoint=False
                        funcInfoStr = line.strip('\n')
                        isFuncInfo=True
                        #LOG INFO
                        print "find head info line:",line
                    else:
                        #Tail function call stack info 
                        funcInfoStr+=line.strip()
                        #LOG INFO
                        print "find tail info line:",line
            elif nullLineNum == 2:
                #Error info
                #FIXME
                #listOfLines = fixBlock(blockOfNormalLines)
                listOfLines = blockOfNormalLines
                l.extend(listOfLines)
                blockOfNormalLines=[]
                #errorInfo.append(line)
        print 'ALL PARSED\n============================================'
        fixer=RedundancyFixer(l,self.redundant_level)
        now1 = datetime.datetime.now()
        print "initial parse time:",now1-now0
        l=fixer.fix()
        now2 = datetime.datetime.now()
        print "filter complains time:",now2-now1
        write2File("trace.txt", l)
        now3 = datetime.datetime.now()
        print "write2File time:",now3-now2
        return l
def write2File(filepath,l):
    tra=file(filepath,"w")
    result=""
    for aline in l:
        result+=str(aline).rstrip()+"\n"
    tra.write(result)
    tra.close()      
if __name__ =="__main__":
    parser=LogParser()
    parser.parse("../gdb.txt")