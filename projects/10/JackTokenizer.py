# Jack Tokenizer
# Takes text file and converts to a series of tokens along with their token type
# Used by CompilationEngine.py to create XML tree of source file.


import string
import re

class JackTokenizer:

    KEYWORDS = ["CLASS",
                "METHOD",
                "FUNCTION",
                "CONSTRUCTOR",
                "INT",
                "BOOLEAN",
                "CHAR",
                "VOID",
                "VAR",
                "STATIC",
                "FIELD",
                "LET",
                "DO",
                "IF",
                "ELSE",
                "WHILE",
                "RETURN",
                "TRUE",
                "FALSE",
                "NULL",
                "THIS"]

    IDENTIFIER_CHARS = string.ascii_letters + string.digits + '_'

    SYMBOLS = '{}()[].,;+-*/&|<>=~'

    def __init__(self, filename):
        self.input = self.cleanCode(self.loadFile(filename))
        self.tokens = self.tokenize()
        self.current_token = ''
        self.token_index = 0

    def loadFile(self, filename):
        lines = []
        with open(filename) as g:
            lines = g.readlines()
        return lines

    def cleanCode(self, lines):
        """Removes comments and empty lines from source input"""

        # remove empty lines and lines beginning with // comment
        code_lines = [line.strip() for line in lines if (line.strip() and line.strip()[0:2] != '//')]

        # remove inline comments
        clean_lines = []
        for line in code_lines:
            if '//' in line:
                clean_lines.append(line.split('//')[0].strip())
            else:
                clean_lines.append(line)

        # remove multiline comments
        clean_lines = '\n'.join(clean_lines)
        clean_lines = re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" ,clean_lines)

        return clean_lines

    def hasMoreTokens(self):
        return self.token_index < len(self.tokens) - 1

    def advance(self):
        self.current_token = self.tokens[self.token_index]
        if self.hasMoreTokens():
            self.next_token = self.tokens[self.token_index + 1]
        else:
            self.next_token = False
        self.token_index += 1
        return self.current_token


    def tokenize(self):
        self.pointer = 0
        tokens = []

        while (self.pointer < len(self.input)):
            if self.input[self.pointer] in self.SYMBOLS:
                tokens.append(self.parseSymbol())
            elif self.input[self.pointer] in string.digits:
                tokens.append(self.parseIntegerConstant())
            elif ((self.input[self.pointer] in string.ascii_letters) or (self.input[self.pointer] == '_')):
                tokens.append(self.parseKeywordOrIdentifier())
            elif self.input[self.pointer] == '"':
                tokens.append(self.parseStringConstant())
            else:
                self.pointer += 1

        return tokens

    def parseKeywordOrIdentifier(self):
        """Parse tokens beginning with alpha character or underscore, corresponding to keywords or identifiers"""
        token = ""

        while (self.input[self.pointer] in self.IDENTIFIER_CHARS):
            token += self.input[self.pointer]
            self.pointer += 1

        if token.upper() in self.KEYWORDS:
            return ('keyword', token)
        else:
            return ('identifier', token)

    def parseSymbol(self):
        token = self.input[self.pointer]
        self.pointer += 1

        return ('symbol', token)

    def parseIntegerConstant(self):
        """Parse tokens beginning with a digit, corresponding to an integerConstant"""
        token = ""

        while (self.input[self.pointer] in string.digits):
            token += self.input[self.pointer]
            self.pointer += 1

        return ('integerConstant', token)

    def parseStringConstant(self):
        """Parse tokens beginning with a double quote, corresponding to a stringConstant"""
        token = ""

        # check pointer points at beginning of string constant
        if self.input[self.pointer] != '"':
            raise ValueError('Tried to parse string constant that does not begin with double quotes')

        # skip over opening double quote
        self.pointer += 1

        while (self.input[self.pointer] != '"'):
            if self.input[self.pointer] is '\n':
                raise ValueError('Newline character found in string constant')
            token += self.input[self.pointer]
            self.pointer += 1

        # skip over closing double quote
        self.pointer += 1

        return ('stringConstant', token)

    def tokensToXML(self):
        """Test function to create xml file of tokens. Used to check diff with known valid tokenizer output to check
        validity"""
        xml = []
        xml.append("<tokens>")
        for token in self.tokens:
            xml_string = "<{}> {} </{}>".format(token[0], token[1], token[0])
            xml.append(xml_string)
        xml.append("</tokens>\n")

        return '\n'.join(xml)

#unit testing
def main():
    input_file = "ExpressionLessSquare/SquareGame.jack"
    tokenizer = JackTokenizer(input_file)
    print(tokenizer.tokensToXML())


if __name__ == "__main__":
    main()