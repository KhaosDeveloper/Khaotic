'''

██╗  ██╗██╗  ██╗ █████╗  ██████╗ ████████╗██╗ ██████╗
██║ ██╔╝██║  ██║██╔══██╗██╔═══██╗╚══██╔══╝██║██╔════╝
█████╔╝ ███████║███████║██║   ██║   ██║   ██║██║
██╔═██╗ ██╔══██║██╔══██║██║   ██║   ██║   ██║██║
██║  ██╗██║  ██║██║  ██║╚██████╔╝   ██║   ██║╚██████╗
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝
 █ █ █▀▀ █▀█ █▀ █ █▀█ █▄ █ ▄█   ▄█
 ▀▄▀ ██▄ █▀▄ ▄█ █ █▄█ █ ▀█  █ ▄  █

RELEASED: 2/1
LAST UPDATED: 2/1

CHANGES:
- Full lexer upgrade containing conditions, arithmitic, and other functions.
- Conditional parser
- Added strings (must be declared using " ", only useful when lexed/parsed)

'''

class Token: # Lexer and parser started at 1:48 PM, 1/4. Full lexer and parser done at 4:18 PM, 2/1.
    def __init__(self, type, value):
        self.type = type
        self.value = value
class Variable:
    def __init__(self, name, value):
        self.name = name
        self.value = value

def fullLexer(text):
    tokens = []
    number = ''
    modText = text.replace(" ", "")
    modText = modText + " "
    x = 0
    while x in range (len(modText)):
        if modText[x] == '"':
            x += 1
            while modText[x] != '"':
                number += modText[x]
                x += 1
            else:
                if number != '':
                    tokens.append(Token('string', number))
                number = ''
        if modText[x].isdigit() or modText[x] == '.':
            number += modText[x]
        else:
            if number != '':
                tokens.append(Token('number', number))
            number = ''
        if modText[x] in ['>', '<', '=', '!'] and modText[x + 1] == '=':
            tokens.append(Token('operator', modText[x:x + 2]))
            x += 1
        elif modText[x] in ['>', '<', '=']:
            tokens.append(Token('operator', modText[x]))
        elif modText[x:x + 3] == 'and':
            x += 2
            tokens.append(Token('condition', 'and'))
        elif modText[x:x + 2] == 'or':
            tokens.append(Token('condition', 'or'))
            x += 1
        elif modText[x:x + 3] == 'not':
            tokens.append(Token('condition', 'not'))
            x += 2
        if modText[x] in ['+', '-', '*', '/', '%']:
            tokens.append(Token('operator', modText[x]))
        if modText[x] == '(':
            tokens.append(Token('leftPara', modText[x]))
        if modText[x] == ')':
            tokens.append(Token('rightPara', modText[x]))
        x += 1 # Increment
    return tokens

def parse(tokens):
    currentToken = 0
    def nextToken():
        nonlocal currentToken
        if currentToken < len(tokens):
            return tokens[currentToken]
        return Token('EOF', None)
    def factor():
        nonlocal currentToken
        token = nextToken()
        if token.type == 'number':
            currentToken += 1
            return float(token.value)
        elif token.type == 'leftPara':
            currentToken += 1
            result = expr()
            if tokens[currentToken].type != 'rightPara':
                raise ValueError("no closing parenthesis")
            currentToken += 1
            return result
    def term():
        nonlocal currentToken
        result = factor()
        while nextToken().type in ['operator', 'number', 'leftPara']:
            if nextToken().type == 'operator' and nextToken().value in ['*', '/', '%']:
                operator = nextToken().value
                currentToken += 1
                operand = factor()
                if operator == '*':
                    result *= operand
                elif operator == '/':
                    if operand == 0:
                        raise ZeroDivisionError("D")
                    result /= operand
                elif operator == '%':
                    result %= operand
            else:
                break
        return result
    def expr():
        nonlocal currentToken
        result = term()
        while nextToken().type in ['operator', 'number', 'leftPara']:
            if nextToken().type == 'operator' and nextToken().value in ['+', '-']:
                operator = nextToken().value
                currentToken += 1
                operand = term()
                if operator == '+':
                    result += operand
                elif operator == '-':
                    result -= operand
            else:
                break
        return result
    return expr() # Whole lexer and parser done at 7:51 PM, 1/4 (Actually completed at 5:25 PM on 1/6)

def conParse(tokens):
    currentToken = 0
    def nextToken():
        nonlocal currentToken
        if currentToken < len(tokens):
            return tokens[currentToken]
        return Token('EOF', None)
    def factor():
        nonlocal currentToken
        token = nextToken()
        if token.type == 'number':
            currentToken += 1
            return float(token.value)
        if token.type == 'string':
            currentToken += 1
            return str(token.value)
        elif token.type == 'condition' and token.value == 'not':
            currentToken += 1
            return not factor()
        elif token.type == 'leftPara':
            currentToken += 1
            result = condition()
            if tokens[currentToken].type != 'rightPara':
                raise ValueError("no closing parenthesis")
            currentToken += 1
            return result
    def compare():
        nonlocal currentToken
        a = factor()
        while nextToken().type in ['operator', 'number', 'string']:
            if nextToken().type == 'operator':
                operation = nextToken().value
                currentToken += 1
                b = factor()
                if operation == '==':
                    a = a == b
                elif operation == '!=':
                    a = a != b
                elif operation == '<=':
                    a = float(a) <= float(b)
                elif operation == '>=':
                    a = float(a) >= float(b)
                elif operation == '<':
                    a = float(a) < float(b)
                elif operation == '>':
                    a = float(a) > float(b)
            else:
                break
        return a
    def condition():
        nonlocal currentToken
        a = compare()
        while nextToken().type == 'condition':
            if nextToken().value in ['and', 'or']:
                operation = nextToken().value
                currentToken += 1
                b = compare()
                if operation == 'and':
                    a = a and b
                elif operation == 'or':
                    a = a or b
            else:
                break
        return a
    return condition() # Starts chain event

def solver(text): # Add the variable translations.
    text = text.replace(" ", "")
    a = 0
    b = 0
    while a in range(len(text)):
        while text[a] == '@':
            while text[b] in ['+', '-', '*', '/', '%', '(', ')']:
                varName = text[a+1:b]
                varValue = searchVar(varName)
                text = text.replace(text[a:b], str(varValue))
                b = a
            else:
                if b == len(text) - 1:
                    varName = text[a+1:]
                    varValue = searchVar(varName)
                    text = text.replace(text[a:], str(varValue))
                    b = a
                else:
                    b += 1
        else:
            a += 1
            b = a
    tokens = fullLexer(text)
    result = parse(tokens)
    return result

def conditionSetup(text):
    text = text.replace(" ", "")
    a = 0
    b = 0
    while a in range(len(text)):
        while text[a] == '@':
            while text[b] in ['=', '!', '>', '<', 'and', 'or', 'not', '(', ')']:
                varName = text[a+1:b]
                varValue = searchVar(varName)
                if any(not char.isdigit() for char in text[a:b]):
                    text = text.replace(text[a:b], '"' + str(varValue) + '"')
                else:
                    text = text.replace(text[a:b], str(varValue))
                b = a
            else:
                if b == len(text) - 1:
                    varName = text[a+1:]
                    varValue = searchVar(varName)
                    text = text.replace(text[a:], str(varValue))
                    b = a
                else:
                    b += 1
        else:
            a += 1
            b = a
    tokens = fullLexer(text)
    result = conParse(tokens)
    return result

def searchVar(varName): # Searches by name and returns the value
    for i in range(len(variableMemory)):
      if variableMemory[i].name == varName:
          return variableMemory[i].value

def forceExit():
    exit()

running = True
lastAddress = 0
ifCheck = False
while running:
    print()
    print("\nKHAOTIC 1.1")
    program = input('> ') # Interpreter/AST?
    variableMemory = []
    returnAddrs = []
    commands = program.split(';')
    x = 0
    for i in range(len(commands)):
        if commands[i] == '<start':
            x = i
            continue
        if commands[i] == "" or " ":
            commands.pop(-1)
            commands.append("exit")
    while x in range(len(commands) - 1):
        if commands[x][0] == '^' and commands[x][1] == '"':  # Print string
            if commands[x][-4:-1] == '/nl': # Will make new line "/nl"
                print(commands[x][2:-4])
            else:
                print(commands[x][2:-1], end='')
        elif commands[x][0] == '^' and commands[x][1] == '@':  # Print var
            print(searchVar(commands[x][2:]), end='')
        elif commands[x][0] == '^' and commands[x][1] == '(':  # Print equation
            equation = commands[x][2:]
            print(solver(equation), end='')
        elif commands[x][0] == '@':  # Declaring variables
            y = commands[x].split('=')
            varName = y[0][1:]
            varName = varName.replace(" ", "")
            varValue = y[1]
            varValue = varValue.replace(" ", "")
            if varValue[0] == '@':  # From other variable
                variableMemory.insert(0, Variable(varName, searchVar(y[1][1:])))
            elif varValue[0] == '(':  # From equation
                equation = varValue[1:-1]
                varValue = solver(equation)
                variableMemory.insert(0, Variable(varName, varValue))
            else:  # From direct input
                if varValue[0] == '"':
                    varValue = varValue[1:-1]
                variableMemory.insert(0, Variable(varName, varValue)) # Done at 11:51, 1/4
        elif commands[x][0] == 'v':  # Getting input, destination specified
            varName = commands[x][2:]
            varValue = input()
            variableMemory.insert(0, Variable(varName, varValue))
        elif commands[x][0] == '>': # Go to a label
            destination = commands[x][1:]
            if destination  == 'return': # Return check
                x = returnAddrs.pop(-1)
            else:
                for z in range(len(commands)-1):
                    if commands[z][0] == '<':
                        varName = commands[z][1:]
                        if varName == destination:
                            returnAddrs.append(x)
                            lastAddress = x
                            x = z
                            break
                continue
        elif commands[x][0] == '?': # If statement (WILL BE TURING COMPLETE)
            sCond = commands[x].find('(')
            eCond = commands[x].rfind(')', 0, commands[x].rfind(')'))
            cond = commands[x][sCond + 1:eCond]
            dest = commands[x][eCond + 2:-1]
            if conditionSetup(cond):
                ifCheck = True
                commands.insert(x + 1, dest)
                lastAddress = x
                x+=1
                continue
        elif commands[x][0] == '!': # System commands
            if commands[x][1] == 'q': # Quit
                running = False
            elif commands[x][1] == 'o':
              file = open(input("path: "),"r")
              program = file.read().replace('\n', '')
              variableMemory = []
              returnAddrs = []
              commands = program.split(';')
              x = 0
              for i in range(len(commands)):
                if commands[i] == '<start':
                  x = i
                  continue
                if commands[i] == "" or " ":
                  commands.pop(-1)
                  commands.append("exit")
        if ifCheck:
              commands.pop(lastAddress)
              ifCheck = False
        lastAddress = x
        # print("last address:", lastAddress)
        x+=1 # Last line in main loop

# COMMANDS:
# ^output; (/nl for new line)
# v@input;
# @variable;
# <label;
# >goto;
# >return; (returns to the last goto + 1)
# ?if(condition){statement};
# ! for system commands (!q; to quit, !o; to open and run a file)

# PROGRAMS:

# The first program (calculator):
# <start;^"Enter first number: ";v@num1;^"Enter second number: ";v@num2;^"Enter operator (+, -, *, /, %): ";v@op;^"Result: ";?(@op == "+"){^(@num1+@num2)};?(@op == "-"){^(@num1-@num2)};?(@op == "*"){^(@num1*@num2)};?(@op == "/"){^(@num1/@num2)};?(@op == "%"){^(@num1/@num2)};!q;

# Fibonacci:
# <start;^"To term?: ";v@terms;@n1=0;@n2=1;@nth=0;@count=0;^"Count: ";^"Number/nl";<loop;^@count;^": ";^@n1;^"/nl";@nth=(@n1 + @n2);@n1=@n2;@n2=@nth;@count=(@count + 1);?(@count>@terms){>end};>loop;<end;^"Finished. ";!q;

# Geometric Sequence:
# <start;^"To term?: ";v@terms;@num=1;@count=0;^"Count: ";^"Number/nl";<loop;^@count;^": ";^@num;^"/nl";@num=(@num + @num);@count=(@count + 1);?(@count>@terms){>end};>loop;<end;^"Finished. ";!q;

# Counting to 10:
# <start;@x=1;<loop;^@x;^"/nl";@x=(@x + 1);?(@x > 10){>end};>loop;<end;^"Finished";
