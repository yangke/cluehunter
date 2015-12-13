import re
from FunctionCallInfo import FunctionCallInfo
from LineOfCode import LineOfCode
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
        l=fix_redundancy(l)
        l=filter_complains(l)
        write2File("trace.txt", l)
        return l
def filter_complains(l):
    new=[]
    complains_pattern=r"^[0-9]+\s*in .*\.[c,S]$"
    pat=re.compile(complains_pattern)
    for line in l:
        s=str(line)
        if not isinstance(line, FunctionCallInfo):
            if pat.match(s) or "No such file or directory." in s:
                if len(new)>0 and isinstance(new[-1], FunctionCallInfo):
                    new=new[:-1]
            else:
                new.append(line)
        else:
            new.append(line)   
    return new   
def fix_redundancy(l):
    new_list=[]
    i=0
    while i< len(l):
        if isinstance(l[i], FunctionCallInfo):
            j=check_I(i,l)
            while j>i:
                #print "Caught IT!",l[i]
                i=j
                j=check_I(i,l)
        #print "add:",i
        new_list.append(l[i]) 
        i+=1
    return new_list       
def check_I(i,l):
    m=1
    #print "--------------"
    #print i
    while i+m<len(l) and str(l[i])!=str(l[i+m]):
        m+=1
    #print i+m
    if i+m==len(l):
        return 0
    else:
        for j in range(0,m):
            if str(l[i+j])!=str(l[i+m+j]):
                return i
        return i+m    
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