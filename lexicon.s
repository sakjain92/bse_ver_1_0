//Defining Structure
//All types ends with '_typ'. rhs starts with 'rhsx_' where x is number or none. Array is the only one with multiple words
%struct.structure2 = type { %struct.structure2*, %struct.structure1,[2 x [3 x float]],i32 }
instr:type;lhs:%struct.structure2;rhs_typ:%struct.structure2*;rhs1_typ:%struct.structure1;rhs2_typ:[2 x [3 x float]];rhs3_typ:i32;

