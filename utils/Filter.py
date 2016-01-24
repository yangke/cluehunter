'''
Created on Sep 23, 2015

@author: yangke
'''
import re
class Filter:
    @staticmethod
    def filterLibFunc(symbols):
        file_input="fgetc|fgets|fread|fscanf|stat"
        file_output="fwrite|fprintf"
        open_close="fopen|fclose"
        cursor_move="lseek|fseek"
        str_op="strerror|strdup|strcspn|strtod|strtol|strupr|strtok|strstr|strrchr|strchr|strcpy|strncpy|strcat|strncat|strcmp|strncmp|strnicmp|sprintf|sscanf"
        syscall="read|write"
        memory="free|alloca|realloc|malloc|calloc|memset|memcpy|memmove|memcmp"
        pattern="|".join([file_input,file_output,open_close,cursor_move,str_op,syscall,memory])
        pattern=r"(^|[^A_Za-z0-9_])("+pattern+r")($|[^A_Za-z0-9_])"
        p=re.compile(pattern)
        return [symbol for symbol in symbols if not p.match(symbol)]
    
    @staticmethod
    def filterConstants(symbols):
        result=set()
        for symbol in symbols:
            if not Filter.isConstants(symbol.strip()):
                result.add(symbol)
        return result
    @staticmethod
    def isConstants(symbol):
        num_pattern=re.compile(r"(^-?[1-9]\d*$)|(^-?([1-9]\d*\.\d*|0\.\d*[1-9]\d*|0?\.0+|0)$)")
        constant_pattern=re.compile(r"[A-Z_]+")
        if num_pattern.match(symbol.strip()) or constant_pattern.match(symbol.strip()):
            return True
        elif symbol.strip()=="sizeof":
            return True
        return False
    @staticmethod
    def removeKeywords(symbols):
        return [symbol for symbol in symbols if not Filter.isKeywords(symbol)]
    @staticmethod
    def isKeywords(symbol):
        types="sizeof|char|int|unsigned|long|short|float|double|register|size_t|u_int"
        statements="for|while|if|else|switch|goto"
        pattern="|".join([types,statements])
        p=re.compile(r"^("+pattern+r")$")
        if p.match(symbol):
            return True
        return False
    @staticmethod
    def expression2symbols(e):
        #=======================================================================
        # if "SIZE" in e:
        #     print "OH NO!"
        #     print 1/0
        #=======================================================================
        clean = Filter.removeStrings(e)
        cleaner = "".join(clean.split())
        cleanest=cleaner.replace("->", "@")
        segs1=re.split(r"(?<=[_A-Za-z0-9])\s+(?=[_A-Za-z0-9])",cleanest)#To avoid the case:'int a'-->'inta'
        segs2=set()
        for seg in segs1:
            sgs=re.split(r"(?<=[_A-Za-z0-9\)])\*",''.join(seg.split()))#split by the multiply operator 
            segs2|=set(sgs)
        segs3=set()
        for seg in segs2:
            sgs=re.split(r"&&",seg)#split by brackets or other  operators
            segs3|=set(sgs)
        segs4=set()
        for seg in segs3:
            sgs=re.split(r"(?<=[_A-Za-z0-9])&(?=[_A-Za-z0-9])",seg)#split by brackets or other  operators
            segs4|=set(sgs)
        segs5=set()
        for seg in segs4:
            sgs=re.split(r"[^A-Za-z0-9_&\.@\*]",seg)#split by brackets or other  operators
            segs5|=set(sgs)
        words=segs5-set([''])
        #words=set(re.split(r"[^A-Za-z0-9_\.@]",cleanest))-set([''])
        symbols=[w.replace("@","->") for w in words]
        return symbols
    @staticmethod
    def removeStrings(e):
        i=0
        result=""
        in_string = False
        while i<len(e):
            if e[i]=='"':
                in_string = not in_string
            elif in_string==False:
                result+=e[i]
            i+=1
        return result
    @staticmethod
    def expression2vars(e):
        identifiers=Filter.expression2symbols(e)
        identifiers=Filter.removeKeywords(identifiers)
        variables=Filter.filterLibFunc(Filter.filterConstants(identifiers))
        print variables
        return variables
    @staticmethod
    def isFuncName(symbol,linestr):
        if re.search(r"(?<![_A-Za-z0-9])"+symbol.strip()+r"\s*\(",linestr):
            return True
        return False
    @staticmethod
    def filterOutFuncNames(symbols,linestr):
        return [symbol for symbol in symbols if not Filter.isFuncName(symbol,linestr)]