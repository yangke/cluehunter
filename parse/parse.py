import re
from FunctionCallInfo import FunctionCallInfo
from LineOfCode import LineOfCode
from RedundancyFixer import RedundancyFixer 
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
        errorInfo=[]
        meetBreakPoint = True
        ignore=False
        ignoreNext=False
        blockOfNormalLines=[]
        for line in lines:
            if 'rand () at rand.c:26' in line:
                print "HEY"
            if valueReturnLinePattern.match(line):
                ignore=False
                continue
            if ignore:
                continue
            if ignoreNext:
                if normalLinePattern.match(line):
                    ignoreNext=False
                else:
                    continue
            if hexHeadPattern.match(line):
                ignoreNext=True
                continue
            if nullLinePattern.match(line):
                nullLineNum+=1
            elif nullLineNum == 1:
                #trace content
                if normalLinePattern.match(line):
                    if isFuncInfo:
                        isFuncInfo = False
                        funcInfo=FunctionCallInfo(funcInfoStr)
                        l.append(funcInfo)
                        funcInfoStr=''
                    blockOfNormalLines.append(LineOfCode(line,funcInfo))
                    print "find normal line:",line
                else:
                    if headInfoPattern.match(line):
                        if lines.index(line)+1<len(lines):
                            if re.search(no_such_file_or_directory,lines[lines.index(line)+1]):
                                ignore=True
                                continue
                        listOfLines = fixBlock(blockOfNormalLines)
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
                        print "find head info line:",line
                    else:
                        #Tail function call stack info 
                        funcInfoStr+=line.strip()
                        print "find tail info line:",line
            elif nullLineNum == 2:
                #Error info
                listOfLines = fixBlock(blockOfNormalLines)
                l.extend(listOfLines)
                blockOfNormalLines=[]
                errorInfo.append(line)
        print 'ALL PARSED\n============================================'
        fixer=RedundancyFixer(l,self.redundant_level)
        l=fixer.fix()
        write2File("trace.txt", l)
        return l
    
def write2File(filepath,l):
    tra=file(filepath,"w")
    result=""
    for aline in l:
        print str(aline).rstrip()
        result+=str(aline).rstrip()+"\n"
    tra.write(result)
    tra.close()      
if __name__ =="__main__":
    parser=LogParser()
    parser.parse("../gdb.txt")