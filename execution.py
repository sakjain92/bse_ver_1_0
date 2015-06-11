import common
import stp
import parse
import copy
import re
from common import log

class Basic_variable:
    name=None
    typ=None
    addr=None
    sval=None
    def __init__(self,name,typ,addr)

class Var_type:
    ispointer=None
    isarray=None
    array_dim=None
    pointer_dim=None
    typ=None
    pointer_type=None
    array_typ=None
    size=None
    element_list=[]
    array_size=None
    def __init__(self):
        self.ispointer=None
        self.isarray=None   
        self.array_dim=None
        self.pointer_dim=None
        self.typ=None
        self.pointer_typ=None
        self.array_typ=None
        self.size=None
        self.array_size=None
        self.element_list=None #Needs to be links



def backward_execution(glb_lines,start_line,glb_func,glb_types):
    return
    #Main backward execution    
    current_path=path(start_line)
    current_path.function=find_current_function(start_line,glb_func)
    current_path_list=[] 
    current_path_list.append(current_path)

    log.debug("Starting Execution-Start line:"+str(start_line))
    log.debug("Start Function:"+str(current_path.function.name))
    successful_path_list=[]
    
    while (len(current_path_list)!=0):
        temp_path_list=""
        for temp_path in current_path_list:
            temp_path_list=temp_path_list+" "+(str(temp_path.lineno))
        log.debug("Current Path Buffer:"+temp_path_list)
        next_path_list=[]
        for i in range(0,len(current_path_list)):
            current_path=current_path_list.pop()
            log.debug("Current Path"+str(current_path.lineno))
            list_next_path=execute_line(current_path,glb_lines,glb_func)
            temp_path_list=""
            for j in range(0,len(list_next_path)):
                temp_path_list=temp_path_list+" "+str(list_next_path[j].lineno)
                if(list_next_path[j].stop==0):
                    next_path_list.append(list_next_path[j])
                elif(list_next_path[j].end_reached==0):
                    impossible_path_list.append(list_next_path[j])
                    log.debug("Impossible Path"+str(list_next_path[j].flow))
                    log.debug("Path alias:")
                    for temp_alias in list_next_path[j].path_var_alias_assign:
                        log.debug(str(list_next_path[j].path_var_alias_assign[temp_alias].__dict__))
                    log.debug("Path constraints are:")
                    for constraint in list_next_path[j].path_constraint:
                        if(constraint.elements==3):
                            log.debug("Contraint:"+str(constraint.typ)+"LHS is:"+str(constraint.lhs.name)+"RHS is:"+str(constraint.rhs.name)+ "RHS1 is:"+str(constraint.rhs1.name))
                        elif(constraint.elements==2):
                            log.debug("Contraint:"+str(constraint.typ)+"LHS is:"+str(constraint.lhs.name)+"RHS is:"+str(constraint.rhs.name))
                        else:
                            log.error("Unsupported no. of elements in constraint="+str(constraint.elements))

                else:
                    successful_path_list.append(list_next_path[j])
                    log.debug("Successful Path"+str(list_next_path[j].flow))

            log.debug("Return Path List:"+str(temp_path_list))
        current_path_list=next_path_list

