/*
██╗  ██╗██╗  ██╗ █████╗  ██████╗ ████████╗██╗ ██████╗
██║ ██╔╝██║  ██║██╔══██╗██╔═══██╗╚══██╔══╝██║██╔════╝
█████╔╝ ███████║███████║██║   ██║   ██║   ██║██║
██╔═██╗ ██╔══██║██╔══██║██║   ██║   ██║   ██║██║
██║  ██╗██║  ██║██║  ██║╚██████╔╝   ██║   ██║╚██████╗
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝ ╚═════╝
 █ █ █▀▀ █▀█ █▀ █ █▀█ █▄ █   ▀█   █▀█
 ▀▄▀ ██▄ █▀▄ ▄█ █ █▄█ █ ▀█   █▄ ▄ █▄█

STARTED: ~1/22/2025
RELEASED: 

CHANGES: 
- Switched to C++
- Removed prototype features (text editor, CLI, system commands)
- 

TO-DO: 



*/

#include <iostream>
#include <vector>
#include <string>
#include <unordered_map>

#include "solve.h"

void debug(std::string input) { // Internal debug function
    std::cout << "DEBUG: " << input << std::endl;
}

int main() {

    debug(solve("3 + 4 != 7"));

    return 0;
}
