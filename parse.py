#!/usr/bin/python
import sys
import re 
import common
from cStringIO import StringIO
import execution
import copy
import inspect
import logging
import os
import subprocess

LOG_FILENAME = 'log.out'
#logging.basicConfig(filename=LOG_FILENAME,
#                    level=logging.DEBUG,
#                    )
log=logging

def get_lineno():
    return inspect.currentframe().f_back.f_lineno

glb_func={}
glb_lines={}

class branch:
    jump_point=[]
    def __init__(self):
        self.jump_point = []

class function:
    name=None
    start=-1
    end=-1
    branches={}
    ret_line=[]
    def __init__(self):
        self.branches = {}
        self.start=-1
        self.end=-1    
        name=None
        self.ret_line=[]
def open_input_file(fname):
    try:
        fb=open(str(fname),"r")
    except:
        sys.exit("Cannot open input file for reading");
    return fb
def open_output_file(fname):
    try:
        fb=open(str(fname),"r")
    except:
        sys.exit("Cannot open output file for writing");
    return fb


def cmd_args_parse():
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

def parse_file(ifb):
    global glb_func;
    global glb_lines;

    lineno=0
    current_function=""
    log.debug("Starting Parsing") 
    while True:
        log.debug("Parsing Line"+str(lineno+1))
        lineno=lineno+1
        line=ifb.readline()
        log.debug("Line is:"+str(line))
        if(not(line)):
            break
        if(re.match("^(\s)*$",line)):
            continue
        else:
            line_desc=parse_line(line)
            glb_lines[lineno]=line_desc;
            #print line_descfind_current_function

        log.debug("Line description is"+str(line_desc))
        instruction=line_desc["instr"]
        if(instruction=="define"):
            temp_func=function()
            temp_func.start=lineno
            func_name=line_desc["func"]
            temp_func.name=func_name
            glb_func[func_name]=temp_func
            current_function=func_name #Do I need to make @main as main?
        elif(instruction=="function_end"):
            glb_func[current_function].end=lineno
        elif(instruction=="ret"):
            glb_func[current_function].ret_line.append(lineno)
        elif(instruction=="br"):
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
                if br in glb_func[current_function].branches:
                    glb_func[current_function].branches[br].jump_point.append(lineno)
                else:
                    temp_branch=branch()
                    temp_branch.jump_point.append(lineno)
                    glb_func[current_function].branches[br]=temp_branch
                
    #Find elements of glb_funct
    log.debug("Glb Functions-") 
    for func in glb_func:
        log.debug("Function name:"+glb_func[func].name)
        log.debug("Function branches-")
        for br in glb_func[func].branches: 
            log.debug(br+" branch points:"+str(glb_func[func].branches[br].jump_point))     
        log.debug("Function return statement:"+str(glb_func[func].ret_line))
            
def get_branch_name(label):
    if(label[0]=="%"):
        return label[1:]
    else:
        return label
def get_type_size(typ):
    if(re.match("i([\d]*)",typ)):
        grp=re.match("i([\d]*)",typ)
        return int(grp.group(1))
    else:
        log.error("Type not supported"+str(typ))
def convert_pointer_typ(typ):
    #Remove the last *
    if(typ[-1]=="*"):
        return typ[:-1]
    else:
        return typ         
    
def parse_line(line):
    cur_is_word=0
    line_desc={}
    word=""
    desc=""
    for i in range(0,len(line)):
        char=line[i]
        if(char==":"):
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
                

def log_setup():
    i=0
    if 'bse_last' in os.listdir("./"):
        subprocess.call(["rm","-rf","bse_last"])
        while(1):
            if 'bse_out_'+str(i) in os.listdir("./"):
                i=i+1
            else:
                break
    subprocess.call(["mkdir","bse_out_"+str(i)])
    subprocess.call(["ln","-s","bse_out_"+str(i),"bse_last"])
    LOG_PATH = "./"+"bse_last"
    LOG_FILENAME="bse.log"
    logging.basicConfig(filename=LOG_FILENAME,pathname=LOG_PATH,
                    level=logging.DEBUG,
                    )
    logging.info("Starting Log")

def log_close():
    subprocess.call(["mv","bse.log","./bse_last"])
            
def main():
    #Call like this: python parse.py <filepath/filename> <lineno_to _start_from>
    log_setup()
    [infile,start_line]=cmd_args_parse()
    ifb=open_input_file(infile)
    parse_file(ifb)
    execution.execution(glb_lines,start_line,glb_func)
    close_file(ifb)
    log_close()

if __name__ == "__main__":
    main()
