from JackTokenizer import JackTokenizer


class CompilationEngine:

    UNARYOP = ['-', '~']
    OP = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
    KEYWORDCONSTANT = ['true', 'false', 'null', 'this']

    def __init__(self, filename):
        self.tokenizer = JackTokenizer(filename)
        self.token = self.tokenizer.advance()
        self.xml = []
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
        self.xml.append(self.token2XML())

    def matchType(self):
        """"match type of form:
        'int'|'char'|'boolean'|className """
        if self.token[0] == 'keyword' and self.token[1] in ['int', 'char', 'boolean']:
            self.xml.append(self.token2XML())
        elif self.token[0] == 'identifier':
            self.xml.append(self.token2XML())
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

    def compileClass(self):
        """compiles class of form:
        'class' classname '{' classVarDec* subroutineDec* '}'"""

        self.xml.append('<class>')

        #'class'
        self.matchToken('keyword', 'class')

        #classname
        self.advanceToken()
        self.matchToken('identifier', '')

        #{
        self.advanceToken()
        self.matchToken('symbol', '{')

        #classVarDec*
        self.advanceToken()
        while self.token[0] == 'keyword' and self.token[1] in ['field', 'static']:
            self.compileClassVarDec()
            self.advanceToken()

        #subroutineDec*
        while self.token[0] == 'keyword' and self.token[1] in ['constructor', 'function', 'method']:
            self.compileSubroutine()
            self.advanceToken()

        #}
        self.matchToken('symbol', '}')

        self.xml.append('</class>')

    def compileClassVarDec(self):
        """compiles class variable declaration of form:
        ('static'|'field') type varName (',' varName)* ';' """

        self.xml.append('<classVarDec>')

        #('static'|'field')
        self.matchToken('keyword', ['static', 'field'])

        #type
        self.advanceToken()
        self.matchType()

        #varName
        self.advanceToken()
        self.matchToken('identifier', '')
        self.advanceToken()

        #(',' varName)*
        while self.token[1] == ',':
            self.matchToken('symbol', ',')
            self.advanceToken()
            self.matchToken('identifier', '')
            self.advanceToken()

        #';'
        self.matchToken('symbol', ';')

        self.xml.append('</classVarDec>')

    def compileSubroutine(self):
        """compiles subroutine of form:
        ('constructor'|'function'|'method') ('void'|type) subroutineName '(' parameterList ')' subroutineBody """

        self.xml.append('<subroutineDec>')

        #('constructor'|'function'|'method')
        self.matchToken('keyword', ['constructor', 'function', 'method'])

        #('void'|type)
        self.advanceToken()
        if self.token[1] == 'void':
            self.matchToken('keyword', 'void')
        else:
            self.matchType()

        #subroutineName
        self.advanceToken()
        self.matchToken('identifier', '')

        #(
        self.advanceToken()
        self.matchToken('symbol', '(')

        #parameterList
        self.advanceToken()
        self.compileParameterList()

        #)
        self.matchToken('symbol', ')')

        #subroutineBody
        self.advanceToken()
        self.compileSubroutineBody()

        self.xml.append('</subroutineDec>')

    def compileParameterList(self):
        """compiles parameterList of form:
        ((type varName) (',' type varName)*)? """

        self.xml.append('<parameterList>')

        #((type varName) (',' type varName)*)?
        if self.isType():
            self.matchType()
            self.advanceToken()
            self.matchToken('identifier', '')
            self.advanceToken()

        while self.token[1] == ',':
            self.matchToken('symbol', ',')
            self.advanceToken()
            self.matchType()
            self.advanceToken()
            self.matchToken('identifier', '')
            self.advanceToken()

        self.xml.append('</parameterList>')



    def compileSubroutineBody(self):
        """compiles subroutine body of form:
        '{' varDec* statements '}' """

        self.xml.append('<subroutineBody>')

        #{
        self.matchToken('symbol', '{')

        #varDec*
        self.advanceToken()
        while self.token[0] == 'keyword' and self.token[1] == 'var':
            self.compileVarDec()
            self.advanceToken()

        #statements
        self.compileStatements()

        #}
        self.matchToken('symbol', '}')

        self.xml.append('</subroutineBody>')

    def compileVarDec(self):
        """"compiles variable declarations of form:
        'var' type varName (',' varName)* ';' """

        self.xml.append('<varDec>')

        #'var'
        self.matchToken('keyword', 'var')

        #type
        self.advanceToken()
        self.matchType()

        #varName
        self.advanceToken()
        self.matchToken('identifier', '')
        self.advanceToken()

        # (',' varName)*
        while self.token[1] == ',':
            self.matchToken('symbol', ',')
            self.advanceToken()
            self.matchToken('identifier', '')
            self.advanceToken()

        # ';'
        self.matchToken('symbol', ';')

        self.xml.append('</varDec>')

    def compileStatements(self):
        """compiles statements of form:
        statement*
        statement are of form:
        letStatement|ifStatement|whileStatement|doStatement|returnStatement """

        self.xml.append('<statements>')

        #statements*
        while(True):
            if self.token[0] != 'keyword':
                break;

            if self.token[1] == 'let':
                self.compileLet()
                self.advanceToken()
            elif self.token[1] == 'if':
                self.compileIf()
            elif self.token[1] == 'while':
                self.compileWhile()
                self.advanceToken()
            elif self.token[1] == 'do':
                self.compileDo()
                self.advanceToken()
            elif self.token[1] == 'return':
                self.compileReturn()
                self.advanceToken()
            else:
                break;



        self.xml.append('</statements>')

    def compileLet(self):
        """compiles let statement of form:
        'let' varName ('[' expression ']')? '=' expression ';' """

        self.xml.append('<letStatement>')

        #'let'
        self.matchToken('keyword', 'let')

        #varName
        self.advanceToken()
        self.matchToken('identifier', '')
        self.advanceToken()

        #('[' expression ']')?
        if self.token[0] == 'symbol' and self.token[1] == '[':
            self.matchToken('symbol', '[')
            self.advanceToken()
            self.compileExpression()
            self.advanceToken()
            self.matchToken('symbol', ']')
            self.advanceToken()

        #'='
        self.matchToken('symbol', '=')

        #expression
        self.advanceToken()
        self.compileExpression()

        #;
        self.advanceToken()
        self.matchToken('symbol', ';')

        self.xml.append('</letStatement>')

    def compileIf(self):
        """compiles if statement of form:
        'if' '(' expression ')' '{' statements '}' ('else''{' statements '}')? """

        self.xml.append('<ifStatement>')

        #'if'
        self.matchToken('keyword', 'if')

        #'('
        self.advanceToken()
        self.matchToken('symbol', '(')

        #expression
        self.advanceToken()
        self.compileExpression()

        # ')'
        self.advanceToken()
        self.matchToken('symbol', ')')

        # '{'
        self.advanceToken()
        self.matchToken('symbol', '{')

        # statements
        self.advanceToken()
        self.compileStatements()

        # '}'
        self.matchToken('symbol', '}')
        self.advanceToken()

        #('else''{' statements '}')?
        if self.token[1] == 'else':
            self.matchToken('keyword', 'else')
            self.advanceToken()
            self.matchToken('symbol', '{')
            self.advanceToken()
            self.compileStatements()
            self.matchToken('symbol', '}')
            self.advanceToken()

        self.xml.append('</ifStatement>')

    def compileWhile(self):
        """compiles while statement of form:
        'while' '(' expression ')''{' statements '}' """

        self.xml.append('<whileStatement>')

        #'while'
        self.matchToken('keyword', 'while')

        #'('
        self.advanceToken()
        self.matchToken('symbol', '(')

        #expression
        self.advanceToken()
        self.compileExpression()

        #')'
        self.advanceToken()
        self.matchToken('symbol', ')')

        # '{'
        self.advanceToken()
        self.matchToken('symbol', '{')

        #statements
        self.advanceToken()
        self.compileStatements()

        # '}'
        self.matchToken('symbol', '}')

        self.xml.append('</whileStatement>')

    def compileDo(self):
        """compile do statement of form:
        'do' subroutineCall ';' """

        self.xml.append('<doStatement>')

        #'do'
        self.matchToken('keyword', 'do')

        #subroutineCall
        self.advanceToken()
        self.compileTerm(False)

        #';'
        self.advanceToken()
        self.matchToken('symbol', ';')

        self.xml.append('</doStatement>')

    def compileReturn(self):
        """compile return statement of form:
        'return' expression? ';' """

        self.xml.append('<returnStatement>')

        #'return'
        self.matchToken('keyword', 'return')

        #expression? ';'
        self.advanceToken()
        if self.token[1] != ';':
            self.compileExpression()
            self.advanceToken()
        self.matchToken('symbol', ';')

        self.xml.append('</returnStatement>')

    def compileExpression(self):
        """compile expression of form:
        term (op term)"""

        self.xml.append('<expression>')

        #term
        self.compileTerm(True)

        #(op term)*
        while self.tokenizer.next_token[1] in self.OP:
            self.advanceToken()
            self.matchToken('symbol', self.OP)
            self.advanceToken()
            self.compileTerm(True)

        self.xml.append('</expression>')

    def compileTerm(self, isTerm):
        """compiles a term of form:
        integerConstant|stringConstant|keywordConstant|varName|
         varName'['expression']'|subroutineCall|'('expression')'|unaryOp term"""

        if isTerm:
            self.xml.append('<term>')

        if self.token[0] in ['integerConstant', 'stringConstant']:
            self.matchToken(['integerConstant', 'stringConstant'], '')
        elif self.token[1] in self.KEYWORDCONSTANT:
            self.matchToken('keyword', self.KEYWORDCONSTANT)
        elif self.token[0] == 'identifier':
            next_token = self.tokenizer.next_token
            if next_token[1] == '[':
                #var array
                self.matchToken('identifier', '')
                self.advanceToken()
                self.matchToken('symbol', '[')
                self.advanceToken()
                self.compileExpression()
                self.advanceToken()
                self.matchToken('symbol', ']')
            elif next_token[1] == '(':
                #subroutine call
                self.matchToken('identifier', '')
                self.advanceToken()
                self.matchToken('symbol', '(')
                self.advanceToken()
                self.compileExpressionList()
                self.matchToken('symbol', ')')
            elif next_token[1] == '.':
                #subroutine call with method
                self.matchToken('identifier', '')
                self.advanceToken()
                self.matchToken('symbol', '.')
                self.advanceToken()
                self.matchToken('identifier', '')
                self.advanceToken()
                self.matchToken('symbol', '(')
                self.advanceToken()
                self.compileExpressionList()
                self.matchToken('symbol', ')')
            else:
                self.matchToken('identifier', '')
        elif self.token[1] == '(':
            #'('expression')'
            self.matchToken('symbol', '(')
            self.advanceToken()
            self.compileExpression()
            self.advanceToken()
            self.matchToken('symbol', ')')
        elif self.token[1] in self.UNARYOP:
            self.matchToken('symbol', self.UNARYOP)
            self.advanceToken()
            self.compileTerm(True)
        else:
            for i, line in enumerate(self.xml):
                print(str(i) + line)
            raise ValueError(
                'Expected term, but instead got {0} at tokenizer line {1}'.format(str(self.token),
                                                                                 str(self.tokenizer.token_index)))

        if isTerm:
            self.xml.append('</term>')


    def compileExpressionList(self):
        """compile expression list of form:
        (expression(',' expression)*)?"""

        self.xml.append('<expressionList>')

        #(expression(',' expression)*)?
        if self.token[1] != ')':
            self.compileExpression()
            self.advanceToken()

        while self.token[1] == ',':
            self.matchToken('symbol', ',')
            self.advanceToken()
            self.compileExpression()
            self.advanceToken()

        self.xml.append('</expressionList>')



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