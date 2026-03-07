'''

██╗  ██╗██╗  ██╗ █████╗  ██████╗ ████████╗██╗ ██████╗
██║ ██╔╝██║  ██║██╔══██╗██╔═══██╗╚══██╔══╝██║██╔════╝
█████╔╝ ███████║███████║██║   ██║   ██║   ██║██║
██╔═██╗ ██╔══██║██╔══██║██║   ██║   ██║   ██║██║
██║  ██╗██║  ██║██║  ██║╚██████╔╝   ██║   ██║╚██████╗
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝
 █ █ █▀▀ █▀█ █▀ █ █▀█ █▄ █    ▀█   █▀█
 ▀▄▀ ██▄ █▀▄ ▄█ █ █▄█ █ ▀█    █▄ ▄ █▄█

CREATED: 2/6/2026 --- Exactly 2 years after version 1.2

FEATURES:
- Combined full lexer and parser.
- Number, String, and Boolean data types. 
- Very basic standard Library
- System/shell commands
- External command line interface

CHANGES: 
- Combined AST
- Combined setup and setupNoParse into lexer
- Break character for new lines, tabs, and quotes               
- Updated variable memory to be a dictionary for O(1)           
- Removed text editor
- QOL Changes

NOTE: A lot of these changes were supposed to be in the final version 
for the fair but since time was short I had to do what I could. 
'''

import os
import os.path
import argparse
import sys
import time
import random as ran

# =============
# == CLASSES ==
# =============

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

# =============
# === LEXER ===
# =============

def fullLexer(text, v_mem):
    tokens = []
    buffer = ''
    text = text + " "
    x = 0
    while x in range (len(text)):
        if text[x] == ' ' and buffer == '':
            x += 1
            continue
        elif text[x] == '"' and text[x-1] != '\\':      # BREAK CHARACTERS : CHECK FIRST
            x += 1
            while True:
                if text[x] == '\\':             # Trigger break character (\)
                    x += 1
                    if text[x] == 'n':          # New line
                        buffer += '\n'
                    elif text[x] == 't':          # Tab
                        buffer += '\t'
                    else:
                        buffer += text[x]
                    x += 1
                elif text[x] == '\"':           # Trigger string end
                    break
                else:
                    buffer += text[x]
                    x += 1
            if buffer != '':
                tokens.append(Token('string', buffer))
                buffer = ''
        elif text[x] == '@':
            varLoop = True
            x += 1
            start_x = x
            while varLoop:
                if text[x].isalnum() or text == '_':
                    buffer += text[x]
                    x += 1
                else:
                    text = text.replace("@" + buffer, str(v_mem[buffer]))
                    x = start_x - 1
                    buffer = ''
                    varLoop = False
        elif text[x] == ':':
            # NOTE: Avoid using .count(), as it's an O(n) algorithm that
            # would run everytime we check the '(' or ')' counts. 
            para_layer = 0  # Using this instead to track the nested layer we are in. 
            start_x = x
            x += 1
            while text[x] != ')' or para_layer == 0:       # Should we add to buffer? True
                if text[x] == '(': para_layer += 1
                elif text[x] == ')': para_layer -= 1
                buffer += text[x]
                x += 1
            buffer += ")"
            stdtest = standardLib(buffer, v_mem)
            text = text.replace(":" + buffer, str(stdtest))
            x = start_x - 1
            buffer = ''
        if text[x].isdigit() or text[x] == '.':
            buffer += text[x]
        elif text[x] == '-' and (text[x+1].isdigit() or text[x+1] == '.'):
            if buffer == '':
                buffer = '-'
                x += 1
                continue
            if buffer != '':        # NOTE: Fixes bug
                tokens.append(Token('number', buffer))
                buffer = ''
        else:
            if buffer != '':
                tokens.append(Token('number', buffer))
            buffer = ''
        if text[x] in ['>', '<', '=', '!'] and text[x + 1] == '=':
            tokens.append(Token('operator', text[x:x + 2]))
            x += 1
        elif text[x] in ['>', '<', '=']:
            tokens.append(Token('operator', text[x]))
        elif text[x:x + 2] == '**':
            tokens.append(Token('operator', '**'))
            x += 1
        elif text[x] in ['+', '-', '*', '/', '%']:
            tokens.append(Token('operator', text[x]))
        elif text[x:x + 3] == 'and':
            x += 2
            tokens.append(Token('condition', 'and'))
        elif text[x:x + 2] == 'or':
            tokens.append(Token('condition', 'or'))
            x += 1
        elif text[x:x + 3] == 'not':
            tokens.append(Token('condition', 'not'))
            x += 2
        elif text[x:x + 4] == 'True':
            tokens.append(Token('boolean', True))
            x += 3
        elif text[x:x + 5] == 'False':
            tokens.append(Token('boolean', False))
            x += 4
        elif text[x] == '(':
            tokens.append(Token('leftPara', text[x]))
        elif text[x] == ')':
            tokens.append(Token('rightPara', text[x]))
        x += 1 # Increment
    return tokens

# ==============
# === PARSER ===
# ==============

def fullParser(tokens):
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
        if token.type == 'boolean':
            currentToken += 1
            return bool(token.value)
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
    def expo():
        nonlocal currentToken
        result = factor()
        while nextToken().type in ['operator', 'number', 'leftPara']:
            if nextToken().type == 'operator' and nextToken().value == '**':
                operator = nextToken().value
                currentToken += 1
                operand = factor()
                if operator == '**':
                    x = result
                    y = 1
                    while y < operand:
                      result *= x
                      y += 1
            else:
                break
        return result
    def term():
        nonlocal currentToken
        result = expo()
        while nextToken().type in ['operator', 'number', 'leftPara']:
            if nextToken().type == 'operator' and nextToken().value in ['*', '/', '%']:
                operator = nextToken().value
                currentToken += 1
                operand = expo()
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
                    if type(result) == float and type(operand) == str:
                        result = str(result) + operand
                    elif type(result) == str and type(operand) == float:
                        result += str(operand)
                    else:
                        result += operand
                elif operator == '-':
                    result -= operand
            else:
                break
        return result
    def compare():
        nonlocal currentToken
        a = expr()
        while nextToken().type in ['operator', 'number', 'string']:
            if nextToken().type == 'operator':
                operation = nextToken().value
                currentToken += 1
                b = expr()
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

# ======================
# === ERROR HANDLING ===
# ======================
def throw_warning(line_num, message):
    header = f"\x1b[33m\x1b[1m[WARNING] [LINE {line_num}] "
    print(header + "\x1b[0m" + message)

def throw_error(line_num, message):
    header = f"\x1b[31m\x1b[1m[ERROR] [LINE {line_num}] "
    print(header + "\x1b[0m" + message)
    forceExit()

# ========================
# === STANDARD LIBRARY ===
# ========================

# NOTE: This whole standard library is quite bad and needs to be re-done, but at
# the moment, it works so I will take it. I'd eventually like to do something where
# the lexer actually submits the function name and args as a list, this way the string
# only gets looped through once. This would require heavy lexer modification however. 

def standardLib(text, v_mem):
  def absoluteValue(a):
    a = str(setup(a, v_mem))
    b = a + '/' + '-1'
    if setup(a + '>=' + '0', v_mem):
      return a
    else:
      return setup(b, v_mem)
  def round(a):
    a = str(setup(a, v_mem))
    b = setup(a + '%' + '1', v_mem)
    if setup(str(b) + '<' + '0.5', v_mem):
      return setup(a + '-' + str(b), v_mem)
    else:
      return setup(a + '+' + '('+ '1' + '-' + str(b) + ')', v_mem)
  def getChar(args):  # (string[index])
    str = setup(args[0 : args.rfind('[')], v_mem)
    index = setup(args[args.rfind('[') + 1:args.rfind(']')], v_mem)
    return '"' + str[int(float(index))] + '"'
  def setChar(args):  # (string[index], char)
    tokens = setup(args + ')', v_mem, parse=False)
    string = tokens[0].value   # args[args.find('"') + 1 : args.find('"', args.find('"') + 1)]
    index = tokens[1].value    # args[args.find('[', args.find('"', args.find('"') + 1)) + 1 : args.find(']', args.find('[', args.find('"', args.find('"') + 1)) + 1)]
    char = tokens[2].value     # args[-1]
    string2 = ''
    for x in range(len(string)):   # NOTE: Strings are immutable in python, which may be quite possibly the dumbest thing I've ever heard.
        if x == int(index):
            string2 += char
        else:
            string2 += string[x]
    return '"' + string2 + '"'
  def getLen(args):
    s = str(setup(args, v_mem))
    x = 0
    for char in s:
        x += 1
    return x
  def fileLines(args):
      tokens = setup(args, v_mem, parse=False)
      file = tokens[0].value
      with open(file, 'r') as f:
          lines = f.readlines()
      return len(lines)
  def readFile(args):  # ("file.txt[index]") FILE NEEDS QUOTES AROUND IT
      tokens = setup(args, v_mem, parse=False)
      file = tokens[0].value
      index = tokens[1].value
      with open(file, 'r') as f:
          lines = f.readlines()
      string = '"' + lines[int(index) - 1] + '"'
      string = string.replace("\n", "")
      return string
  def writeFile(args):  # ("file.txt"[index], "Text") FILE NEEDS QUOTES AROUND IT.
      tokens = setup(args, v_mem, parse=False)
      file = tokens[0].value
      index = tokens[1].value
      text = tokens[2].value
      with open(file, 'r') as f:
        lines = f.readlines()
      del lines[int(index) - 1]
      lines.insert(int(index) - 1, text + '\n')
      with open(file, 'w') as f:
        f.writelines(lines)
      return
  def delay(args):
      tokens = setup(args, v_mem, parse=False)
      wait = tokens[0].value
      time.sleep(float(wait))
      return
  def random(args):
      tokens = setup(args, v_mem, parse=False)
      min = tokens[0].value
      max = tokens[1].value
      return ran.randrange(int(min), int(max))

  start = text.find('(')
  end = text.rfind(')')
  args = text[start + 1:end]
  if text[0:start] == 'abs':
    return absoluteValue(args)
  elif text[0:start] == 'round':
    return round(args)
  elif text[0:start] == 'getChar':
    return getChar(args)
  elif text[0:start] == 'setChar':
    return setChar(args)
  elif text[0:start] == 'getLen':
    return getLen(args)
  elif text[0:start] == 'fileLines':
    return fileLines(args)
  elif text[0:start] == 'readFile':
    return readFile(args)
  elif text[0:start] == 'writeFile':
    return writeFile(args)
  elif text[0:start] == 'delay':
    return delay(args)
  elif text[0:start] == 'random':
    return random(args)

# =================
# === FUNCTIONS ===
# =================

def setup(text, v_mem, parse=True):     # TODO: Scrap this shit
    tokens = fullLexer(text, v_mem)     # (eventually, right now just use it for lexing/parsing)
    if len(tokens) == 1:
      return tokens[0].value
    elif parse == False:
      return tokens
    else:
      result = fullParser(tokens)
      return result

def forceExit():
    exit()

# ===========
# === AST ===
# ===========

def AST(loop, v_mem, name=""):
    running = True
    lastAddress = 0
    ifCheck = False
    khaotic = '''====================
=== KHAOTIC V2.0 ===
====================
"!h;" for help.'''
    help = '''
Welcome to Khaotic, a minimalistic coding language. Here's a few basic tips and commands to get you started:
- Remember to end each line with a ";".
- You only have to implicitly state strings like "this".
- New lines in files are ignored by the interpreter.
- After a semicolon, DO NOT use the space character, as the first character is crucial for the command type. (i.e: ^"hello"; ^"This command will be ignored because the "^" was not the first character";).
- The directory is directly relative to where the .exe for the interpreter is.

COMMANDS:
"^" to print.
"@name" to declare or reference a variable.
"v@name" to save user input into a variable.
"<name" defines a label (<label1;<label2;). Use "<start" to define the start of your program or it will start at the first line.
">name" jumps to the label specified. ">return" jumps to the last place a jump command was called.
"?(condition){statement}" executes the statement if the condition is True.
":(args)" are for built in functions like ":abs(num)" will return the absolute value of the number specified.

SYSTEM COMMANDS:
"!q;" to quit.
"!h;" for help.
"!p;" to change path.
"!r;" to run a file.
"!n;" to make a new file.
"!c;" to clear terminal.
"!l;" to list all .kha files in current directory.
"!d;" to dissect/debug a program.
'''

    if os.getcwd() == '/content':
        path = os.getcwd() + '/'
    else:
        path = os.getcwd() + '\\'
    if loop == True:
        print(khaotic)
        print("Current directory: " + path + '\n')
    while running:
        if loop == True:
            program = input(">>> ") # Interpreter/AST?
        else:
            file = open(name,"r")
            program = file.read().replace('\n', '')
        variableMemory = v_mem
        returnAddrs = []
        commands = program.split(';')
        x = 0
        for i in range(len(commands)):
            if commands[i] == '<start':
                x = i
                continue
        commands.pop(-1)
        commands.append("exit")
        while x in range(len(commands) - 1):
            if commands[x][0] == '<':
                x += 1
                continue
            if commands[x][0] == '^':  # Printing
                if commands[x][1] == '^':  # Print new line
                    print(setup(commands[x][2:], variableMemory))
                else:
                    print(setup(commands[x][1:], variableMemory), end='')
            elif commands[x][0] == '@':  # Declaring variables
                y = commands[x].find('=')
                varName = commands[x][1:y]
                varName = varName.replace(" ", "")
                varValue = commands[x][y+1:]
                varValue = setup(varValue, variableMemory)
                variableMemory[varName] = varValue
            elif commands[x][0] == 'v':  # Getting input, destination specified
                varName = commands[x][2:]
                for v in range(len(variableMemory)):
                    if variableMemory[v].name == varName:
                        variableMemory.pop(v)
                        break
                variableMemory[varName] = input()
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
                                x = z + 1
                                break
                    if ifCheck:
                        commands.pop(lastAddress)
                        ifCheck = False
                        x-=1
                    continue
            elif commands[x][0] == ':': # Built-in Function
                setup(commands[x])
            elif commands[x][0] == '?': # If statement (WILL BE TURING COMPLETE)
                sCond = commands[x].find('(')
                eCond = commands[x].rfind('{') - 1
                cond = commands[x][sCond + 1:eCond]
                dest = commands[x][eCond + 2:-1]
                if setup(cond, variableMemory):
                    ifCheck = True
                    commands.insert(x + 1, dest)
                    lastAddress = x
                    x+=1
                    continue
            elif commands[x][0] == '!': # System commands
                if commands[x][1] == 'q': # Quit
                    running = False
                elif commands[x][1] == 'h': # Help
                    print(help)
                elif commands[x][1] == 'p': # Set path
                    temppath = str(input("Path: "))
                    if not temppath.endswith('\\'):
                        temppath = temppath + '\\'
                    if os.path.exists(temppath):
                        path = temppath
                        print("Current directory: " + path)
                    else:
                        print("ERROR: Invalid path")
                elif commands[x][1] == 'l': # List
                    for f in os.listdir(path):
                        if f.endswith(".kha"):
                            print(f)
                elif commands[x][1] == 'c': # Clear
                    os.system('cls' if os.name == 'nt' else 'clear')
                elif commands[x][1] == 'n': # New file
                    name = str(input("File name: ") + '.kha')
                    if os.path.exists(path + name):
                        print("File", path + name, "already exists")
                    else:
                        file = open(path + name, 'x')
                        file.close()
                        print("File", path + name, "created.")
                elif commands[x][1] == 'r': # Run a file
                    name = input("File name: ")
                    if os.path.exists(path + name):
                        file = open(path + name,"r")
                        program = file.read().replace('\n', '')
                        ifCheck = False
                        variableMemory = []
                        returnAddrs = []
                        commands = program.split(';')
                        x = -1
                        for i in range(len(commands)):
                            if commands[i] == '<start':
                                x = i
                                continue
                        commands.pop(-1)
                        commands.append("exit")
                        file.close()
                    else:
                        print("ERROR: Invalid path or file name")
                elif commands[x][1] == 'd': # Dissect input
                    name = input("Insert path to file or direct input: ")
                    if os.path.exists(path + name):
                        file = open(path + name,"r")
                        program = file.read().replace('\n', '')
                        commands = program.split(';')
                        file.close()
                    else:
                        program = name
                        commands = program.split(';')
                    print()
                    print('Full Program:', program)
                    print('Index : Command : Keyword : Argument')
                    for i in range(len(commands)):
                        keyword = None
                        argument = None
                        if commands[i] == '':
                            break
                        if commands[i][0] == '^':
                            if commands[i][1] == '^':
                                keyword = 'Print new line'
                                argument = commands[i][2:]
                            else:
                                keyword = 'Print'
                                argument = commands[i][1:]
                        elif commands[i][0] == '@':
                            keyword = 'Variable'
                            argument = commands[i][1:]
                        elif commands[i][0] == 'v':
                            keyword = 'Input'
                            argument = commands[i][1:]
                        elif commands[i][0] == '<':
                            keyword = 'Label'
                            argument = commands[i][1:]
                        elif commands[i][0] == '>':
                            keyword = 'Jump/Goto'
                            argument = commands[i][1:]
                        elif commands[i][0] == '?':
                            keyword = 'If statement'
                            argument = commands[i][1:]
                        elif commands[i][0] == '!':
                            keyword = 'System'
                            argument = commands[i][1:]
                        elif commands[i][0] == ':':
                            keyword = 'Standard Function'
                            argument = commands[i][1:]
                        else:
                            keyword = 'Unknown Command'
                            argument = commands[i][1:]
                        print(i, ':', commands[i], ':', keyword, ':' ,argument)
                    commands = []
            else:
                throw_error(x, f"Invalid command '{commands[x][0]}'")
            if ifCheck:
                commands.pop(x)
                ifCheck = False
                x-=1
            lastAddress = x
            x+=1 # Last line in main loop
        else:
            print()
            if loop == False: sys.exit()
            ifCheck = False

# ==================
# === MAIN START ===
# ==================

running = True
variableMemory: dict[str, str] = {}
returnAddrs: list[int] = []
def launch():
    print("Launching Khaotic...")
    os.system('cls' if os.name == 'nt' else 'clear')
    AST(True)
def version():
    print("Khaotic Version 2.0")
    sys.exit()

def main():
    parser = argparse.ArgumentParser(description="Khaotic Application")
    parser.add_argument("--launch", action="store_true", help="Launch the application")
    parser.add_argument("--version", action="store_true", help="Print the version")
    parser.add_argument("--run", metavar="FILE", help="Run the application with a specified file")

    args = parser.parse_args()

    if args.launch:
        launch()
    elif args.version:
        version()
    elif args.run:
        AST(False, variableMemory, name=args.run)
    else:
        print("Invalid command. Use --help for more info.")
        # vvv DEBUG vvv
        AST(False, variableMemory, name="Versions/test_file.kha")
        sys.exit()

if __name__ == "__main__":
    main()