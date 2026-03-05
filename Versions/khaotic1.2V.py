'''

██╗  ██╗██╗  ██╗ █████╗  ██████╗ ████████╗██╗ ██████╗
██║ ██╔╝██║  ██║██╔══██╗██╔═══██╗╚══██╔══╝██║██╔════╝
█████╔╝ ███████║███████║██║   ██║   ██║   ██║██║
██╔═██╗ ██╔══██║██╔══██║██║   ██║   ██║   ██║██║
██║  ██╗██║  ██║██║  ██║╚██████╔╝   ██║   ██║╚██████╗
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝
 █ █ █▀▀ █▀█ █▀ █ █▀█ █▄ █ ▄█   ▀█
 ▀▄▀ ██▄ █▀▄ ▄█ █ █▄█ █ ▀█  █ ▄ █▄

STARTED: 2/6
RELEASED: 3/6
LAST UPDATED: 10/3

CHANGES:
- Combined full lexer and both parsers. Order of operations goes: PEMDASCC
- Added exponents to the lexer/parser
- Boolean token/data type
- Supports negatives
- Standard Library
- Removed sub-commands, now everything is passed through the lexer/parser
- More system commands
- First standalone version
- A text editor
- External command line interface
'''

import os
import os.path
import keyboard
import argparse
import sys
import time
import random as ran

# =============
# == CLASSES ==
# =============

class Token: # Lexer and parser started at 1:48 PM, 1/4. Full lexer and parser done at 4:18 PM, 2/1.
    def __init__(self, type, value):
        self.type = type
        self.value = value
class Variable:
    def __init__(self, name, value):
        self.name = name
        self.value = value

# =============
# === LEXER ===
# =============

def fullLexer(text):
    tokens = []
    number = ''
    modText = text + " "
    x = 0
    while x in range (len(modText)):
        if modText[x] == '"': # TODO: Add quotes to strings using the break (\) character. Issue is Python uses the '\' character, meaning it overrides.
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
        elif modText[x] == '-' and (modText[x+1].isdigit() or modText[x+1] == '.'):
            if number == '':
                number = '-'
                x += 1
                continue
        else:
            if number != '':
                tokens.append(Token('number', number))
            number = ''
        if modText[x] in ['>', '<', '=', '!'] and modText[x + 1] == '=':
            tokens.append(Token('operator', modText[x:x + 2]))
            x += 1
        elif modText[x] in ['>', '<', '=']:
            tokens.append(Token('operator', modText[x]))
        elif modText[x:x + 2] == '**':
            tokens.append(Token('operator', '**'))
            x += 1
        elif modText[x] in ['+', '-', '*', '/', '%']:
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
        elif modText[x:x + 4] == 'True':
            tokens.append(Token('boolean', True))
            x += 3
        elif modText[x:x + 5] == 'False':
            tokens.append(Token('boolean', False))
            x += 4
        elif modText[x] == '(':
            tokens.append(Token('leftPara', modText[x]))
        elif modText[x] == ')':
            tokens.append(Token('rightPara', modText[x]))
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

# ========================
# === STANDARD LIBRARY ===
# ========================

def standardLib(text):
  def absoluteValue(a):
    a = str(setup(a))
    b = a + '/' + '-1'
    if setup(a + '>=' + '0'):
      return a
    else:
      return setup(b)
  def round(a):
    a = str(setup(a))
    b = setup(a + '%' + '1')
    if setup(str(b) + '<' + '0.5'):
      return setup(a + '-' + str(b))
    else:
      return setup(a + '+' + '('+ '1' + '-' + str(b) + ')')
  def getChar(args):  # (string[index])
    str = setup(args[0 : args.rfind('[')])
    index = setup(args[args.rfind('[') + 1:args.rfind(']')])
    return '"' + str[int(float(index))] + '"'
  def setChar(args):  # (string[index], char)
    tokens = setupNoParse(args + ')')
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
    s = str(setup(args))
    x = 0
    for char in s:
        x += 1
    return x
  def fileLines(args):
      tokens = setupNoParse(args)
      file = tokens[0].value
      with open(file, 'r') as f:
          lines = f.readlines()
      return len(lines)
  def readFile(args):  # ("file.txt[index]") FILE NEEDS QUOTES AROUND IT
      tokens = setupNoParse(args)
      file = tokens[0].value
      index = tokens[1].value
      with open(file, 'r') as f:
          lines = f.readlines()
      string = '"' + lines[int(index) - 1] + '"'
      string = string.replace("\n", "")
      return string
  def writeFile(args):  # ("file.txt"[index], "Text") FILE NEEDS QUOTES AROUND IT.
      tokens = setupNoParse(args)
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
      tokens = setupNoParse(args)
      wait = tokens[0].value
      time.sleep(float(wait))
      return
  def random(args):
      tokens = setupNoParse(args)
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

def setupNoParse(text):
    a = 0
    b = 0
    inString = False
    text = ' ' + text + ' '
    while a in range(len(text)):
        while text[a] == '@' and not inString:
            while text[b] in ['=', '!', '>', '<', 'and', 'or', 'not', '+', '-', '*', '/', '%', '(', ')', '[', ']', ' ']:
                varName = text[a+1:b]
                varValue = searchVar(varName)
                if varValue == True or varValue == False:
                    text = text[0:a] + str(varValue) + text[b:]
                elif not all(char.isdigit() or char == '.' for char in str(varValue)) and varValue is not True or False:
                    text = text[0:a] + '"' + str(varValue) + '"' + text[b:]
                else:
                    text = text[0:a] + str(varValue) + text[b:]
                b = a
            else:
                if b == len(text) - 1:
                    varName = text[a+1:]
                    varValue = searchVar(varName)
                    if varValue == True or varValue == False:
                        text = text[0:a] + str(varValue) + text[b+1:]
                    elif not all(char.isdigit() or char == '.' for char in str(varValue)) and varValue is not True or False:
                        text = text[0:a] + '"' + str(varValue) + '"' + text[b+1:]
                    else:
                        text = text[0:a] + str(varValue) + text[b+1:]
                    b = a
                else:
                    b += 1
        while text[a] == ':' and not inString:
          b += 1
          if b == len(text) - 1 and text[b] != ')':
              text = text + ')'
          if text[b] == ')':
            text = text[0:a] + str(standardLib(text[a+1:b+1])) + text[b+1:]
        else:
            if text[a] == '"':
                inString = not inString
            a += 1
            b = a
    tokens = fullLexer(text)
    return tokens

def setup(text):
    a = 0
    b = 0
    inString = False
    text = ' ' + text + ' '
    while a in range(len(text)):
        while text[a] == '@' and not inString:
            while text[b] in ['=', '!', '>', '<', 'and', 'or', 'not', '+', '-', '*', '/', '%', '(', ')', ' ']:
                varName = text[a+1:b]
                varValue = searchVar(varName)
                if varValue == True or varValue == False:
                    text = text[0:a] + str(varValue) + text[b:]
                elif not all(char.isdigit() or char == '.' for char in str(varValue)) and varValue is not True or False:
                    text = text[0:a] + '"' + str(varValue) + '"' + text[b:]
                else:
                    text = text[0:a] + str(varValue) + text[b:]
                b = a
            else:
                if b == len(text) - 1:
                    varName = text[a+1:]
                    varValue = searchVar(varName)
                    if varValue == True or varValue == False:
                        text = text[0:a] + str(varValue) + text[b+1:]
                    elif not all(char.isdigit() or char == '.' for char in str(varValue)) and varValue is not True or False:
                        text = text[0:a] + '"' + str(varValue) + '"' + text[b+1:]
                    else:
                        text = text[0:a] + str(varValue) + text[b+1:]
                    b = a
                else:
                    b += 1
        while text[a] == ':' and not inString:
          b += 1
          if text[b] == ')':
            text = text[0:a] + str(standardLib(text[a+1:b+1])) + text[b+1:]
        else:
            if text[a] == '"':
                inString = not inString
            a += 1
            b = a
    tokens = fullLexer(text)
    if len(tokens) == 1:
      return tokens[0].value
    else:
      result = fullParser(tokens)
      return result

def searchVar(varName): # Searches by name and returns the value
    for i in range(len(variableMemory)):
      if variableMemory[i].name == varName:
          return variableMemory[i].value

def forceExit():
    exit()

# ===================
# === TEXT EDITOR ===
# ===================

def editText(text):
    cursorPos = len(text)
    modText = ''.join(text[:cursorPos]) + '|' + ''.join(text[cursorPos:])
    print(modText)
    while True:
        event = keyboard.read_event(suppress=True)
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'enter':
                text.insert(cursorPos, '\n')
                cursorPos += 1
            elif event.name == 'space':
                text.insert(cursorPos, ' ')
                cursorPos += 1
            elif event.name == 'backspace':
                if cursorPos > 0:
                    text.pop(cursorPos - 1)
                    cursorPos -= 1
            elif event.name == 'esc':
                break
            elif event.name == 'left':
                cursorPos = max(0, cursorPos - 1)
            elif event.name == 'right':
                cursorPos = min(len(text), cursorPos + 1)
            elif event.name not in ('shift', 'alt', 'ctrl', 'right shift', 'right alt', 'caps lock', 'tab', 'up', 'down'):
                text.insert(cursorPos, event.name)
                cursorPos += 1
            os.system('cls' if os.name == 'nt' else 'clear')
            modText = ''.join(text[:cursorPos]) + '|' + ''.join(text[cursorPos:])
            print(modText)
    return ''.join(text[:cursorPos]) + ''.join(text[cursorPos:])

# ========================
# == TERMINAL INTERFACE ==
# ========================

running = True
variableMemory = []
returnAddrs = []
def launch():
    print("Launching Khaotic...")
    os.system('cls' if os.name == 'nt' else 'clear')
def version():
    print("Khaotic Version 1.2")
    sys.exit()
def run(name):
    global running
    global variableMemory
    global returnAddrs
    file = open(name,"r")
    program = file.read().replace('\n', '')
    variableMemory = []
    returnAddrs = []
    lastAddress = 0
    ifCheck = False
    commands = program.split(';')
    x = 0
    for i in range(len(commands)):
        if commands[i] == '<start':
            x = i
            continue
    commands.pop(-1)
    commands.append("exit")
    while x in range(len(commands) - 1) and running == True:
      if commands[x][0] == '<':
          x += 1
          continue
      if commands[x][0] == '^':  # Printing
        if commands[x][1] == '^':  # Print new line
          print(setup(commands[x][2:]))
        else:
          print(setup(commands[x][1:]), end='')
      elif commands[x][0] == '@':  # Declaring variables
          y = commands[x].find('=')
          varName = commands[x][1:y]
          varName = varName.replace(" ", "")
          varValue = commands[x][y+1:]
          varValue = setup(varValue)
          for v in range(len(variableMemory)):
              if variableMemory[v].name == varName:
                  variableMemory.pop(v)
                  break
          variableMemory.insert(0, Variable(varName, varValue))
      elif commands[x][0] == 'v':  # Getting input, destination specified
          varName = commands[x][2:]
          for v in range(len(variableMemory)):
              if variableMemory[v].name == varName:
                  variableMemory.pop(v)
                  break
          variableMemory.insert(0, Variable(varName, input()))
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
              continue
      elif commands[x][0] == ':': # Built-in Function
          setup(commands[x])
      elif commands[x][0] == '?': # If statement (WILL BE TURING COMPLETE)
          sCond = commands[x].find('(')
          eCond = commands[x].rfind('{') - 1
          cond = commands[x][sCond + 1:eCond]
          dest = commands[x][eCond + 2:-1]
          if setup(cond):
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
          elif commands[x][1] == 'o': # Open file
            name = str(input("path: "))
            print(path + name)
            if os.path.exists(path + name):
                os.system('cls' if os.name == 'nt' else 'clear')
                with open(path + name, "r+", encoding='utf-8') as file:
                    text = list(file.read())
                    newText = editText(text)
                    file.seek(0)
                    file.truncate(0)
                    newText = newText.lstrip('\x00')
                    file.write(newText)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(khaotic)
                    print("Current directory: " + path)
            else:
                print("File does not exist.")
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
              print(i, ':', commands[i], ':', keyword, ':' ,argument)
            commands = []
      if ifCheck:
            commands.pop(lastAddress)
            ifCheck = False
            x-=1
      lastAddress = x
      x+=1 # Last line in main loop
    else:
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
        run(args.run)
    else:
        print("Invalid command. Use --help for more info.")
        run("Versions/test_file.kha")
        sys.exit()

if __name__ == "__main__":
    main()

# ===========
# === AST ===
# ===========

running = True
lastAddress = 0
ifCheck = False
khaotic = '''====================
=== KHAOTIC V1.2 ===
====================
"!h;" for help.'''
help = '''
Welcome to Khaotic, a minimalistic coding language. Here's a few basic tips and commands to get you started:
- Remember to end each line with a ";".
- You only have to implicitly state strings like "this".
- New lines in files are ignored by the interpreter.
- After a semicolon, DO NOT use the space character, as the first character is crucial for the command type. (i.e: ^"hello"; ^"This command will be ignored because the "^" was not the first character";).
- The directory is directly relative to where the .exe for the interpreter is.
- Use ESC to save and exit a file.

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
"!o;" to open/edit a file.
"!n;" to make a new file.
"!c;" to clear terminal.
"!l;" to list all .kha files in current directory.
"!d;" to dissect/debug a program.
'''

if os.getcwd() == '/content':
  path = os.getcwd() + '/'
else:
  path = os.getcwd() + '\\'
print(khaotic)
print("Current directory: " + path + '\n')
while running:
    program = input(">>> ") # Interpreter/AST?
    variableMemory = []
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
          print(setup(commands[x][2:]))
        else:
          print(setup(commands[x][1:]), end='')
      elif commands[x][0] == '@':  # Declaring variables
          y = commands[x].find('=')
          varName = commands[x][1:y]
          varName = varName.replace(" ", "")
          varValue = commands[x][y+1:]
          varValue = setup(varValue)
          for v in range(len(variableMemory)):
              if variableMemory[v].name == varName:
                  variableMemory.pop(v)
                  break
          variableMemory.insert(0, Variable(varName, varValue))
      elif commands[x][0] == 'v':  # Getting input, destination specified
          varName = commands[x][2:]
          for v in range(len(variableMemory)):
              if variableMemory[v].name == varName:
                  variableMemory.pop(v)
                  break
          variableMemory.insert(0, Variable(varName, input()))
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
          if setup(cond):
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
          elif commands[x][1] == 'o': # Open file
            name = str(input("path: "))
            print(path + name)
            if os.path.exists(path + name):
                os.system('cls' if os.name == 'nt' else 'clear')
                with open(path + name, "r+", encoding='utf-8') as file:
                    text = list(file.read())
                    newText = editText(text)
                    file.seek(0)
                    file.truncate(0)
                    newText = newText.lstrip('\x00')
                    file.write(newText)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(khaotic)
                    print("Current directory: " + path)
            else:
                print("File does not exist.")
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
              print(i, ':', commands[i], ':', keyword, ':' ,argument)
            commands = []
      if ifCheck:
            commands.pop(x)
            ifCheck = False
            x-=1
      lastAddress = x
      x+=1 # Last line in main loop
    else:
        print()
        ifCheck = False
