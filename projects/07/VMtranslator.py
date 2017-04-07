import sys
import os

def loadFile(filename):
    lines = []
    with open(filename) as g:
        lines = g.readlines()
    return lines

def saveFile(filename, machine_code):
    filepath, file_extension = os.path.splitext(filename)
    filepath += '.asm'

    with open(filepath, 'w') as file_handler:
        for line in machine_code:
            file_handler.write("{}\n".format(line))

def cleanCode(lines):
    return [line.strip() for line in lines if (line.strip() and line.strip()[0:2] != '//')]

def push(vsplit, jump_flag):
    asm = []
    storage_dict = {"local" : "@LCL",
                    "argument": "@ARG",
                    "this": "@THIS",
                    "that": "@THAT",
                    "temp": "@R5",
                    "pointer": "@R3",
                    "static": "@16"}

    asm.append('@' + vsplit[2])
    asm.append('D=A')

    if vsplit[1] == "temp" or vsplit[1] == "pointer" or vsplit[1] == "static":
        asm.append(storage_dict[vsplit[1]])
        asm.append('A=D+A')
        asm.append('D=M')
    elif vsplit[1] != "constant":
        asm.append(storage_dict[vsplit[1]])
        asm.append('A=D+M')
        asm.append('D=M')


    asm.append('@SP')
    asm.append('A=M')
    asm.append('M=D')
    asm.append('@SP')
    asm.append('M=M+1')

    return asm, jump_flag

def pop(vsplit, jump_flag):
    storage_dict = {"local": "@LCL",
                    "argument": "@ARG",
                    "this": "@THIS",
                    "that": "@THAT",
                    "temp": "@R5",
                    "pointer": "@R3",
                    "static": "@16"}

    asm = []

    if vsplit[1] == "temp" or vsplit[1] == "pointer" or vsplit[1] == "static":
        asm += [storage_dict[vsplit[1]],
         'D=A',
         ]
    else:
        asm += [storage_dict[vsplit[1]],
           "D=M"]

    asm += ["@" + vsplit[2],
           "D=D+A",
           "@SP",
           "A=M",
           "M=D",
           "A=A-1",
           "D=M",
           "A=A+1",
           "A=M",
           "M=D",
           "@SP",
           "M=M-1"]

    return asm, jump_flag


def opXY(vsplit, jump_flag):
    op_dict = {"add": "D+M",
                  "sub": "M-D",
               "and": "D&M",
               "or": "D|M"}

    op = op_dict[vsplit[0]]

    return ["@SP",
          "M=M-1",
          "A=M",
          "D=M",
          "A=A-1",
          "M=" + op], jump_flag

def opY(vsplit, jump_flag):
    op_dict = {"neg": "-M",
               "not": "!M"}

    op = op_dict[vsplit[0]]

    return ["@SP",
            "A=M-1",
            "M=" + op], jump_flag

def compare(vsplit, jump_flag):
    jump_dict = {"eq": "JEQ",
                 "lt": "JLT",
                 "gt": "JGT"}

    jump = jump_dict[vsplit[0]]


    jump_flag += 1
    return ["@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "A=A-1",
            "D=M-D",
            "@TRUE" + str(jump_flag),
            "D;" + jump,
            "@SP",
            "A=M-1",
            "M=0",
            "@CONTINUE" + str(jump_flag),
            "0;JMP",
            "(TRUE" + str(jump_flag) + ")",
            "@SP",
            "A=M-1",
            "M=-1",
            "(CONTINUE" + str(jump_flag) + ")"
            ], jump_flag

def translateVcode(vcode):
    jump_flag = 0
    functiondict = {"push": push,
                    "pop": pop,
                    "add": opXY,
                    "sub": opXY,
                    "and": opXY,
                    "or": opXY,
                    "eq": compare,
                    "lt": compare,
                    "gt": compare,
                    "neg": opY,
                    "not": opY
                    }

    asm = []
    for line in vcode:
        vsplit = line.split()
        assembly, jump_flag = functiondict[vsplit[0]](vsplit, jump_flag)
        asm += assembly
    return asm


def main():
    filenames = sys.argv
    filenames = ["", "StaticTest.vm"]
    for filename in filenames[1:]:
        vcode = loadFile(filename)
        vcode = cleanCode(vcode)
        assembly = translateVcode(vcode)
        saveFile(filename, assembly)


if __name__ == "__main__":
    main()