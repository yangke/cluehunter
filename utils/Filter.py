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
        types="struct|sizeof|char|int|unsigned|long|short|float|double|register|size_t|u_int"
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
        # Handle the following condition
        # e="(struct areltdata *) ((*((abfd)->xvec->_bfd_read_ar_hdr_fn)) (abfd));"
        #=======================================================================
        clean = Filter.removeStrings(e)
        cleaner = Filter.removeTypes(clean)
        cleanest=cleaner.replace("->", "@")
        segs1=re.split(r"(?<=[_A-Za-z0-9])\s+(?=[_A-Za-z0-9])",cleanest)#To avoid the case:'int a'-->'inta'
        segs2=set()
        for seg in segs1:
            # side effects: all white space '\s' character are removed now
            sgs=re.split(r"(?<=[_A-Za-z0-9\)])\*(?!\))",''.join(seg.split()))# split by the multiply operator
            segs2|=set(sgs)
        segs3=set()
        for seg in segs2:
            sgs=re.split(r"&&",seg)#split by && and ||  and |
            segs3|=set(sgs)
        segs4=set()
        for seg in segs3:
            #split by '&' e.g.:
            # '...a[x])&(...'
            # '...a[0]&_b...'
            # FIX ME :'type & a...' => 'type&a...' => 'type' and 'a...'  ##reference is ignored here 
            sgs=re.split(r"(?<=[_A-Za-z0-9\)\]])&(?=[\(_A-Za-z0-9])",seg)
            segs4|=set(sgs)
        segs5=set()
        for seg in segs4:
            sgs=re.split(r"[^A-Za-z0-9_&\.@\*]",seg)#split by brackets or other  operators
            ss=set()
            for s in sgs:
                print s
                if len(s) >0 and "@" == s[0]:
                    j=seg.index(")@")
                    i=j
                    stack=[")"]
                    while stack!=[] and i >0:
                        i-=1
                        if seg[i]=="(":
                            stack.pop()
                        elif seg[i]==")":
                            stack.append(")")
                    # (struct areltdata *) ((*((abfd)->xvec->_bfd_read_ar_hdr_fn)) (abfd));
                    #
                    # (struct areltdata *) ((*((abfd)@xvec@bfd_read_ar_hdr_fn)) (abfd));
                    #                                @xvec@bfd_read_ar_hdr_fn
                    #                              j^
                    #                          (abfd)@xvec@bfd_read_ar_hdr_fn
                    #                         i^   j^
                    symbol= seg[i:j+1]+s #     (abfd)@xvec@bfd_read_ar_hdr_fn
                    j+=2
                    #                          (abfd)@xvec@bfd_read_ar_hdr_fn
                    #                         i^     j^
                    while j<len(seg) and re.search(r'[_A-Za-z0-9@\.]', seg[j]):
                        j+=1
                    #                          (abfd)@xvec@bfd_read_ar_hdr_fn)
                    #                         i^                            j^
                    interval=(i,j)#set as default not to extend it.
                    if j< len(seg):
                        bracket_count = 0
                        while i>0:
                            i-=1
                            if seg[i] == "(":
                                bracket_count+=1
                                if seg[j]==")":
                                    j+=1
                                    interval=(i,j)
                                    if j==len(seg):
                                        break
                        #                          ((abfd)@xvec@bfd_read_ar_hdr_fn))
                        #                         i^                               j^   
                                else:
                                    break
                        #                          ((abfd)@xvec@bfd_read_ar_hdr_fn)*
                        #                         i^                              j^ 
                            elif  seg[i] == "*":
                                if i-1<0:
                                    interval=(i,j)
                        #                        #*((abfd)@xvec@bfd_read_ar_hdr_fn))
                        #                        )*((abfd)@xvec@bfd_read_ar_hdr_fn))
                        #                       #i^                               j^
                                elif not re.search( r'[^_A-Za-z0-9\)]',seg[i-1]):
                                    if seg[i-1]=="(":
                                        if seg[j]==")":
                                            i-=1
                                            j+=1
                                            interval=(i,j)
                                            if j==len(seg):
                                                break
                        #                        (*((abfd)@xvec@bfd_read_ar_hdr_fn))
                        #                       i^                                j^
                                        else:
                                            break
                                    else:
                                        break
                            elif re.search( r'[^\s]',seg[i]):
                                break
                    
                    
                    symbol= seg[interval[0]:interval[1]]
                    ss.add(symbol)
                            
                elif s!="" and s[-1]!="*":
                    ss.add(s)            
            segs5|=set(ss)
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
    def removeTypes(e):
        array=re.split(r"(?<![_A-Za-z])\([_A-Za-z][_A-Za-z0-9]*[\s\*]*\)(?=\(*[_A-Za-z0-9])",e)
        return ''.join(array)
    
    @staticmethod 
    def expression2vars(e):
        #"(struct areltdata *) ((*((abfd)->xvec->_bfd_read_ar_hdr_fn)) (abfd))"
        # param:abfd
        # function pointer:  ((*((abfd)->xvec->_bfd_read_ar_hdr_fn))
        
        if "(struct areltdata *) ((*((abfd)->xvec->_bfd_read_ar_hdr_fn)) (abfd))" in e:
            print "yes"
        identifiers=Filter.expression2symbols(e)
        identifiers=Filter.removeKeywords(identifiers)
        variables=Filter.filterLibFunc(Filter.filterConstants(identifiers))
        print "Variables in Expression:", variables
        return variables
    @staticmethod
    def isFuncName(symbol,linestr):
        symbol_pattern=re.sub('(?P<specialchar>[\.\*\-\(\)])', lambda matched: '\\'+matched.group('specialchar'), symbol.strip())
        if re.search(r"(?<![_A-Za-z0-9])"+symbol_pattern+r"\s*\(",linestr):
            return True
        return False
    @staticmethod
    def filterOutFuncNames(symbols,linestr):
        return [symbol for symbol in symbols if not Filter.isFuncName(symbol,linestr)]