import sys
import os
from CompilationEngine import CompilationEngine

def saveFile(filename, xml_list):
    filepath, file_extension = os.path.splitext(filename)
    print(filepath)
    print(os.path.basename(filename))
    if not file_extension:
        filepath += "/" + os.path.basename(filename)
    filepath += '_CJTEST.xml'

    with open(filepath, 'w') as file_handler:
        for line in xml_list:
            file_handler.write("{}\n".format(line))

def main():
    locations = sys.argv
    for location in locations[1:]:
        filenames = []
        if location.endswith(".jack"):
            filenames = [location]
        else:
            for file in os.listdir(location):
                if file.endswith(".jack"):
                    filenames.append(location + "/" + file)

        print(filenames)

        for filename in filenames:
            print(filename)
            comp_engine = CompilationEngine(filename)
            saveFile(filename, comp_engine.xml)

if __name__ == "__main__":
    main()