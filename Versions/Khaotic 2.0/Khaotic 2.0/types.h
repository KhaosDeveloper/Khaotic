#ifndef TYPES_H
#define TYPES_H

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <unordered_map>
#include <variant>

using Value = std::variant<int, float, std::string, bool>;

class Token {
public:
    std::string type;
    std::string value;

    Token(std::string t, std::string v) : type(t), value(v) {}
};

class Array {
    public:
        std::string name;
        std::vector<std::string> values;

};

class Entity {
    public:
        std::string name;
        
};

#endif