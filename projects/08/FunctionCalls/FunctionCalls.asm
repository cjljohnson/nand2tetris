@256
D=A
@0
M=D
@RETURN_FLAG1
D=A
@SP
M=M+1
A=M-1
M=D
@0
D=A
@R1
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@R2
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@R3
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@R4
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@5
D=D+A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Sys.init
0;JMP
(RETURN_FLAG1)
(Sys.init)
@4
D=A
@SP
A=M
M=D
@SP
M=M+1
@RETURN_FLAG2
D=A
@SP
M=M+1
A=M-1
M=D
@0
D=A
@R1
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@R2
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@R3
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@R4
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
@5
D=D+A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(RETURN_FLAG2)
(WHILE)
@WHILE
0;JMP
(Main.fibonacci)
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
A=A-1
D=M-D
@TRUE3
D;JLT
@SP
A=M-1
M=0
@CONTINUE3
0;JMP
(TRUE3)
@SP
A=M-1
M=-1
(CONTINUE3)
@SP
M=M-1
A=M
D=M
@IF_TRUE
D;JGT
@IF_FALSE
0;JMP
(IF_TRUE)
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
@LCL
D=M
@R11
M=D
@5
A=D-A
D=M
@R12
M=D
@ARG
D=M
@0
D=D+A
@SP
A=M
M=D
A=A-1
D=M
A=A+1
A=M
M=D
@SP
M=M-1
@ARG
D=M+1
@SP
M=D
@R11
A=M-1
D=M
@THAT
M=D
@R11
D=M
@2
D=D-A
A=D
D=M
@THIS
M=D
@R11
D=M
@3
D=D-A
A=D
D=M
@ARG
M=D
@R11
D=M
@4
D=D-A
A=D
D=M
@LCL
M=D
@R12
A=M
0;JMP
(IF_FALSE)
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
A=A-1
M=M-D
@RETURN_FLAG4
D=A
@SP
M=M+1
A=M-1
M=D
@0
D=A
@R1
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@R2
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@R3
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@R4
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
@5
D=D+A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(RETURN_FLAG4)
@0
D=A
@ARG
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
A=A-1
M=M-D
@RETURN_FLAG5
D=A
@SP
M=M+1
A=M-1
M=D
@0
D=A
@R1
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@R2
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@R3
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@R4
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
@5
D=D+A
@SP
D=M-D
@ARG
M=D
@SP
D=M
@LCL
M=D
@Main.fibonacci
0;JMP
(RETURN_FLAG5)
@SP
M=M-1
A=M
D=M
A=A-1
M=D+M
@LCL
D=M
@R11
M=D
@5
A=D-A
D=M
@R12
M=D
@ARG
D=M
@0
D=D+A
@SP
A=M
M=D
A=A-1
D=M
A=A+1
A=M
M=D
@SP
M=M-1
@ARG
D=M+1
@SP
M=D
@R11
A=M-1
D=M
@THAT
M=D
@R11
D=M
@2
D=D-A
A=D
D=M
@THIS
M=D
@R11
D=M
@3
D=D-A
A=D
D=M
@ARG
M=D
@R11
D=M
@4
D=D-A
A=D
D=M
@LCL
M=D
@R12
A=M
0;JMP