import re

# --- Lexer Implementation ---
class Lexer:
    def __init__(self):
        self.tokens = []
        self.keywords = {"var", "print"}
        self.token_specification = [
            ("NUMBER", r"\d+"),                   # Integer
            ("IDENTIFIER", r"[a-zA-Z_]\w*"),      # Identifiers
            ("ASSIGN", r"="),                     # Assignment operator
            ("SEMICOLON", r";"),                 # Statement terminator
            ("OPERATOR", r"[+\-*/]"),           # Arithmetic operators
            ("LPAREN", r"\("),                   # Left parenthesis
            ("RPAREN", r"\)"),                   # Right parenthesis
            ("SKIP", r"[ \t]+"),                # Skip spaces and tabs
            ("MISMATCH", r"."),                  # Any other character
        ]

    def tokenize(self, code):
        token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in self.token_specification)
        for match in re.finditer(token_regex, code):
            kind = match.lastgroup
            value = match.group()
            if kind == "NUMBER":
                value = int(value)
            elif kind == "SKIP":
                continue
            elif kind == "MISMATCH":
                raise SyntaxError(f"Unexpected character: {value}")

            self.tokens.append((kind, value))
        self.tokens.append(("EOF", None))  # End-of-file token
        return self.tokens

# --- Parser Implementation ---
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        self.pos += 1
        return self.tokens[self.pos - 1]

    def expect(self, token_type):
        if self.peek()[0] == token_type:
            return self.advance()
        else:
            raise SyntaxError(f"Expected {token_type}, found {self.peek()[0]}")

    def parse(self):
        statements = []
        while self.peek()[0] != "EOF":
            statements.append(self.statement())
        return statements

    def statement(self):
        token_type, value = self.peek()
        if token_type == "IDENTIFIER" and value == "var":
            return self.variable_declaration()
        elif token_type == "IDENTIFIER" and value == "print":
            return self.print_statement()
        else:
            raise SyntaxError(f"Unknown statement: {value}")

    def variable_declaration(self):
        self.expect("IDENTIFIER")  # 'var'
        var_name = self.expect("IDENTIFIER")[1]
        self.expect("ASSIGN")
        value = self.expression()
        self.expect("SEMICOLON")
        return ("var_decl", var_name, value)

    def print_statement(self):
        self.expect("IDENTIFIER")  # 'print'
        value = self.expression()
        self.expect("SEMICOLON")
        return ("print", value)

    def expression(self):
        left = self.term()
        while self.peek()[0] == "OPERATOR":
            op = self.advance()[1]
            right = self.term()
            left = ("bin_op", op, left, right)
        return left

    def term(self):
        token_type, value = self.peek()
        if token_type == "NUMBER":
            return self.advance()
        elif token_type == "IDENTIFIER":
            return self.advance()
        elif token_type == "LPAREN":
            self.advance()  # Skip '('
            expr = self.expression()
            self.expect("RPAREN")
            return expr
        else:
            raise SyntaxError(f"Unexpected token: {token_type}")

# --- Code Generation Implementation ---
class CodeGenerator:
    def __init__(self):
        self.instructions = []

    def generate(self, ast):
        for statement in ast:
            self.generate_statement(statement)
        return self.instructions

    def generate_statement(self, statement):
        if statement[0] == "var_decl":
            _, var_name, value = statement
            self.instructions.append(f"ALLOC {var_name}")
            self.generate_expression(value)
            self.instructions.append(f"STORE {var_name}")
        elif statement[0] == "print":
            _, value = statement
            self.generate_expression(value)
            self.instructions.append("PRINT")
        else:
            raise RuntimeError(f"Unknown statement type: {statement[0]}")

    def generate_expression(self, expr):
        if isinstance(expr, tuple):
            if expr[0] == "bin_op":
                _, op, left, right = expr
                self.generate_expression(left)
                self.generate_expression(right)
                self.instructions.append(f"OP {op}")
            elif expr[0] == "NUMBER":
                self.instructions.append(f"PUSH {expr[1]}")
            elif expr[0] == "IDENTIFIER":
                self.instructions.append(f"LOAD {expr[1]}")
        elif isinstance(expr, int):
            self.instructions.append(f"PUSH {expr}")

# --- Virtual Machine Implementation ---
class VirtualMachine:
    def __init__(self):
        self.stack = []
        self.variables = {}

    def execute(self, instructions):
        for instruction in instructions:
            self.execute_instruction(instruction)

    def execute_instruction(self, instruction):
        parts = instruction.split()
        op = parts[0]
        
        if op == "ALLOC":
            var_name = parts[1]
            self.variables[var_name] = None
        elif op == "PUSH":
            value = int(parts[1])
            self.stack.append(value)
        elif op == "LOAD":
            var_name = parts[1]
            self.stack.append(self.variables.get(var_name))
        elif op == "STORE":
            var_name = parts[1]
            value = self.stack.pop()
            self.variables[var_name] = value
        elif op == "OP":
            operator = parts[1]
            right = self.stack.pop()
            left = self.stack.pop()
            if operator == "+":
                self.stack.append(left + right)
            elif operator == "-":
                self.stack.append(left - right)
            elif operator == "*":
                self.stack.append(left * right)
            elif operator == "/":
                self.stack.append(left / right)
        elif op == "PRINT":
            print(self.stack.pop())

# --- Example Usage ---
if __name__ == "__main__":
    code = """
    var x = 20;
    print(x + (5 + 2));
    """

    # Step 1: Tokenization
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    print("Tokens:")
    for token in tokens:
        print(token)

    # Step 2: Parsing
    parser = Parser(tokens)
    ast = parser.parse()
    print("\nAST:")
    for node in ast:
        print(node)

    # Step 3: Code Generation
    codegen = CodeGenerator()
    instructions = codegen.generate(ast)
    print("\nGenerated Code:")
    for instruction in instructions:
        print(instruction)

    # Step 4: Execution using Virtual Machine
    vm = VirtualMachine()
    vm.execute(instructions)

    # Final value output
    #print("\nFinal value of x through virtual machine implementation:", vm.variables['x'])
