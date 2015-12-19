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
    
    def parse(self,log_file_path='../gdb.txt'):
        logFile=file(log_file_path, 'r')
        lines = logFile.readlines()
        normalLinePattern = re.compile(r'^[1-9][0-9]*.*\n')
        headInfoPattern = re.compile(r'^[A-Za-z_][A-Za-z0-9_]+.*\n')
        nullLinePattern = re.compile(r'^\s*\n')
        nullLineNum = 0
        l = []
        isFuncInfo=True
        funcInfoStr=''
        funcInfo = None 
        errorInfo=[]
        meetBreakPoint = True
        blockOfNormalLines=[]
        for line in lines:
            if nullLinePattern.match(line):
                #trace head info
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
                    #print '***'+lineNumStr,codeline
                    #l.append(line)
                    print "find normal line:",line
                else:
                    if headInfoPattern.match(line):
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
        fixer=RedundancyFixer(l,RedundancyFixer.REMOVE_INTERPROCEDURAL_REDUNDANT)
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