from lexer import Token, Lexer

class Parser:
    class ProgramNode:
        def __init__(self, statements): self.statements = statements
        def __repr__(self): return f"ProgramNode({self.statements})"

    class AssignStatementNode:
        def __init__(self, left, right):
            self.left = left
            self.right = right
        def __repr__(self): return f"AssignStatementNode({self.left}, {self.right})"

    class IfStatementNode:
        def __init__(self, condition, if_body, else_body):
            self.condition = condition
            self.if_body = if_body
            self.else_body = else_body
        def __repr__(self): return f"IfStatementNode({self.condition}, {self.if_body}, {self.else_body})"

    class WhileStatementNode:
        def __init__(self, condition, body):
            self.condition = condition
            self.body = body
        def __repr__(self): return f"WhileStatementNode({self.condition}, {self.body})"

    class ArithmeticExpressionNode:
        def __init__(self, left, operator, right):
            self.left = left
            self.operator = operator
            self.right = right
        def __repr__(self): return f"ArithmeticExpressionNode({self.left}, {self.operator}, {self.right})"

    class IntNode:
        def __init__(self, value): self.value = value
        def __repr__(self): return f"IntNode({self.value})"

    class VarNode:
        def __init__(self, value): self.value = value
        def __repr__(self): return f"VarNode({self.value})"

    def __init__(self, program):
        self.program = program
        self.position = 0
        self.current_token = self.program[self.position]

    def _consume_token_type(self, token_types, error_message):
        if self.current_token.get_token_type() in token_types:
            return self._consume_next_token()
        else:
            raise SyntaxError(error_message)

    def _consume_next_token(self):
        old_token = self.program[self.position]
        self.position += 1
        self.current_token = self.program[self.position]
        return old_token

    def parse_program(self):
        statements = []
        while self.current_token.get_token_type() != Token.Type.EOF:
            stmt = self._parse_statement()
            self._consume_token_type([Token.Type.EOL], "Expected semicolon")
            statements.append(stmt)
        return Parser.ProgramNode(statements)

    def _parse_statement(self):
        match self.current_token.get_token_type():
            case Token.Type.IF:
                return self._parse_if_statement()
            case Token.Type.WHILE:
                return self._parse_while_statement()
            case Token.Type.IDENTIFIER:
                return self._parse_assign_statement()
            case _:
                raise SyntaxError(f"Unexpected token \
                        {self.current_token.get_value()}")

    def _parse_assign_statement(self):
        left_token = self._consume_next_token()
        left_node = Parser.VarNode(left_token.get_value())
        self._consume_token_type([Token.Type.ASSIGNMENT], "Expected :=")
        right_node = self._parse_arithmetic_expression()
        return Parser.AssignStatementNode(left_node, right_node)

    def _parse_arithmetic_expression(self):
        expression = self._parse_term()
        operators = [Token.Type.PLUS, Token.Type.MINUS]
        while self.current_token.get_token_type() in operators:
            operator = self._consume_next_token().get_value()
            right = self._parse_term()
            expression = Parser.ArithmeticExpressionNode(expression, 
                                                         operator, 
                                                         right)
        return expression

    def _parse_term(self):
        expression = self._parse_factor()
        while self.current_token.get_token_type() == Token.Type.TIMES:
            operator = self._consume_next_token().get_value()
            right = self._parse_factor()
            expression = Parser.ArithmeticExpressionNode(expression,
                                                         operator, 
                                                         right)
        return expression

    def _parse_factor(self):
        token = self._consume_next_token()
        match token.get_token_type():
            case Token.Type.IDENTIFIER:
                return Parser.VarNode(token.get_value())
            case Token.Type.INTEGER:
                return Parser.IntNode(token.get_value())
            case Token.Type.LEFT_BRACKET:
                expression = self._parse_arithmetic_expression()
                self._consume_token_type([Token.Type.RIGHT_BRACKET], 
                                         "Expected ')'")
                return expression
            case _:
                raise SyntaxError(f"Unexpected token {token.get_value()}")