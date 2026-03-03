# Khaotic
<p align="center">
  <img width="512" height="512" alt="Khaotic Logo" src="https://github.com/user-attachments/assets/f3e4ebe2-09d4-4c2c-8b37-e720f98f6db1" />
</p>
Khaotic is a minimalistic esoteric coding language I created originally for a high school science fair. It started as just a simple lexer and parser, but after being informed of the fair it evolved into what it is now. The final version is 945 lines of code and features: <br />
- A full lexer and parser. Order of operations goes: PEMDASCC<br />
- Dynamically typed and supports numbers, negatives, decimals, bools, and strings. <br />
- A small standard library<br />
- Custom AST/command interpreter<br />
- System/shell commands for system control <br />
- First standalone version<br />
- A text editor (PROTOTYPE; BUGGY)<br />
- External command line interface<br />
<br />
The idea behind the language was based on old turing machine designs and other esoteric coding languages. Programs can be divided into lines but can also be ran as one big line of code. It has a lot of issues and potentially bugs, however the final version was programmed in 2 months while being in school full time. It also became more like a shell language, with the ability to change directories, open and edit files, create files, and run them using the extension ".kha". Here is the full syntax: <br /><br />
COMMANDS:<br />
"^" to print.<br />
"@name" to declare or reference a variable.<br />
"v@name" to save user input into a variable.<br />
"<name" defines a label (<label1;<label2;). Use "<start" to define the start of your program or it will start at the first line.<br />
">name" jumps to the label specified. ">return" jumps to the last place a jump command was called.<br />
"?(condition){statement}" executes the statement if the condition is True.<br />
":(args)" are for built in functions like ":abs(num)" will return the absolute value of the number specified.<br />
<br />
SYSTEM COMMANDS:<br />
"!q;" to quit.<br />
"!h;" for help.<br />
"!p;" to change path.<br />
"!r;" to run a file.<br />
"!o;" to open/edit a file.<br />
"!n;" to make a new file.<br />
"!c;" to clear terminal.<br />
"!l;" to list all .kha files in current directory.<br />
"!d;" to dissect/debug a program.<br />

<br />
Feel free to steal code from the lexer/parser or to take a look inside. Watch the video on my YouTube or visit my Dev porfolio to learn more (and the issues with it)<br /> <br />
<pre>
 __  __     __  __     ______     ______     ______    
/\ \/ /    /\ \_\ \   /\  __ \   /\  __ \   /\  ___\   
\ \  _"-.  \ \  __ \  \ \  __ \  \ \ \/\ \  \ \___  \  
 \ \_\ \_\  \ \_\ \_\  \ \_\ \_\  \ \_____\  \/\_____\ 
  \/_/\/_/   \/_/\/_/   \/_/\/_/   \/_____/   \/_____/ 
</pre>                                                  
