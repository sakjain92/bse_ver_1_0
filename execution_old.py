import common
import stp
import parse
import copy
import re
from common import log

class constraint:
    typ=None
    lhs=None
    rhs=None
    rhs1=None
    elements=0
    equation=None
    eq=1
    ne=2
    ugt=3
    uge=4
    ult=5
    ule=6
    sgt=7
    sge=8
    slt=9
    sle=10
    add=11#There is no signed/unsigned add.Single Add.
    def __init__(self):
        self.typ=None
        self.lhs=None
        self.rhs=None
        self.rhs1=None
        self.elements=0
        self.equation=None
        

class path_solver:
    s=None
    var=None
    def __init__(self):
        self.s=stp.Solver()
        self.var={}
    def add_var_vec(self,var_name,var_size):
        if(not(var_name in self.var)):
            temp_var=self.s.bitvec(var_name,var_size)
            self.var[var_name]=temp_var
            return temp_var
        else:
            return self.var[var_name]
        
        

glb_path_solver=path_solver()
class alias:
    name=None
    assigned=None
    used=None
    def __init__(self,name,assigned,used):
        self.name=name
        self.assigned=assigned
        self.used=used

class path:
    flow=None
    lineno=0
    function=None
    stop=0
    path_constraint=[]
    path_var_alias_assign={}
    link_reg=[]
    end_reached=0
    label=None
    def __init__(self,lineno):
        self.flow=[lineno]
        self.lineno=lineno
        self.function=None
        self.path_constraint=[]
        self.path_var_alias_assign={}
        self.stop=0
        self.link_reg=[]
        self.label=None
        self.end_reached=0
    def element_is_constant(self,constant_value_str):
        try:
            #Float conversion also takes care of scientific notation
            temp_val=float(constant_value_str)
        except:
            return None
        else:
            #TODO:In case of floating value need to send the floating point eqivalent.Does STP support floating value?--I don't think it does
            return int(temp_val)
    def get_var_name(self,var_name):
        if(var_name[0]=="%"):
            return self.function.name+"--"+var_name
        else:
            return var_name;
 
    def add_element(self,var_name,var_type,assign):
        global glb_path_solver;

        temp_const_val=self.element_is_constant(var_name)
        if(temp_const_val!=None):
            return self.get_constant(temp_const_val,var_type)
        else:
            var_name=self.get_var_name(var_name)
        if(var_name in self.path_var_alias_assign):
            temp_var_assign=self.path_var_alias_assign[var_name]
            temp_var_name=temp_var_assign.name
            
            if(assign==1):
                grp=re.match("(.*)\-([\d]*)$",temp_var_name)
                if(grp):
                    new_var_name=grp.group(1)+"-"+str(int(grp.group(2))+1)
                else:
                    new_var_name=temp_var_name+"-1"
                temp_var_assign.name=new_var_name
                temp_var_assign.assigned=1
                return glb_path_solver.add_var_vec(new_var_name,parse.get_type_size(var_type))
            else:
                temp_var_assign.used=1 
                return glb_path_solver.var[temp_var_name]
                
        else:
            if(assign):
                self.path_var_alias_assign[var_name]=alias(var_name,1,0)
            else:
                self.path_var_alias_assign[var_name]=alias(var_name,0,1)
            return glb_path_solver.add_var_vec(var_name,parse.get_type_size(var_type))

    def add_constraint_element(self,var_name,var_type):
        return self.add_element(var_name,var_type,0) 
    def add_assignment_element(self,var_name,var_type):
        return self.add_element(var_name,var_type,1)
    
    def add_constraint_eq(self,lhs,rhs):
        temp_constraint=self.create_bi_constraint(lhs,rhs,constraint.eq,(lhs.eq(rhs)))
        self.path_constraint.append(temp_constraint)
        return self.ispossible()

    def add_constraint_ne(self,lhs,rhs):
        temp_constraint=self.create_bi_constraint(lhs,rhs,constraint.ne,(lhs.ne(rhs)))
        self.path_constraint.append(temp_constraint)      
        return self.ispossible()

    def add_constraint_ugt(self,lhs,rhs):
        temp_constraint=self.create_bi_constraint(lhs,rhs,constraint.ugt,(lhs.gt(rhs)))
        self.path_constraint.append(temp_constraint)
        return self.ispossible()

    def add_constraint_uge(self,lhs,rhs):
        temp_constraint=self.create_bi_constraint(lhs,rhs,constraint.uge,(lhs.ge(rhs)))
        self.path_constraint.append(temp_constraint)
        return self.ispossible()

    def add_constraint_ult(self,lhs,rhs):
        temp_constraint=self.create_bi_constraint(lhs,rhs,constraint.ult,(lhs.lt(rhs)))
        self.path_constraint.append(temp_constraint)
        return self.ispossible()

    def add_constraint_ule(self,lhs,rhs):
        temp_constraint=self.create_bi_constraint(lhs,rhs,constraint.ule,(lhs.le(rhs)))
        self.path_constraint.append(temp_constraint)
        return self.ispossible()
    
    def add_constraint_sgt(self,lhs,rhs):
        temp_constraint=self.create_bi_constraint(lhs,rhs,constraint.sgt,(lhs.sgt(rhs)))
        self.path_constraint.append(temp_constraint)
        return self.ispossible()

    def add_constraint_sge(self,lhs,rhs):
        temp_constraint=self.create_bi_constraint(lhs,rhs,constraint.sge,(lhs.sge(rhs)))
        self.path_constraint.append(temp_constraint)
        return self.ispossible()

    def add_constraint_slt(self,lhs,rhs):
        temp_constraint=self.create_bi_constraint(lhs,rhs,constraint.slt,(lhs.slt(rhs)))
        self.path_constraint.append(temp_constraint)
        return self.ispossible()
    
    def add_constraint_sle(self,lhs,rhs):
        temp_constraint=self.create_bi_constraint(lhs,rhs,constraint.sle,(lhs.sle(rhs)))
        self.path_constraint.append(temp_constraint)
        return self.ispossible()

    def add_constraint_add(self,lhs,rhs,rhs1):
        temp_constraint=self.create_tri_constraint(lhs,rhs,rhs1,constraint.add,(lhs==(rhs+rhs1)))
        self.path_constraint.append(temp_constraint)
        return self.ispossible()

    
    def create_bi_constraint(self,lhs,rhs,constraint_typ,equation):
        temp_constraint=constraint()
        temp_constraint.lhs=lhs
        temp_constraint.rhs=rhs
        temp_constraint.elements=2
        temp_constraint.typ=constraint_typ
        temp_constraint.equation=(equation)
        return temp_constraint
    
    def create_tri_constraint(self,lhs,rhs,rhs1,constraint_typ,equation):
        temp_constraint=constraint()
        temp_constraint.lhs=lhs
        temp_constraint.rhs=rhs
        temp_constraint.rhs1=rhs1
        temp_constraint.elements=3
        temp_constraint.typ=constraint_typ
        temp_constraint.equation=(equation)
        return temp_constraint
        
    def ispossible(self):
        #Don't use this directly
        #Try to remove any constraint which might always be true/false
        global glb_path_solver
        self.get_path_solver()
        path_possible=glb_path_solver.s.check()
        glb_path_solver.s.pop()
        if(not(path_possible)):
            self.stop=1
        return path_possible

    def get_path_model(self):
        global glb_path_solver
        self.get_path_solver()
        glb_path_solver.s.check()
        model=glb_path_solver.s.model()
        glb_path_solver.s.pop()
        return model
        
    def get_path_solver(self):
        #Pop always after calling this function
        global glb_path_solver
        glb_path_solver.s.push()
        for cnstr in self.path_constraint:
            glb_path_solver.s.add(cnstr.equation)
    
    def make_pseudo_copy(self,next_line):
        next_path=self
        next_path.lineno=next_line
        next_path.flow.append(next_line)
        return next_path
        
    def make_copy(self,next_line):
        next_path=copy.deepcopy(self)
        next_path.lineno=next_line
        next_path.flow.append(next_line)
        return next_path


        
    #def make_constraint_copy(self,constraint):
    #    if(constraint.lhs.name!=None):
    #        lhs=self.path_var[lhs.name]
    #    else:
    #        lhs=constraint.lhs
    #    if(constraint.rhs.name!=None):
    #        rhs=self.path_var[rhs.name]
    #    else:
    #        rhs=constraint.rhs
    #
    #    if(constraint.elements==2):
    #        if(constraint.typ==constraint.eq):
    #            self.add_constraint(lhs==rhs)
    #        elif(constraint.typ==constraint.neq):
    #            self.add_constraint(lhs!=rhs)

    #            
    #def make_copy(self):
    #    
    #    #Issue here.Why?
    #    #Is this issue with python ver of STP
    #    #Can't seem to create two versions of stp.solver in one program
    #    stp.Solver()              
    #    new_path=copy.deepcopy(self)
    #    new_path.path_solver=stp.Solver()
    #    new_path.path_var={}
    #
    #    for var in self.path_var:
    #        var=self.path_var[var]
    #        temp_var=new_path.path_solver.bitvec(var.name,var.width)
    #        new_path.path_var[var.name]=temp_var
    #    for constraint in self.path_constraint:
    #        new_path.add_constraint(next_path.make_constraint_copy(constraint))
    #    return new_path
            
        
        
    def get_constant(self,constant_val,constant_type):
        log.debug("Getting Constant:"+str(constant_val))
        global glb_path_solver;
        #Changing to ease debugging
        #return glb_path_solver.s.bitvecval(parse.get_type_size(constant_type),constant_val)
        temp_constant=glb_path_solver.s.bitvecval(parse.get_type_size(constant_type),constant_val)
        temp_var=self.add_assignment_element(str(constant_type)+str(constant_val),constant_type)
        self.add_constraint_eq(temp_var,temp_constant)
        return temp_var
    
    
def find_current_function(start_line,glb_func):
    for func in glb_func:
        if((start_line>=glb_func[func].start)and(start_line<=glb_func[func].end)):
            return glb_func[func]
    log.error("No Current Function found.Line is:"+str(start_line))
    return None

def execute_line(current_path,glb_lines,glb_func):

    log.debug("Current Line"+str(glb_lines[current_path.lineno]))
    print "Current Line is", current_path.lineno
    #print "Current Flow is",current_path.flow
    list_next_path=[]
    lineno=current_path.lineno
    line_desc=glb_lines[lineno]
    instr=line_desc["instr"]
    if(instr!="br"): #This condition is not needed I suppose
        prev_label=current_path.label=""
    else:
        prev_label=current_path.label

    if(instr=="define"):
        if(len(current_path.link_reg)==0):
            if(current_path.function.name!="@main"):
                log.error("End of Path but current function is not main.It is:"+str(current_path.function))
            current_path.stop=1
            print "Path Possible:",current_path.ispossible()
            print "Path Model is:",current_path.get_path_model()
            print "Path Aliases is:"
            for temp_alias in current_path.path_var_alias_assign:
                print current_path.path_var_alias_assign[temp_alias].__dict__
            print "Path flow is:",current_path.flow
            print "Path Constraints are:"
            for constraint in current_path.path_constraint:
                if(constraint.elements==3):
                    print "Contraint:",constraint.typ,"LHS is:",constraint.lhs.name,"RHS is:",constraint.rhs.name, "RHS1 is:",constraint.rhs1.name
                elif(constraint.elements==2):
                    print "Contraint:",constraint.typ,"LHS is:",constraint.lhs.name,"RHS is:",constraint.rhs.name
                else:
                    log.error("Unsupported no. of elements in constraint="+str(constraint.elements))
            current_path.end_reached=1
            list_next_path.append(current_path) 
    elif(instr=="br"):
        if("cond" in line_desc):
            var=current_path.add_constraint_element(line_desc["cond"],"i1")
            if(prev_label==parse.get_branch_name(line_desc["label"])):
                one=current_path.get_constant(1,"i1")
                current_path.add_constraint_eq(var,one)
            elif(prev_label==parse.get_branch_name(line_desc["label1"])):
                zero=current_path.get_constant(0,"i1")
                current_path.add_constraint_eq(var,zero)
            else:
                #If landing on br statement from a statement below this
                #Instruction such that it is impossible to land on this instr
                log.debug("Current Path Impossible as can't land on this branch statement")
                current_path.stop=1
        next_path=current_path.make_pseudo_copy(lineno-1)
        if(prev_label!=parse.get_branch_name(line_desc["label"])):
            try:# I think this statement can't be reached
                if(prev_label!=parse.get_branch_name(line_desc["label1"])):
                    next_path.stop=1
            except: 
                next_path.stop=1
                log.debug("Current Path Impossible as can't land on this branch statement")

        list_next_path.append(next_path)
        
    elif(instr=="label"):
        label_name=parse.get_branch_name(line_desc["label"])
        try:
            #In case there is no entry point to this label
            label_jump_lines=(current_path.function.branches[label_name]).jump_point
        except:
            label_jump_lines=[]
        up_line=current_path.lineno-1
        
        if(not(up_line in label_jump_lines)):
            #Every label can be reached from previous line.If previous line 
            #is a br statement such that it makes it impossible to land here,
            #then the path is discarded
            label_jump_lines.append(up_line)
        for i in label_jump_lines:
            next_path=current_path.make_copy(i)
            next_path.label=label_name
            list_next_path.append(next_path)
            #next_path=execute_line(next_path,glb_lines,label_name)
            #for j in range(0,len(next_path)):
            #    list_next_path.append(next_path[j])
    elif(instr=="icmp"):
        next_path=current_path.make_pseudo_copy(lineno-1)
        lhs=line_desc["lhs"]
        rhs=line_desc["rhs"]
        rhs1=line_desc["rhs1"]
        rhs_typ=line_desc["rhs_typ"]
        lhs_var=next_path.add_assignment_element(lhs,'i1')
        one=next_path.get_constant(1,'i1')
        zero=next_path.get_constant(0,'i1')
        rhs_var=next_path.add_constraint_element(rhs,rhs_typ)
        rhs1_var=next_path.add_constraint_element(rhs1,rhs_typ)
        cond_flag=line_desc["cond_flag"]
        next_path2=next_path.make_copy(next_path.lineno)

        if(cond_flag=="eq"):
            next_path.add_constraint_eq(rhs_var,rhs1_var)
            next_path.add_constraint_eq(lhs_var,one)
            next_path2.add_constraint_ne(rhs_var,rhs1_var)
            next_path2.add_constraint_eq(lhs_var,zero)

        elif(cond_flag=="ne"):
            next_path.add_constraint_ne(rhs_var,rhs1_var)
            next_path.add_constraint_eq(lhs_var,one)
            next_path2.add_constraint_eq(rhs_var,rhs1_var)
            next_path2.add_constraint_eq(lhs_var,zero)

        elif(cond_flag=="ugt"):
            next_path.add_constraint_ugt(rhs_var,rhs1_var)
            next_path.add_constraint_eq(lhs_var,one)
            next_path2.add_constraint_ule(rhs_var,rhs1_var)
            next_path2.add_constraint_eq(lhs_var,zero)

        elif(cond_flag=="uge"):
            next_path.add_constraint_uge(rhs_var,rhs1_var)
            next_path.add_constraint_eq(lhs_var,one)
            next_path2.add_constraint_ult(rhs_var,rhs1_var)
            next_path2.add_constraint_eq(lhs_var,zero)

        elif(cond_flag=="ult"):
            next_path.add_constraint_ult(rhs_var,rhs1_var)
            next_path.add_constraint_eq(lhs_var,one)
            next_path2.add_constraint_uge(rhs_var,rhs1_var)
            next_path2.add_constraint_eq(lhs_var,zero)

        elif(cond_flag=="ule"):
            next_path.add_constraint_ule(rhs_var,rhs1_var)
            next_path.add_constraint_eq(lhs_var,one)
            next_path2.add_constraint_ugt(rhs_var,rhs1_var)
            next_path2.add_constraint_eq(lhs_var,zero)

        elif(cond_flag=="sgt"):
            next_path.add_constraint_sgt(rhs_var,rhs1_var)
            next_path.add_constraint_eq(lhs_var,one)
            next_path2.add_constraint_sle(rhs_var,rhs1_var)
            next_path2.add_constraint_eq(lhs_var,zero)

        elif(cond_flag=="sge"):
            next_path.add_constraint_sge(rhs_var,rhs1_var)
            next_path.add_constraint_eq(lhs_var,one)
            next_path2.add_constraint_slt(rhs_var,rhs1_var)
            next_path2.add_constraint_eq(lhs_var,zero)

        elif(cond_flag=="slt"):
            next_path.add_constraint_slt(rhs_var,rhs1_var)
            next_path.add_constraint_eq(lhs_var,one)
            next_path2.add_constraint_sge(rhs_var,rhs1_var)
            next_path2.add_constraint_eq(lhs_var,zero)
    
        elif(cond_flag=="sle"):
            next_path.add_constraint_sle(rhs_var,rhs1_var)
            next_path.add_constraint_eq(lhs_var,one)
            next_path2.add_constraint_sgt(rhs_var,rhs1_var)
            next_path2.add_constraint_eq(lhs_var,zero)
        
        list_next_path.append(next_path)
        list_next_path.append(next_path2)

    elif(instr=="add"):
        next_path=current_path.make_pseudo_copy(lineno-1)
        lhs=line_desc["lhs"]
        rhs=line_desc["rhs"]
        rhs1=line_desc["rhs1"]
        rhs_typ=line_desc["rhs_typ"]
        lhs_var=next_path.add_assignment_element(lhs,rhs_typ)
        rhs_var=next_path.add_constraint_element(rhs,rhs_typ)
        rhs1_var=next_path.add_constraint_element(rhs1,rhs_typ)
        flag=line_desc["flag"] #Currently not in use
        next_path.add_constraint_add(lhs_var,rhs_var,rhs1_var)
        list_next_path.append(next_path)

        

    elif(instr=="load"):
        next_path=current_path.make_pseudo_copy(lineno-1)
        lhs=line_desc["lhs"]
        rhs=line_desc["rhs"]
        rhs_typ=line_desc["rhs_typ"]
        converted_typ=parse.convert_pointer_typ(rhs_typ)
        lhs_var=next_path.add_assignment_element(lhs,converted_typ)
        rhs_var=next_path.add_constraint_element(rhs,converted_typ)
        next_path.add_constraint_eq(lhs_var,rhs_var)
        list_next_path.append(next_path)

    elif(instr=="store"):
        #What to do in case lhs_typ!=rhs_typ
        next_path=current_path.make_pseudo_copy(lineno-1)
        lhs=line_desc["lhs"]
        rhs=line_desc["rhs"]
        lhs_typ=line_desc["lhs_typ"]
        rhs_typ=line_desc["rhs_typ"]
        lhs_var=next_path.add_assignment_element(lhs,rhs_typ)
        rhs_var=next_path.add_constraint_element(rhs,rhs_typ)
        next_path.add_constraint_eq(lhs_var,rhs_var)
        list_next_path.append(next_path)

    #Instructions having no effect or not supported                  
    elif((instr=="alloca")):
        next_path=current_path.make_pseudo_copy(lineno-1)
        list_next_path.append(next_path)
    elif((instr=="bitcast")):
        log.error("Current Instruction Not supported:"+str(instr))
        next_path=current_path.make_pseudo_copy(lineno-1)
        list_next_path.append(next_path)


    #for nex in list_next_path:
    #    print "Nex->:",nex.lineno,"Stop->:",nex.stop
    #    if(nex.stop!=0):
    #        print "Path flow is:",nex.flow
    #print ""
    return list_next_path

def execution(glb_lines,start_line,glb_func):
    log.debug("Starting Execution-Start line:"+str(start_line))
    current_path=path(start_line)
    current_path.function=find_current_function(start_line,glb_func)
    log.debug("Start Function:"+str(current_path.function.name))
    current_path_list=[]
    impossible_path_list=[]
    successful_path_list=[]
    current_path_list.append(current_path)
    
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


#TODO:Draw Path Flow Tree  (Successful and Impossible Paths)
#TODO:Get Example Values of Defined variables
#I left off, classes function not checked/log not added there.Take an overall look of the while program again      
