#!/usr/bin/python
import sys
import re 
import common
import execution
import copy
from common import log

glb_functions={}
glb_lines={}
glb_types={}

class branch:
    #Class for branch labels
    jump_point=[]
    def __init__(self):
        self.jump_point = []

def get_branch_name(label):
    #To get names of branch which is same as branch label
    #Just remove % appended in starting.I don't think any global branch exist.
    if(label[0]=="%"):
        return label[1:]
    elif(label[0]=="@"):
        log.error("Unexpected @ in label name "+str(label))
        return label[1:]
    else:
        return label

class function:
    name=None
    start=-1
    end=-1
    branches={}#Stored with names after using get_branch_name
    ret_line=[]
    def __init__(self,name,lineno):
        self.branches = {}
        self.start=lineno
        self.end=-1    
        self.name=name
        self.ret_line=[]

def open_input_file(fname):
    try:
        fb=open(str(fname),"r")
    except:
        sys.exit("Cannot open input file for reading");
    return fb
def open_output_file(fname):
    try:
        fb=open(str(fname),"w")
    except:
        sys.exit("Cannot open output file for writing");
    return fb


def cmd_args_parse():
    #Currently script_name secondary_ir lineno
    log.info("Command args:"+str(sys.argv))
    if(len(sys.argv)!=3):#Script+InputName
        log.error("Command args number:"+str(len(sys.argv)))
        sys.exit("Improper arguments")
    else:
        #Return input_file_name
        return [sys.argv[1],int(sys.argv[2])]
    return

def close_file(fb):
    fb.close()

def parse_line(line):
    #Parse a line.Format of line is <desc>:<word>;<line>:<word>..... Currently white-spaces not allowed.
    #Words and descriptors can't have ';' or ':'
    cur_is_word=0
    line_desc={}
    word=""
    desc=""
    for i in range(0,len(line)):
        char=line[i]
        if(re.match("\s",char)):
            if(not(char=="\n")):
                log.error("Found white-space in line:"+str(line))   
            continue
        elif(char==":"):
            cur_is_word=1
        elif(char==";"):
            cur_is_word=0
            line_desc[desc]=word
            word=""
            desc=""
        elif(cur_is_word):
            word=word+char
        else:
            desc=desc+char
    return line_desc

def parse_file(ifb):
    global glb_functions;
    global glb_lines;
    global glb_types;

    lineno=0
    current_function=""

    log.debug("Starting Parsing")
    while True:
        lineno=lineno+1
        line=ifb.readline()#Trailing \n left
        
        
        if(not(line)):#EOF
            break
        if(re.match("^(\s)*$",line)):#Blank line.This needed?
            continue
        else:
            line_desc=parse_line(line)
            glb_lines[lineno]=line_desc;
        
        log.debug("Parsing Line:"+str(lineno))
        log.debug("Line is:"+str(line))
        log.debug("Line description is:"+str(line_desc))
        
        #All lines must have a instr descriptor 
        instruction=line_desc["instr"]
        if(instruction=="define"):
            func_name=line_desc["func"]
            temp_func=function(func_name,lineno)
            glb_functions[func_name]=temp_func
            current_function=func_name #Do I need to make @main as main?
        elif(instruction=="function_end"):
            if(current_function==""):
                log.error("Current function is undefined but function_end called")
            glb_functions[current_function].end=lineno
            current_function=""
        elif(instruction=="ret"):
            if(current_function==""):
                log.error("Current function is undefined but ret called")
            glb_functions[current_function].ret_line.append(lineno)
        elif(instruction=="br"):
            if(current_function==""):
                log.error("Current function is undefined but br called")

            br_list=[]
            br1=get_branch_name(line_desc["label"])
            br_list.append(br1)
            try:
                br2=get_branch_name(line_desc["label1"])
            except:
                pass
            else:
                br_list.append(br2)

            for br in br_list:
                if br in glb_functions[current_function].branches:
                    glb_functions[current_function].branches[br].jump_point.append(lineno)
                else:
                    temp_branch=branch()
                    temp_branch.jump_point.append(lineno)
                    glb_functions[current_function].branches[br]=temp_branch
                
    #Log elements of glb_functions
    log.debug("Glb Functions-") 
    for func in glb_functions:
        log.debug("Function name:"+glb_functions[func].name)
        if(not(func==glb_functions[func].name)):
            log.error("Function name and name in glb_function doesn't match:"+str(func))
        log.debug("Function branches-")
        for br in glb_functions[func].branches: 
            log.debug("Branch:"+str(br)+" Branch points:"+str(glb_functions[func].branches[br].jump_point))     
        log.debug("Function return statement:"+str(glb_functions[func].ret_line))

                            
def main():
    #Call like this: python parse.py <filepath/filename> <lineno_to _start_from>
    common.log_setup()
    [infile,start_line]=cmd_args_parse()
    ifb=open_input_file(infile)
    parse_file(ifb)
    execution.backward_execution(glb_lines,start_line,glb_functions,glb_types)
    close_file(ifb)
    common.log_close()

if __name__ == "__main__":
    main()
