import sys
import os

def loadFile(filename):
    lines = []
    with open(filename) as g:
        lines = g.readlines()
    return lines

def saveFile(filename, machine_code):
    filepath, file_extension = os.path.splitext(filename)
    print(filepath)
    print(os.path.basename(filename))
    if not file_extension:
        filepath += "/" + os.path.basename(filename)
    filepath += '.asm'

    with open(filepath, 'w') as file_handler:
        for line in machine_code:
            file_handler.write("{}\n".format(line))

def cleanCode(lines):
    code_lines = [line.strip() for line in lines if (line.strip() and line.strip()[0:2] != '//')]

    clean_lines = []
    for line in code_lines:
        if '//' in line:
            clean_lines.append(line.split('//')[0].strip())
        else:
            clean_lines.append(line)

    return clean_lines


def push(vsplit, jump_flag):
    asm = []
    address_dict = {"local" : "@LCL",
                    "argument": "@ARG",
                    "this": "@THIS",
                    "that": "@THAT"}

    pointer_dict = {"sppointer": "@R0",
                    "lclpointer": "@R1",
                    "argpointer": "@R2",
                    "thispointer": "@R3",
                    "thatpointer": "@R4",
                    "temp": "@R5",
                    "pointer": "@R3",
                    "static": "@16",
                    }

    asm.append('@' + vsplit[2])
    asm.append('D=A')

    if vsplit[1] in pointer_dict:
        asm.append(pointer_dict[vsplit[1]])
        asm.append('A=D+A')
        asm.append('D=M')
    elif vsplit[1] != "constant":
        asm.append(address_dict[vsplit[1]])
        asm.append('A=D+M')
        asm.append('D=M')


    asm.append('@SP')
    asm.append('A=M')
    asm.append('M=D')
    asm.append('@SP')
    asm.append('M=M+1')

    return asm, jump_flag

def pop(vsplit, jump_flag):
    address_dict = {"local": "@LCL",
                    "argument": "@ARG",
                    "this": "@THIS",
                    "that": "@THAT"}

    pointer_dict = {"sppointer": "@R0",
                    "lclpointer": "@R1",
                    "argpointer": "@R2",
                    "thispointer": "@R3",
                    "thatpointer": "@R4",
                    "temp": "@R5",
                    "pointer": "@R3",
                    "static": "@16",
                    }

    asm = []

    if vsplit[1] in pointer_dict:
        asm += [pointer_dict[vsplit[1]],
         'D=A',
         ]
    else:
        asm += [address_dict[vsplit[1]],
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

def label(vsplit, jump_flag):
    return ['(' + vsplit[1] + ')'], jump_flag

def goto(vsplit, jump_flag):
    return ['@' + vsplit[1],
            '0;JMP'], jump_flag

def ifgoto(vsplit, jump_flag):
    jump_flag += 1
    return ['@SP',
            'M=M-1',
            'A=M',
            'D=M',
            '@FALSE' + str(jump_flag),
            'D;JEQ',
            '@' + vsplit[1],
            '0;JMP',
            '(FALSE' + str(jump_flag) + ')'], jump_flag

def callCommand(vsplit, jump_flag):
    jump_flag += 1

    # push returnAddress
    asm = ["@RETURN_FLAG" + str(jump_flag),
           "D=A",
           "@SP",
           "M=M+1",
           "A=M-1",
           "M=D"]

    #push frame info
    asm += push(["push", "lclpointer", "0"], jump_flag)[0]
    asm += push(["push", "argpointer", "0"], jump_flag)[0]
    asm += push(["push", "thispointer", "0"], jump_flag)[0]
    asm += push(["push", "thatpointer", "0"], jump_flag)[0]

    asm += ["@" + vsplit[2],
            "D=A",
            "@5",
            "D=D+A",
            "@SP",
            "D=M-D",
            "@ARG",
            "M=D",
            "@SP",
            "D=M",
            "@LCL",
            "M=D",
            "@" + vsplit[1],
            "0;JMP",
            "(RETURN_FLAG" + str(jump_flag) + ")"]

    return asm, jump_flag

def funcCommand(vsplit, jump_flag):
    asm, jump_flag = push(["push", "constant", "0"], jump_flag)
    asm *= int(vsplit[2])
    asm = ["(" + vsplit[1] + ")"] + asm
    return asm, jump_flag

def returnCommand(vsplit, jump_flag):
    asm = ["@LCL",
           "D=M",
           "@R11",
           "M=D",
           "@5",
           "A=D-A",
           "D=M",
           "@R12",
           "M=D"]

    asm += pop(["pop", "argument", "0"], jump_flag)[0]

    asm += ["@ARG",
            "D=M+1",
            "@SP",
            "M=D",
            "@R11",
            "A=M-1",
            "D=M",
            "@THAT",
            "M=D",
            "@R11",
            "D=M",
            "@2",
            "D=D-A",
            "A=D",
            "D=M",
            "@THIS",
            "M=D",
            "@R11",
            "D=M",
            "@3",
            "D=D-A",
            "A=D",
            "D=M",
            "@ARG",
            "M=D",
            "@R11",
            "D=M",
            "@4",
            "D=D-A",
            "A=D",
            "D=M",
            "@LCL",
            "M=D",
            "@R12",
            "A=M",
            "0;JMP"]

    return asm, jump_flag

def translateVcode(vcode, jump_flag):
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
                    "not": opY,
                    "label": label,
                    "goto": goto,
                    "if-goto": ifgoto,
                    "function": funcCommand,
                    "return": returnCommand,
                    "call": callCommand
                    }

    asm = []
    for line in vcode:
        print(line)
        vsplit = line.split()
        assembly, jump_flag = functiondict[vsplit[0]](vsplit, jump_flag)
        asm.append("// " + line)
        asm += assembly
    return asm, jump_flag

def bootstrap():
    asm = ["@256",
            "D=A",
            "@0",
            "M=D"]

    asm += callCommand(["call", "Sys.init", "0"], 0)[0]

    return asm



def main():
    locations = sys.argv
    locations = ["", "FunctionCalls/StaticsTest"]
    for location in locations[1:]:
        filenames = []
        if location.endswith(".vm"):
            filenames = [location]
        else:
            for file in os.listdir(location):
                if file.endswith(".vm"):
                    filenames.append(location + "/" + file)

        print(filenames)

        assembly = bootstrap()
        jump_flag = 1
        for filename in filenames:
            vcode = loadFile(filename)
            vcode = cleanCode(vcode)
            asm, jump_flag = translateVcode(vcode, jump_flag)
            assembly += asm

        saveFile(location, assembly)


if __name__ == "__main__":
    main()