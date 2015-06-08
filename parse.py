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
glb_temp_types={}


class Branch:
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

class Function:
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
    if(len(sys.argv)!=3):#Script+InputName+Lineno
        log.error("Command args number:"+str(len(sys.argv)))
        sys.exit("Improper arguments")
    else:
        #Return input_file_name , Lineno
        return [sys.argv[1],int(sys.argv[2])]
    return

def close_file(fb):
    fb.close()


def get_pointer_dim(word):
    #Return how many *'s in the end of string (pointer_dim) an remaining string (rest)
    #Check no space in word
    grp=re.match("(.*?)(\*+)$",word)
    try:
        pointer_dim=len(grp.group(2))
        rest=grp.group(1)
    except:
        pointer_dim=None
        rest=word
    return [rest,pointer_dim]

def get_var_type(typ):
    global glb_types
    #Not arrays.Return new copy of Var_type
    [rest_typ,pointer_dim]=get_pointer_dim(typ)
    temp_type=execution.Var_type()
 
    if rest_typ in glb_typ:
        temp_glb_typ=glb_typ[rest_typ]
        temp_typ.size=temp_glb_typ.size
        temp_typ.element_list=temp_glb_typ.element_list
        temp_typ.typ=temp_glb_typ.typ
    else:
        grp=re.match("i([\d]+)",typ)
        if(not(grp==None)):
            temp_type.typ="integer"
            temp_type.size=int(grp.group(1))
        else:
            log.error("Unknown typ:"+str(typ))
            #Could be that that typ has not been defined yet but is being used
            #Don't support it.Need to add code here for that.
            #Use glb_temp_types when need to add support for this.

    if(not(pointer_dim==None)):
        temp_type.ispointer=1
        temp_type.pointer_dim=pointer_dim
        temp_type.size=32
        temp_type.pointer_typ=temp_typ.typ
        temp_type.typ="pointer"
    
    return temp_type    

def parse_array(word):
    #Identifies if word is array.If yes, send the list containing dimension and array type.
    #Not considering pointers to array here. Ending '*' are 'don't care'
    #Assumption:Type name doesn't start with number
    digit=""
    typ=None
    array_dim=[]
    previous_char=None
    for char in word:
        if((re.match("\d",char)and(typ==None):
            digit=digit+char
        elif(char=="["):
            array_dim.append(int(digit))
        elif(char=="]"):
            break
        elif(not(re.match("\s",char)):
            if((re.match("\s",previous_char)): #New word begins    
                typ=char
            else:
                typ=typ+char
        previous_char=char
    
    temp_array_type=get_var_type(typ)
    temp_type=execution.Var_type();

    if(not(array_dim==[])): #shouldn't need to check
        temp_type.isarray=1
        temp_type.array_dim=array_dim
        prod=temp_array_type.size
        if(temp_array_type.size<=0):
            log.error("Array Type Size <=0:",word)
        for dim in array_dim:
           prod=prod*dim

        temp_type.size=prod
        temp_type.array_size=prod
        temp_type.typ="array"
        temp_type.array_type=temp_array_typ.typ
        temp_type.element_list=temp_array_typ.element_list
    else:
        log.error("Array without dimension:"+str(word))

    return temp_type

def parse_type(word):
   [rest,pointer_dim]=get_pointer_dim(word)
                    
    if '[' in word:
        [rest,pointer_dim]=get_pointer_dim(word)
        temp_type=parse_array(rest)
        if(pointer_dim>1): #None<1
            log.error("With array, one that 1 pointer_dim:"+str(old_word))
        if(not(pointer_dim==None)):
            temp_type.ispointer=1;
            temp_type.pointer_dim=pointer_dem
            temp_type.size=32

    else:
        temp_type=get_var_type(word)
    
    return temp_type
         
def parse_desc(old_desc,old_word):
    #Clean up desc. Currently supports:
    #1) Converting *_typ into execution.basic_type
    if(re.match("^.*_typ$",old_desc)):
        temp_type=parse_type(old_word) 
        new_word=temp_type
        new_desc=old_desc

    return [new_desc,new_word]

def parse_line(line):
    #Parse a line.Format of line is <desc>:<word>;<line>:<word>..... Currently white-spaces not allowed.
    #Words and descriptors can't have ';' or ':'
    #Currently can't have two same keywords(desc) in same line
    cur_is_word=0
    line_desc={}
    word=""
    desc=""
    for i in range(0,len(line)):
        char=line[i]
        if(re.match("\s",char)):
            #if(not(char=="\n")):
            #    log.warn("Found white-space in line:"+str(line))
            #    log.warn("Ignoring this whitespace")   
            continue
        elif(char==":"):
            cur_is_word=1
        elif(char==";"):
            cur_is_word=0
            try:
                line_desc[desc]
            except:
                pass
            else:
                log.error("Desc already exist in line.Line:"+str(line)+" Desc:"+str(desc))
            [desc,word]=parse_desc(desc,word)
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
    #Starting elements are in global
    current_function="|global|"

    log.debug("Starting Parsing")
    log.debug("");log.debug("");log.debug("");
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
        log.debug("");
        
        #All lines must have a instr descriptor 
        instruction=line_desc["instr"]
        if(instruction=="define"):
            func_name=line_desc["func"]
            temp_func=Function(func_name,lineno)
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
                    temp_branch=Branch()
                    temp_branch.jump_point.append(lineno)
                    glb_functions[current_function].branches[br]=temp_branch
        elif(instruction=="type"):
            temp_type=execution.Var_type()
            new_type=line_desc["lhs"]
            if new_type  in glb_types:
                log.error("Type already in glb_types:"+str(new_type));
            glb_types[new_type]=temp_type
            temp_type.typ="structure"
            temp_rhs=parse_type(line_desc["rhs_typ"])
            temp_type.size=temp_rhs.size
            temp_type.element_list=[temp_rhs]
            i=0
            while True:
                i=i+1
                desc_string=str("rhs"+str(i)+"_typ") 
                if desc_string in line_desc:
                    temp_rhs=parse_type(line_desc[desc_string])
                    temp_type.size=temp_type.size+temp_rhs.size
                    temp_type.element_list.append(temp_rhs)
                else:
                    break
            
        
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
    
    log.debug("Glb Types-")
    for glb_var_type in glb_types:
        log.debug("Type name:"+glb_var_type)
        log.debug("Type size:"+str(glb_types[glb_var_type].size))
        log.debug("Type type:"+str(glb_types[glb_var_type].typ))


def init_glb():
    global glb_types
    global glb_functions

    float_type=execution.Var_type();
    float_type.typ="float"
    float_type.size=64 #32 or 64?
    
    double_type=execution.Var_type();
    double_type.typ="double"
    double_type.size=64
    
    glb_types["float"]=float_type
    glb_types["double"]=double_type

    temp_func=Function("|global|",-1)
    glb_functions["|global|"]=temp_func

                            
def main():
    #Call like this: python parse.py <filepath/filename> <lineno_to _start_from>
    common.log_setup()
    [infile,start_line]=cmd_args_parse()
    ifb=open_input_file(infile)
    init_glb();
    parse_file(ifb)
    execution.backward_execution(glb_lines,start_line,glb_functions,glb_types)
    close_file(ifb)
    common.log_close()

if __name__ == "__main__":
    main()
