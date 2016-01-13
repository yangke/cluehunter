'''
Created on Sep 9, 2015

@author: yangke
'''
from parse.FunctionCallInfo import FunctionCallInfo
class TaintGraph:
    def __init__(self,l):
        self.inInnerEdges=dict()
        self.outInnerEdges=dict()
        self.inInterEdges=dict()
        self.outInterEdges=dict()
        self.inCrossEdges=dict()
        self.outCrossEdges=dict()
        self.inExpandEdges=dict()
        self.outExpandEdges=dict()
        self.nodes=set()
        self.l=l
        
    def linkInnerEdges(self,startIndex,endIndex,accessstr):
        print "InnerEdge:"+str(self.l[startIndex]).rstrip()+"--->"+str(self.l[endIndex]).rstrip()+":"+accessstr+"\n"
        if startIndex not in self.outInnerEdges:
            self.outInnerEdges[startIndex]=set()
        self.outInnerEdges[startIndex].add((endIndex,accessstr))
        #######################################
        if endIndex not in self.inInnerEdges:
            self.inInnerEdges[endIndex]=set()
        self.inInnerEdges[endIndex].add((startIndex,accessstr))
        self.nodes.add(startIndex)
        self.nodes.add(endIndex)
        
    def linkCrossEdges(self,startIndex,endIndex,accessstr):
        print "CrossEdge:"+str(self.l[startIndex]).rstrip()+"--->"+str(self.l[endIndex]).rstrip()+":"+accessstr+"\n"
        if startIndex not in self.outCrossEdges:
            self.outCrossEdges[startIndex]=set()
        self.outCrossEdges[startIndex].add((endIndex,accessstr))
        #######################################
        if endIndex not in self.inCrossEdges:
            self.inCrossEdges[endIndex]=set()
        self.inCrossEdges[endIndex].add((startIndex,accessstr))
        self.nodes.add(startIndex)
        self.nodes.add(endIndex)
          
    def linkExpandEdges(self,startIndex,endIndex,accessstr):
        print "ExpandEdge:"+str(self.l[startIndex]).rstrip()+"--->"+str(self.l[endIndex]).rstrip()+":"+accessstr+"\n"
        if startIndex not in self.outCrossEdges:
            self.outExpandEdges[startIndex]=set()
        self.outExpandEdges[startIndex].add((endIndex,accessstr))
        if endIndex not in self.inExpandEdges:
            self.inExpandEdges[endIndex]=set()
        self.inExpandEdges[endIndex].add((startIndex,accessstr))
        self.nodes.add(startIndex)
        self.nodes.add(endIndex)
            
    def linkInterEdges(self,startIndex,endIndex,param,arg,argpos):
        print "InterEdge:"+str(self.l[startIndex]).rstrip()+"--->"+str(self.l[endIndex]).rstrip()+":"+str(arg)+","+str(argpos)+"\n"
        if startIndex not in self.outInterEdges:
            self.outInterEdges[startIndex]=set()
        self.outInterEdges[startIndex].add((endIndex, arg, argpos))
        #######################################
        if endIndex not in self.inInterEdges:
            self.inInterEdges[endIndex]=set()
        self.inInterEdges[endIndex].add((startIndex,param, argpos))
        self.nodes.add(startIndex)
        self.nodes.add(endIndex)
        
    def __str__(self):
        result="inner edges:\n"
        for key,value in self.outInnerEdges.items():
            result+=str(self.l[key]).rstrip()+"--->"+str(self.l[value[0]]).rstrip()+":"+str(value[1])+"\n"
        result="cross edges:\n"
        for key,value in self.outCrossEdges.items():
            result+=str(self.l[key]).rstrip()+"--->"+str(self.l[value[0]]).rstrip()+":"+str(value[1])+"\n"
        result="expand edges:\n"
        for key,value in self.outExpandEdges.items():
            result+=str(self.l[key]).rstrip()+"--->"+str(self.l[value[0]]).rstrip()+":"+str(value[1])+"\n"
        result+="inter edges:\n"
        for key,value in self.outInterEdges.items():
            result+=str(self.l[key]).rstrip()+"--->"+str(self.l[value[0]]).rstrip()+":"+str(value[1])+","+str(value[2])+"\n"
        return result
    def serialize2dot(self):
        result="digraph tiantgraph{\n"
        for nodeIndex in self.nodes:
            if isinstance(self.l[nodeIndex], FunctionCallInfo):
                result+="\""+self.linenum2DotStr(nodeIndex)+'\"[shape="record"];\n'
            else:
                result+="\""+self.linenum2DotStr(nodeIndex)+'\";\n'
        result+='edge [fontname = "Verdana", fontsize = 10, color="crimson", style="solid"];\n'
        for key,values in self.outInnerEdges.items():
            for value in values:
                result+="\""+self.linenum2DotStr(key)+"\"->\""+self.linenum2DotStr(value[0])+"\"[label=\""+self.handleDotKeywords(str(value[1]))+"\"];\n"
        for key,values in self.outCrossEdges.items():
            for value in values:
                result+="\""+self.linenum2DotStr(key)+"\"->\""+self.linenum2DotStr(value[0])+"\"[label=\""+self.handleDotKeywords(str(value[1]))+"\","
                result+='style="dashed", color="yellow"];\n'
        for key,values in self.outExpandEdges.items():
            for value in values:
                result+="\""+self.linenum2DotStr(key)+"\"->\""+self.linenum2DotStr(value[0])+"\"[label=\""+self.handleDotKeywords(str(value[1]))+"\","
                result+='style="dashed", color="orange"];\n'
        for key,values in self.outInterEdges.items():
            for value in values:
                result+="\""+self.linenum2DotStr(key)+"\"->\""+self.linenum2DotStr(value[0])+"\"[label=\""+self.handleDotKeywords(str(value[1]))+","+self.handleDotKeywords(str(value[2]))+"\","
                result+='style="dashed", color="forestgreen"];\n'       
        result+="}"
        return result
    
    def handleDotKeywords(self,s):
        s=s.replace(r'"', r'\"')#.replace(r';', r'\;')
        s=s.replace(r'{', r'\{').replace(r'}', r'\}')
        #s=s.replace(r'<', r'\<').replace(r'>', r'\>')
        s=s.replace('\\','\\\\')
        return s
    def linenum2DotStr(self,num):
        return self.handleDotKeywords(str(num)+"#"+str(self.l[num]).rstrip())
class Node:
    def __init__(self,job):
        self.index=job.traceIndex
        self.var=job.var
    def initiate(self,var,index):
        self.index=index
        self.var=var