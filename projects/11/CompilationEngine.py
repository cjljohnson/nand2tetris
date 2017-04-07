from JackTokenizer import JackTokenizer

class SymbolTable:
    def __init__(self, parent):
        self.parent = parent
        self.table = {}
        self.kind_index = {"static": 0,
                      "field": 0,
                      "argument": 0,
                      "local": 0}

    def define(self, name, type, kind):
        if name in self.table:
            raise ValueError(name + " is already defined in the symbol table")


        self.table[name] = (type, kind, self.kind_index[kind])
        self.kind_index[kind] += 1

    def varCount(self, kind):
        if self.parent is None:
            return self.kind_index[kind]
        else:
            return self.kind_index[kind] + self.parent.varCount(kind)

    def kindOf(self, name):
        if name in self.table:
            return self.table[name][1]
        if self.parent is None:
            raise ValueError("Could not find " + name + "in symbol table")
        else:
            return self.parent.kindOf(name)

    def typeOf(self, name):
        if name in self.table:
            return self.table[name][0]
        if self.parent is None:
            raise ValueError("Could not find " + name + "in symbol table")
        else:
            return self.parent.typeOf(name)

    def indexOf(self, name):
        if name in self.table:
            return self.table[name][2]
        if self.parent is None:
            raise ValueError("Could not find " + name + " in symbol table")
        else:
            return self.parent.indexOf(name)


class CompilationEngine:

    UNARYOP = ['-', '~']
    OP = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    KEYWORDCONSTANT = ['true', 'false', 'null', 'this']

    UNARYOP_VCODE = {'-': 'neg', '~': 'not'}
    OPERATOR_VCODE = {'+': 'add', '-': 'sub', '*': 'call Math.multiply 2', '/': 'call Math.divide 2', '&': "and", '|': "or", '<': "lt", '>': "gt", '=': "eq"}
    KEYWORDCONSTANT_VCODE = {'true': ['push constant 0', 'not'], 'false': ['push constant 0'], 'null': ['push constant 0'], 'this': ['push pointer 0']}

    def __init__(self, filename):
        self.tokenizer = JackTokenizer(filename)
        self.token = self.tokenizer.advance()
        self.xml = []
        self.vcode = []
        self.classcode = []
        self.labelIndex = 1
        self.compileClass()

    def token2XML(self):
        body = self.token[1]
        body = body.replace('&', '&amp;')
        body = body.replace('<', '&lt;')
        body = body.replace('>', '&gt;')
        body = body.replace('"', '&quot;')
        return "<{}> {} </{}>".format(self.token[0], body, self.token[0])

    def advanceToken(self):
        self.token = self.tokenizer.advance()

    def matchToken(self, token_type, values):
        """Ensures current token matches the token type and value given and appends to xml, otherwise throws
        ValueError"""
        if token_type and isinstance(token_type, str):
            token_type = [token_type]
        if values and isinstance(token_type, str):
            values = [values]
        if (token_type and self.token[0] not in token_type) or (values and self.token[1] not in values):
            for i, line in enumerate(self.xml):
                print(str(i) + line)
            raise ValueError('Expected{}{}, but instead got '.format(' ' + str(token_type), ' ' + str(values)) + str(self.token)
                             + "at tokenizer line " + str(self.tokenizer.token_index))

    def matchType(self):
        """"match type of form:
        'int'|'char'|'boolean'|className """
        if self.token[0] == 'keyword' and self.token[1] in ['int', 'char', 'boolean']:
            return self.token[1]
        elif self.token[0] == 'identifier':
            return self.token[1]
        else:
            raise ValueError('Expected type, but instead got ' + str(self.token))

    def isType(self):
        """"match type of form:
        'int'|'char'|'boolean'|className """

        if self.token[0] == 'keyword' and self.token[1] in ['int', 'char', 'boolean']:
            return True
        elif self.token[0] == 'identifier':
            return True
        else:
            return False

    def vcodeVariable(self, command, name, symbols):
        """writes vcode of type 'command kind index' based on name for given symbol table"""
        kind_dict = {'static': 'static', 'field': 'this', 'argument': 'argument', 'local': 'local'}

        if name == 'this':
            self.vcode.append(command + ' pointer 0')
        else:
            self.vcode.append(command + ' ' + kind_dict[symbols.kindOf(name)] + ' ' + str(symbols.indexOf(name)))

    def vcodeJump(self, command, name, index):
        #if index == False:

        if index:
            self.vcode.append(command + ' ' + name + str(index))
        else:
            index = self.labelIndex
            self.labelIndex += 1
            self.vcode.append(command + ' ' + name + str(index))
        return index

    def compileClass(self):
        """compiles class of form:
        'class' classname '{' classVarDec* subroutineDec* '}'"""

        symbols = SymbolTable(None)


        #'class'
        self.matchToken('keyword', 'class')

        #classname
        self.advanceToken()
        self.matchToken('identifier', '')
        class_name = self.token[1]
        self.class_name = self.token[1]

        #{
        self.advanceToken()
        self.matchToken('symbol', '{')

        #classVarDec*
        self.advanceToken()
        while self.token[0] == 'keyword' and self.token[1] in ['field', 'static']:
            self.compileClassVarDec(symbols)
            self.advanceToken()

        #subroutineDec*
        while self.token[0] == 'keyword' and self.token[1] in ['constructor', 'function', 'method']:
            self.compileSubroutine(symbols, class_name)
            self.advanceToken()

        #}
        self.matchToken('symbol', '}')

    def compileClassVarDec(self, symbols):
        """compiles class variable declaration of form:
        ('static'|'field') type varName (',' varName)* ';' """


        #('static'|'field')
        self.matchToken('keyword', ['static', 'field'])
        kind = self.token[1]

        #type
        self.advanceToken()
        self.matchType()
        type = self.token[1]

        #varName
        self.advanceToken()
        self.matchToken('identifier', '')
        name = self.token[1]
        symbols.define(name, type, kind)
        self.advanceToken()

        #(',' varName)*
        while self.token[1] == ',':
            self.matchToken('symbol', ',')
            self.advanceToken()
            self.matchToken('identifier', '')
            name = self.token[1]
            symbols.define(name, type, kind)
            self.advanceToken()

        #';'
        self.matchToken('symbol', ';')

    def compileSubroutine(self, parent_symbols, class_name):
        """compiles subroutine of form:
        ('constructor'|'function'|'method') ('void'|type) subroutineName '(' parameterList ')' subroutineBody """

        symbols = SymbolTable(parent_symbols)
        parameter_count = 0
        is_constructor = False

        #('constructor'|'function'|'method')
        self.matchToken('keyword', ['constructor', 'function', 'method'])
        if self.token[1] == 'method':
            parameter_count += 1
            symbols.define('this', self.class_name, 'argument')
            self.vcode.append('push argument 0')
            self.vcode.append('pop pointer 0')
        elif self.token[1] == 'constructor':
            field_variables = symbols.varCount('field')
            self.vcode.append('push constant ' + str(field_variables))
            self.vcode.append('call Memory.alloc 1')
            self.vcode.append('pop pointer 0')

        #('void'|type)
        self.advanceToken()
        if self.token[1] == 'void':
            self.matchToken('keyword', 'void')
        else:
            self.matchType()
        return_type = self.token[1]

        #subroutineName
        self.advanceToken()
        self.matchToken('identifier', '')
        subroutine_name = self.token[1]

        #(
        self.advanceToken()
        self.matchToken('symbol', '(')

        #parameterList
        self.advanceToken()
        parameter_count += self.compileParameterList(symbols)

        #)
        self.matchToken('symbol', ')')

        #subroutineBody
        self.advanceToken()
        self.compileSubroutineBody(symbols)

        self.classcode.append('function ' + class_name + '.' + subroutine_name + ' ' + str(symbols.kind_index['local']))
        self.classcode += self.vcode
        self.vcode = []

    def compileParameterList(self, symbols):
        """compiles parameterList of form:
        ((type varName) (',' type varName)*)? """

        parameter_count = 0

        #((type varName) (',' type varName)*)?
        if self.isType():
            type = self.matchType()
            self.advanceToken()
            self.matchToken('identifier', '')
            name = self.token[1]
            parameter_count += 1
            self.advanceToken()
            symbols.define(name, type, 'argument')

        while self.token[1] == ',':
            self.matchToken('symbol', ',')
            self.advanceToken()
            type = self.matchType()
            self.advanceToken()
            self.matchToken('identifier', '')
            name = self.token[1]
            parameter_count += 1
            self.advanceToken()
            symbols.define(name, type, 'argument')

        return parameter_count



    def compileSubroutineBody(self, symbols):
        """compiles subroutine body of form:
        '{' varDec* statements '}' """

        #{
        self.matchToken('symbol', '{')

        #varDec*
        self.advanceToken()
        while self.token[0] == 'keyword' and self.token[1] == 'var':
            self.compileVarDec(symbols)
            self.advanceToken()

        #statements
        self.compileStatements(symbols)

        #}
        self.matchToken('symbol', '}')


    def compileVarDec(self, symbols):
        """"compiles variable declarations of form:
        'var' type varName (',' varName)* ';' """

        #'var'
        self.matchToken('keyword', 'var')

        #type
        self.advanceToken()
        type = self.matchType()

        #varName
        self.advanceToken()
        self.matchToken('identifier', '')
        name = self.token[1]
        self.advanceToken()
        symbols.define(name, type, 'local')

        # (',' varName)*
        while self.token[1] == ',':
            self.matchToken('symbol', ',')
            self.advanceToken()
            self.matchToken('identifier', '')
            name = self.token[1]
            self.advanceToken()
            symbols.define(name, type, 'local')

        # ';'
        self.matchToken('symbol', ';')

    def compileStatements(self, symbols):
        """compiles statements of form:
        statement*
        statement are of form:
        letStatement|ifStatement|whileStatement|doStatement|returnStatement """

        #statements*
        while(True):
            if self.token[0] != 'keyword':
                break;

            if self.token[1] == 'let':
                self.compileLet(symbols)
                self.advanceToken()
            elif self.token[1] == 'if':
                self.compileIf(symbols)
            elif self.token[1] == 'while':
                self.compileWhile(symbols)
                self.advanceToken()
            elif self.token[1] == 'do':
                self.compileDo(symbols)
                self.advanceToken()
            elif self.token[1] == 'return':
                self.compileReturn(symbols)
                self.advanceToken()
            else:
                break;



    def compileLet(self, symbols):
        """compiles let statement of form:
        'let' varName ('[' expression ']')? '=' expression ';' """

        is_array = False

        #'let'
        self.matchToken('keyword', 'let')

        #varName
        self.advanceToken()
        self.matchToken('identifier', '')
        name = self.token[1]
        self.advanceToken()

        #('[' expression ']')?
        if self.token[0] == 'symbol' and self.token[1] == '[':
            is_array = True
            self.matchToken('symbol', '[')
            self.advanceToken()
            self.compileExpression(symbols)
            self.advanceToken()
            self.matchToken('symbol', ']')
            self.advanceToken()
            self.vcodeVariable('push', name, symbols)
            self.vcode.append('add')

        #'='
        self.matchToken('symbol', '=')

        #expression
        self.advanceToken()
        self.compileExpression(symbols)

        #;
        self.advanceToken()
        self.matchToken('symbol', ';')

        if is_array:
            self.vcode.append('pop temp 0')
            self.vcode.append('pop pointer 1')
            self.vcode.append('push temp 0')
            self.vcode.append('pop that 0')
        else:
            self.vcodeVariable('pop', name, symbols)



    def compileIf(self, parent_symbols):
        """compiles if statement of form:
        'if' '(' expression ')' '{' statements '}' ('else''{' statements '}')? """

        #'if'
        self.matchToken('keyword', 'if')

        #'('
        self.advanceToken()
        self.matchToken('symbol', '(')

        #expression
        self.advanceToken()
        self.compileExpression(parent_symbols)

        # ')'
        self.advanceToken()
        self.matchToken('symbol', ')')

        label_index = self.vcodeJump('if-goto', 'IF_TRUE', False)
        self.vcodeJump('goto', 'IF_FALSE', label_index)
        self.vcodeJump('label', 'IF_TRUE', label_index)

        # '{'
        self.advanceToken()
        self.matchToken('symbol', '{')

        symbols = SymbolTable(parent_symbols)

        # statements
        self.advanceToken()
        self.compileStatements(symbols)

        # '}'
        self.matchToken('symbol', '}')
        self.advanceToken()

        self.vcodeJump('goto', 'IF_END', label_index)
        self.vcodeJump('label', 'IF_FALSE', label_index)

        #('else''{' statements '}')?
        if self.token[1] == 'else':
            symbols = SymbolTable(parent_symbols)
            self.matchToken('keyword', 'else')
            self.advanceToken()
            self.matchToken('symbol', '{')
            self.advanceToken()
            self.compileStatements(symbols)
            self.matchToken('symbol', '}')
            self.advanceToken()

        self.vcodeJump('label', 'IF_END', label_index)

    def compileWhile(self, parent_symbols):
        """compiles while statement of form:
        'while' '(' expression ')''{' statements '}' """

        symbols = SymbolTable(parent_symbols)

        #'while'
        self.matchToken('keyword', 'while')
        label_index = self.vcodeJump('label', 'WHILE_EXP', False)

        #'('
        self.advanceToken()
        self.matchToken('symbol', '(')

        #expression
        self.advanceToken()
        self.compileExpression(symbols)

        #')'
        self.advanceToken()
        self.matchToken('symbol', ')')

        # while jump
        self.vcode.append('not')
        self.vcodeJump('if-goto', 'WHILE_END', label_index)

        # '{'
        self.advanceToken()
        self.matchToken('symbol', '{')

        #statements
        self.advanceToken()
        self.compileStatements(symbols)

        # '}'
        self.matchToken('symbol', '}')

        self.vcodeJump('goto', 'WHILE_EXP', label_index)
        self.vcodeJump('label', 'WHILE_END', label_index)

    def compileDo(self, symbols):
        """compile do statement of form:
        'do' subroutineCall ';' """

        #'do'
        self.matchToken('keyword', 'do')

        #subroutineCall
        self.advanceToken()
        self.compileTerm(False, symbols)
        # dispose of return value from stack
        self.vcode.append('pop temp 0')

        #';'
        self.advanceToken()
        self.matchToken('symbol', ';')

    def compileReturn(self, symbols):
        """compile return statement of form:
        'return' expression? ';' """


        #'return'
        self.matchToken('keyword', 'return')

        #expression? ';'
        self.advanceToken()
        if self.token[1] != ';':
            self.compileExpression(symbols)
            self.advanceToken()
        else:
            # return 0 if no return type
            self.vcode.append("push constant 0")
        self.matchToken('symbol', ';')
        self.vcode.append("return")

    def compileExpression(self, symbols):
        """compile expression of form:
        term (op term)"""

        #term
        self.compileTerm(True, symbols)

        #(op term)*
        while self.tokenizer.next_token[1] in self.OP:
            self.advanceToken()
            self.matchToken('symbol', self.OP)
            operator = self.token[1]
            self.advanceToken()
            self.compileTerm(True, symbols)
            self.vcode.append(self.OPERATOR_VCODE[operator])



    def compileTerm(self, isTerm, symbols):
        """compiles a term of form:
        integerConstant|stringConstant|keywordConstant|varName|
         varName'['expression']'|subroutineCall|'('expression')'|unaryOp term"""

        if self.token[0] in ['integerConstant', 'stringConstant']:
            self.matchToken(['integerConstant', 'stringConstant'], '')
            if self.token[0] == 'integerConstant':
                self.vcode.append('push constant ' + self.token[1])
            else:
                string_constant = self.token[1]
                self.vcode.append('push constant ' + str(len(string_constant)))
                self.vcode.append('call String.new 1')
                for c in string_constant:
                    self.vcode.append('push constant ' + str(ord(c)))
                    self.vcode.append('call String.appendChar 2')

        elif self.token[1] in self.KEYWORDCONSTANT:
            self.matchToken('keyword', self.KEYWORDCONSTANT)
            self.vcode +=self.KEYWORDCONSTANT_VCODE[self.token[1]]
        elif self.token[0] == 'identifier':
            next_token = self.tokenizer.next_token
            if next_token[1] == '[':
                #var array
                self.matchToken('identifier', '')
                name = self.token[1]
                self.advanceToken()
                self.matchToken('symbol', '[')
                self.advanceToken()
                self.compileExpression(symbols)
                self.advanceToken()
                self.matchToken('symbol', ']')
                self.vcodeVariable('push', name, symbols)
                self.vcode.append('add')
                self.vcode.append('pop pointer 1')
                self.vcode.append('push that 0')
            elif next_token[1] == '(':
                #subroutine call
                self.vcode.append('push pointer 0')
                self.matchToken('identifier', '')
                method = self.token[1]
                self.advanceToken()
                self.matchToken('symbol', '(')
                self.advanceToken()
                expression_count = self.compileExpressionList(symbols)
                self.matchToken('symbol', ')')
                self.vcode.append('call ' + self.class_name + '.' + method + ' ' + str(expression_count + 1))
            elif next_token[1] == '.':
                #subroutine call with method
                self.matchToken('identifier', '')
                object = self.token[1]
                expression_count = 0
                try:
                    symbols.typeOf(object)
                    self.vcodeVariable('push', object, symbols)
                    expression_count += 1
                except ValueError:
                    pass
                self.advanceToken()
                self.matchToken('symbol', '.')
                self.advanceToken()
                self.matchToken('identifier', '')
                method = self.token[1]
                self.advanceToken()
                self.matchToken('symbol', '(')
                self.advanceToken()
                expression_count += self.compileExpressionList(symbols)
                self.matchToken('symbol', ')')
                try:
                    self.vcode.append('call ' + symbols.typeOf(object) + "." + method + " " + str(expression_count))
                except ValueError:
                    self.vcode.append('call ' + object + "." + method + " " + str(expression_count))
            else:
                self.matchToken('identifier', '')
                self.vcodeVariable('push', self.token[1], symbols)
        elif self.token[1] == '(':
            #'('expression')'
            self.matchToken('symbol', '(')
            self.advanceToken()
            self.compileExpression(symbols)
            self.advanceToken()
            self.matchToken('symbol', ')')
        elif self.token[1] in self.UNARYOP:
            self.matchToken('symbol', self.UNARYOP)
            unary_op = self.token[1]
            self.advanceToken()
            self.compileTerm(True, symbols)
            self.vcode.append(self.UNARYOP_VCODE[unary_op])
        else:
            for i, line in enumerate(self.xml):
                print(str(i) + line)
            raise ValueError(
                'Expected term, but instead got {0} at tokenizer line {1}'.format(str(self.token),
                                                                                 str(self.tokenizer.token_index)))


    def compileExpressionList(self, symbols):
        """compile expression list of form:
        (expression(',' expression)*)?"""

        expression_count = 0

        #(expression(',' expression)*)?
        if self.token[1] != ')':
            expression_count += 1
            self.compileExpression(symbols)
            self.advanceToken()

        while self.token[1] == ',':
            self.matchToken('symbol', ',')
            self.advanceToken()
            expression_count += 1
            self.compileExpression(symbols)
            self.advanceToken()

        return expression_count



#unit testing
def main():
    input_file = "ExpressionLessSquare/SquareGame.jack"
    compilationEngine = CompilationEngine(input_file)
    i=0
    for line in compilationEngine.xml:
        i += 1
        print(line)


if __name__ == "__main__":
    main()