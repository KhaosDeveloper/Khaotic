#include "solve.h"
#include "types.h"

#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>
#include <cmath>
#include <stack>
#include <cctype>
#include <set>
#include <unordered_map>
#include <variant>

std::vector<Token> tokenize(const std::string& input) {
    int x = 0;
    bool inString = false;
    std::string buffer;
    std::vector<Token> tokens;

    while (x < input.length()) {
        if (std::isspace(input[x])) { // space handling
            x++;
            continue;

        } else if ((std::isdigit(input[x])) || (input[x] == '-' && std::isdigit(input[x + 1]))) { // numbers (including negatives)
            buffer += input[x];
            x++;
            while (std::isdigit(input[x]) || input[x] == '.') {
                buffer += input[x];
                x++;
            }
            tokens.push_back(Token("number", buffer));
            buffer.clear();
            continue;

        } else if (input[x] == '\"') { // strings
            x++;  // skip quote
            buffer.clear();
            while (x < input.length() && !(input[x] == '\"' && input[x - 1] != '\\')) {
                buffer += input[x];
                x++;
            }
            if (x < input.length()) {
                tokens.push_back(Token("string", buffer));
                buffer.clear();
                x++; // Skip the closing quote
            } else {
                throw std::runtime_error("No string close");
            }
            continue;

        } else if (input.substr(x, 5) == "false") { // booleans
            tokens.push_back(Token("boolean", "false"));
            x += 5;
        } else if (input.substr(x, 4) == "true") {
            tokens.push_back(Token("boolean", "true"));
            x += 4;

        } else if (input.substr(x, 3) == "and" || input.substr(x, 3) == "not") { // Handle conditions
            tokens.push_back(Token("condition", input.substr(x, 3)));
            x += 3;
        } else if (input.substr(x, 2) == "or") {
            tokens.push_back(Token("condition", "or"));
            x += 2;

        } else if (input.substr(x, 2) == "<=" || input.substr(x, 2) == ">=" || input.substr(x, 2) == "!=" || input.substr(x, 2) == "==") { // dual operators
            tokens.push_back(Token("operator", input.substr(x, 2)));
            x += 2;

        } else if (input[x] == '+' || input[x] == '-' || input[x] == '*' || input[x] == '/' || input[x] == '%' || input[x] == '<' || input[x] == '>' || input[x] == '^') { // single operators
            tokens.push_back(Token("operator", std::string(1, input[x])));
            x++;
        
        } else if (input[x] == '='){
            x++;

        } else if (input[x] == '(') { // handle parentheses
            tokens.push_back(Token("left_para", "("));
            x++;
        } else if (input[x] == ')') {
            tokens.push_back(Token("right_para", ")"));
            x++;
        
        } else if ((std::isalnum(input[x])) || (input[x] == '_')) { // variables
            buffer += input[x];
            x++;
            while ((std::isalnum(input[x])) || (input[x] == '_')) {
                buffer += input[x];
                x++;
            }
            tokens.push_back(Token("variable", buffer));
            buffer.clear();
            continue;

        } else { // Unknown
            tokens.push_back(Token("unknown", "None"));
        }
    } 

    tokens.push_back(Token("EOF", "None"));
    return tokens;
}

int precedence(const Token& token) {
    if (token.value == "not") return 3;
    if (token.value == "and") return 2;
    if (token.value == "or") return 1;
    if (token.value == ">" || token.value == "<" || token.value == "==" || token.value == ">=" || token.value == "<=") return 4;
    if (token.value == "+" || token.value == "-") return 5;
    if (token.value == "*" || token.value == "/" || token.value == "%") return 6;
    return 0;
}

bool isOperator(const Token& token) {
    return token.type == "operator";
}

std::vector<std::string> math_postfix(const std::vector<Token>& tokens) {
    std::stack<Token> s;
    std::vector<std::string> postfix;

    for (const auto& token : tokens) {
        if (token.type == "number" || token.type == "boolean" || token.type == "string") {
            postfix.push_back("LDA: " + token.value);
        } else if (token.type == "left_para") {
            s.push(token);
        } else if (token.type == "right_para") {
            while (!s.empty() && s.top().type != "left_para") {
                postfix.push_back("OPR: " + s.top().value);
                s.pop();
            }
            if (!s.empty() && s.top().type == "left_para") s.pop();
        } else if (isOperator(token)) {  // Handle arithmetic, logical, and comparison operators
            while (!s.empty() && precedence(s.top()) >= precedence(token) && s.top().value != "^") {
                postfix.push_back("OPR: " + s.top().value);
                s.pop();
            }
            s.push(token);
        } else if (token.value == "and" || token.value == "or" || token.value == "not") {  // Handle logical operators
            while (!s.empty() && precedence(s.top()) >= precedence(token)) {
                postfix.push_back("OPR: " + s.top().value);
                s.pop();
            }
            s.push(token);
        } else if (token.value == ">" || token.value == "<" || token.value == "==" || token.value == ">=" || token.value == "<=") {  // Handle comparison operators
            while (!s.empty() && precedence(s.top()) >= precedence(token)) {
                postfix.push_back("OPR: " + s.top().value);
                s.pop();
            }
            s.push(token);
        }
    }

    // Pop remaining operators from the stack
    while (!s.empty()) {
        postfix.push_back("OPR: " + s.top().value);
        s.pop();
    }

    return postfix;
}

bool isNumber(const Value& val) {
    return std::holds_alternative<float>(val);
}

bool isString(const Value& val) {
    return std::holds_alternative<std::string>(val);
}

bool isBoolean(const Value& val) {
    return std::holds_alternative<bool>(val);
}

std::string toString(const Value& val) {
    if (isNumber(val)) {
        return std::to_string(std::get<float>(val));
    } else if (isString(val)) {
        return std::get<std::string>(val);
    } else if (isBoolean(val)) {
        return std::get<bool>(val) ? "true" : "false";
    }
    return "";
}

void performArithmetic(std::stack<Value>& stack, const std::string& op) {
    if (stack.size() < 2) {
        throw std::runtime_error("Insufficient operands for operation: " + op);
    }

    Value right = stack.top();
    stack.pop();
    Value left = stack.top();
    stack.pop();

    if (isNumber(left) && isNumber(right)) {
        float leftVal = std::get<float>(left);
        float rightVal = std::get<float>(right);
        float result;

        if (op == "+") {
            result = leftVal + rightVal;
        } else if (op == "-") {
            result = leftVal - rightVal;
        } else if (op == "*") {
            result = leftVal * rightVal;
        } else if (op == "/") {
            if (rightVal == 0) {
                throw std::runtime_error("Division by zero");
            }
            result = leftVal / rightVal;
        } else if (op == "%") {
            if (rightVal == 0) {
                throw std::runtime_error("Modulo by zero");
            }
            result = std::fmod(leftVal, rightVal);
        } else {
            throw std::runtime_error("Unsupported operator: " + op);
        }

        stack.push(result);

    } else if (op == "+") {
        std::string leftVal = toString(left);
        std::string rightVal = toString(right);
        std::string result = leftVal + rightVal;
        stack.push(result);
    } else {
        throw std::runtime_error("Invalid operands for operation: " + op);
    }
}

void performComparison(std::stack<Value>& stack, const std::string& op) {
    if (stack.size() < 2) {
        throw std::runtime_error("Insufficient operands for comparison");
    }

    Value right = stack.top();
    stack.pop();
    Value left = stack.top();
    stack.pop();

    bool result = false;

    if (isNumber(left) && isNumber(right)) {
        if (op == "==") {
            result = std::get<float>(left) == std::get<float>(right);
        } else if (op == ">") {
            result = std::get<float>(left) > std::get<float>(right);
        } else if (op == "<") {
            result = std::get<float>(left) < std::get<float>(right);
        } else if (op == ">=") {
            result = std::get<float>(left) >= std::get<float>(right);
        } else if (op == "<=") {
            result = std::get<float>(left) <= std::get<float>(right);
        }
    } else if (isString(left) && isString(right)) {
        if (op == "==") {
            result = std::get<std::string>(left) == std::get<std::string>(right);
        }
    } else {
        throw std::runtime_error("Invalid operands for comparison");
    }

    stack.push(result);
}


void performLogicalAnd(std::stack<Value>& stack) {
    if (stack.size() < 2) {
        throw std::runtime_error("Insufficient operands for logical AND");
    }

    Value right = stack.top();
    stack.pop();
    Value left = stack.top();
    stack.pop();

    if (isBoolean(left) && isBoolean(right)) {
        bool result = std::get<bool>(left) && std::get<bool>(right);
        stack.push(result);
    } else {
        throw std::runtime_error("Invalid operands for logical AND");
    }
}

void performLogicalOr(std::stack<Value>& stack) {
    if (stack.size() < 2) {
        throw std::runtime_error("Insufficient operands for logical OR");
    }

    Value right = stack.top();
    stack.pop();
    Value left = stack.top();
    stack.pop();

    if (isBoolean(left) && isBoolean(right)) {
        bool result = std::get<bool>(left) || std::get<bool>(right);
        stack.push(result);
    } else {
        throw std::runtime_error("Invalid operands for logical OR");
    }
}

void performLogicalNot(std::stack<Value>& stack) {
    if (stack.empty()) {
        throw std::runtime_error("Insufficient operands for logical NOT");
    }

    Value top = stack.top();
    stack.pop();

    if (isBoolean(top)) {
        bool result = !std::get<bool>(top);
        stack.push(result);
    } else {
        throw std::runtime_error("Invalid operand for logical NOT");
    }
}

std::string parse_statement(const std::vector<std::string>& postfix) {
    std::stack<Value> stack;

    for (const std::string& token : postfix) {
        if (token.substr(0, 4) == "LDA:") {
            // Load a value (either number, string, or boolean)
            std::string operand = token.substr(5);

            // Check if the operand is a boolean value
            if (operand == "true" || operand == "false") {
                stack.push(operand == "true");
            }

            else if ((operand[0] == '-' && operand.substr(1).find_first_not_of("0123456789.") == std::string::npos) || 
                    operand.find_first_not_of("0123456789.") == std::string::npos) {
                stack.push(std::stof(operand));
            } else {
                stack.push(operand);
            }
        } else if (token.substr(0, 4) == "OPR:") {
            std::string op = token.substr(5);

            if (op == "+" || op == "-" || op == "*" || op == "/" || op == "%") {
                performArithmetic(stack, op);
            }
            else if (op == "==" || op == ">" || op == "<" || op == ">=" || op == "<=") {
                performComparison(stack, op);
            }
            else if (op == "and") {
                performLogicalAnd(stack);
            }
            else if (op == "or") {
                performLogicalOr(stack);
            }
            else if (op == "not") {
                performLogicalNot(stack);
            }
            else {
                throw std::runtime_error("Unknown operator: " + op);
            }
        } else {
            throw std::runtime_error("Unknown token: " + token);
        }
    }

    if (stack.size() != 1) {
        std::cout << "Stack contents (top to bottom): ";
        
        while (!stack.empty()) {
            std::cout << toString(stack.top()) << " ";
            stack.pop();
        }
        
        std::cout << std::endl;
        throw std::runtime_error("Invalid postfix expression");
    }

    Value result = stack.top();
    stack.pop();

    if (isNumber(result)) {
        return toString(result);
    } else if (isString(result)) {
        return std::get<std::string>(result);
    } else if (isBoolean(result)) {
        return (std::get<bool>(result) ? "true" : "false");
    }
}

std::string solve(std::string input) {
    std::vector<Token> tokens = tokenize(input);
    std::vector<std::string> postfixed_commands = math_postfix(tokens);
    
    return parse_statement(postfixed_commands);

} 