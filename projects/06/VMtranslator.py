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