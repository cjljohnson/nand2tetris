import sys
import os

def loadFile(filename):
    lines = []
    with open(filename) as g:
        lines = g.readlines()
    return lines

def saveFile(filename, machine_code):
    filepath, file_extension = os.path.splitext(filename)
    filepath += '.hack'

    with open(filepath, 'w') as file_handler:
        for line in machine_code:
            file_handler.write("{}\n".format(line))

def cleanCode(lines):
    return [line.strip() for line in lines if (line.strip() and line.strip()[0:2] != '//')]

def findLabels(lines):
    command = 0
    symbols = {'SP' : 0x0000,
               'LCL' : 0x0001,
               'ARG' : 0x0002,
               'THIS' : 0x0003,
               'THAT' : 0x0004,
               'R0' : 0x0000,
               'R1' : 0x0001,
               'R2': 0x0002,
               'R3': 0x0003,
               'R4': 0x0004,
               'R5': 0x0005,
               'R6': 0x0006,
               'R7': 0x0007,
               'R8': 0x0008,
               'R9': 0x0009,
               'R10': 0x000a,
               'R11': 0x000b,
               'R12': 0x000c,
               'R13': 0x000d,
               'R14': 0x000e,
               'R15': 0x000f,
               'SCREEN' : 0x4000,
               'KBD' : 0x6000}

    for line in lines:
        if line[0] == '(':
            label = line[1:line.index(')')]
            symbols[label] = command
        else:
            command += 1
    return symbols

def parseAssembly(lines, symbols):
    machine_code = []
    address_counter = 16

    for line in lines:
        if line[0] == '(':
            continue
        elif line[0] == '@':
            address_counter = aCommand(line, symbols, address_counter, machine_code)
        else:
            cCommand(line, symbols, machine_code)
    return machine_code



def aCommand(line, symbols, address_counter, machine_code):
    line = line[1:]
    num = 0
    try:
        num = int(line)
    except ValueError:
        if line not in symbols:
            symbols[line] = address_counter
            address_counter += 1
        num = symbols[line]
    num_bin = "{0:{fill}16b}".format(num, fill='0')
    machine_code.append(num_bin)
    return address_counter

def cCommand(line, symbols, machine_code):
    try:
        line = line[:line.index('//')]
        line.strip()
    except:
        line = line.strip()

    bin_string = "111"
    comp = '0000000'
    dest='000'
    jump='000'

    if ';' in line:
        jump = parseJump(line[line.index(';') + 1:])
        line = line[:line.index(';')]
    if '=' in line:
        comp = parseComp(line[line.index('=') + 1:])
        dest = parseDest(line[:line.index('=')])
    else:
        comp = parseComp(line.strip())

    bin_string += comp + dest + jump
    machine_code.append(bin_string)

def parseJump(jcode):
    jcode = jcode.strip()

    jcodes = {'JGT' : '001',
              'JEQ' : '010',
              'JGE' : '011',
              'JLT' : '100',
              'JNE' : '101',
              'JLE' : '110',
              'JMP' : '111'}

    if jcode in jcodes:
        return jcodes[jcode]
    else:
        return '000'

def parseComp(ccode):
    ccode = ccode.strip()

    ccodes = {'0' : '0101010',
              '1' : '0111111',
              '-1' : '0111010',
              'D' : '0001100',
              'A' : '0110000',
              '!D' : '0001101',
              '!A' : '0110001',
              '-D' : '0001111',
              '-A' : '0110011',
              'D+1' : '0011111',
              'A+1' : '0110111',
              'D-1' : '0001110',
              'A-1' : '0110010',
              'D+A' : '0000010',
              'D-A' : '0010011',
              'A-D' : '0000111',
              'D&A' : '0000000',
              'D|A' : '0010101',
              'M' : '1110000',
              '!M' : '1110001',
              '-M' : '1110011',
              'M+1' : '1110111',
              'M-1' : '1110010',
              'D+M' : '1000010',
              'D-M' : '1010011',
              'M-D' : '1000111',
              'D&M' : '1000000',
              'D|M' : '1010101'}

    return ccodes[ccode]

def parseDest(dcode):
    dcode = dcode.strip()

    bin_string = ''

    if 'A' in dcode:
        bin_string += '1'
    else:
        bin_string += '0'

    if 'D' in dcode:
        bin_string += '1'
    else:
        bin_string += '0'

    if 'M' in dcode:
        bin_string += '1'
    else:
        bin_string += '0'

    return bin_string

def main():
    filenames = sys.argv
    filenames = ["", "Sys.asm"]
    for filename in filenames[1:]:
        assembly = loadFile(filename)
        assembly = cleanCode(assembly)
        symbols = findLabels(assembly)
        machine_code = parseAssembly(assembly, symbols)
        saveFile(filename, machine_code)


if __name__ == "__main__":
    main()