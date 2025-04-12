from lexer import Token, Lexer


class Parser:
    class ProgramNode:
        def __init__(self, statements): self.statements = statements

        def __repr__(self):
            return f"ProgramNode({self.statements})"

    class AssignStatementNode:
        def __init__(self, left, right):
            self.left = left
            self.right = right

        def __repr__(self):
            return f"AssignStatementNode({self.left}, {self.right})"

    class IfStatementNode:
        def __init__(self, condition, if_body, else_body):
            self.condition = condition
            self.if_body = if_body
            self.else_body = else_body

        def __repr__(self):
            return f"IfStatementNode({self.condition}, {self.if_body}, {self.else_body})"

    class WhileStatementNode:
        def __init__(self, condition, body):
            self.condition = condition
            self.body = body

        def __repr__(self):
            return f"WhileStatementNode({self.condition}, {self.body})"

    class ArithmeticExpressionNode:
        def __init__(self, left, op, right):
            self.left = left
            self.op = op
            self.right = right

        def __repr__(self):
            return f"ArithmeticExpressionNode({self.left}, {self.op}, {self.right})"

    class IntNode:
        def __init__(self, value): self.value = value

        def __repr__(self): return f"IntNode({self.value})"

    class VarNode:
        def __init__(self, value): self.value = value

        def __repr__(self): return f"VarNode({self.value})"

    class BoolNode:
        def __init__(self, value): self.value = value

        def __repr__(self): return f"BoolNode({self.value})"

    class NotNode:
        def __init__(self, boolean): self.boolean = boolean

        def __repr__(self): return f"NotNode({self.boolean})"

    class ComparisonNode:
        def __init__(self, left, op, right):
            self.left = left
            self.op = op
            self.right = right

        def __repr__(self):
            return f"ComparisonNode({self.left}, {self.op}, {self.right})"

    class AndNode:
        def __init__(self, left, right):
            self.left = left
            self.right = right

        def __repr__(self): return f"AndNode({self.left}, {self.right})"

    def __init__(self, program):
        self.program = program
        self.position = 0
        self.current_token = self.program[self.position]

    def _consume_token_type(self, token_type, error_message):
        if self.current_token.get_token_type() == token_type:
            return self._consume_next_token()
        else:
            value = self.current_token.get_value()
            raise SyntaxError(error_message + f", Current token: {value}")

    def _consume_next_token(self):
        old_token = self.program[self.position]
        self.position += 1
        self.current_token = self.program[self.position]
        return old_token

    def _peek(self):
        return self.program[self.position + 1]

    def parse_program(self):
        statements = []
        while self.current_token.get_token_type() != Token.Type.EOF:
            stmt = self._parse_statement()
            self._consume_token_type(Token.Type.EOL, "Expected semicolon")
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
        self._consume_token_type(Token.Type.ASSIGNMENT, "Expected :=")
        right_node = self._parse_arithmetic_expression()
        return Parser.AssignStatementNode(left_node, right_node)

    def _parse_arithmetic_expression(self):
        expression = self._parse_arithmetic_term()
        operators = [Token.Type.PLUS, Token.Type.MINUS]
        while self.current_token.get_token_type() in operators:
            operator = self._consume_next_token().get_value()
            right = self._parse_arithmetic_term()
            expression = Parser.ArithmeticExpressionNode(expression,
                                                         operator,
                                                         right)
        return expression

    def _parse_arithmetic_term(self):
        expression = self._parse_arithmetic_factor()
        while self.current_token.get_token_type() == Token.Type.TIMES:
            operator = self._consume_next_token().get_value()
            right = self._parse_arithmetic_factor()
            expression = Parser.ArithmeticExpressionNode(expression,
                                                         operator,
                                                         right)
        return expression

    def _parse_arithmetic_factor(self):
        token = self._consume_next_token()
        match token.get_token_type():
            case Token.Type.IDENTIFIER:
                return Parser.VarNode(token.get_value())
            case Token.Type.INTEGER:
                return Parser.IntNode(token.get_value())
            case Token.Type.LEFT_BRACKET:
                expression = self._parse_arithmetic_expression()
                self._consume_token_type(Token.Type.RIGHT_BRACKET,
                                         "Expected ')'")
                return expression
            case _:
                raise SyntaxError(f"Unexpected token {token.get_value()}")

    def _parse_if_statement(self):
        self._consume_next_token() # Consume if
        condition = self._parse_boolean_expression()
        self._consume_next_token() # Consume then
        if_body = []
        while self.current_token.get_token_type() != Token.Type.ELSE:
            if self.current_token.get_token_type() == Token.Type.EOF:
                raise SyntaxError("Unexpected end of file, expected 'else'")
            stmt = self._parse_statement()
            self._consume_token_type(Token.Type.EOL, "Expected semicolon")
            if_body.append(stmt)
        self._consume_next_token() # Consume else
        else_body = []
        while self.current_token.get_token_type() != Token.Type.END:
            if self.current_token.get_token_type() == Token.Type.EOF:
                raise SyntaxError("Unexpected end of file, expected 'end'")
            stmt = self._parse_statement()
            self._consume_token_type(Token.Type.EOL, "Expected semicolon")
            else_body.append(stmt)
        self._consume_next_token() # Consume end
        return Parser.IfStatementNode(condition, if_body, else_body)

    def _parse_boolean_expression(self):
        print(f"parsing expression, token: {self.current_token.get_value()}")
        expression = self._parse_boolean_term()
        operators = [Token.Type.EQUALS,
                     Token.Type.LESS_THAN,
                     Token.Type.LESS_OR_EQUAL,
                     Token.Type.GREATER_THAN,
                     Token.Type.GREATER_OR_EQUAL]
        while self.current_token.get_token_type() in operators:
            operator = self._consume_next_token().get_value()
            right = self._parse_boolean_term()
            expression = Parser.ComparisonNode(expression, operator, right)
        return expression

    def _parse_boolean_term(self):
        print(f"parsing term, token: {self.current_token.get_value()}")
        expression = self._parse_boolean_factor()
        while self.current_token.get_token_type() == Token.Type.AND:
            self._consume_next_token()
            right = self._parse_boolean_factor()
            expression = Parser.AndNode(expression, right)
        return expression

    def _parse_boolean_factor(self):
        print(f"parsing factor, token: {self.current_token.get_value()}")
        token = self._consume_next_token()
        true_or_false = [Token.Type.TT, Token.Type.FF]
        var_or_int = [Token.Type.IDENTIFIER, Token.Type.INTEGER]
        match token.get_token_type():
            case x if x in true_or_false:
                return Parser.BoolNode(True if x == Token.Type.TT else False)
            case Token.Type.NOT:
                expression = self._parse_boolean_expression()
                return Parser.NotNode(expression)
            case Token.Type.LEFT_BRACKET:
                expression = self._parse_boolean_expression()
                self._consume_token_type(Token.Type.RIGHT_BRACKET,
                                         "Expected ')'")
                return expression
            case x if x in var_or_int:
                ops = [Token.Type.EQUALS,
                       Token.Type.LESS_THAN,
                       Token.Type.LESS_OR_EQUAL,
                       Token.Type.GREATER_THAN,
                       Token.Type.GREATER_OR_EQUAL,
                       Token.Type.RIGHT_BRACKET]
                if self.current_token.get_token_type() in ops:
                    if token.get_token_type() == Token.Type.IDENTIFIER:
                        return self.VarNode(token.get_value())
                    else:
                        return self.IntNode(token.get_value())
                expression = self._parse_arithmetic_expression()
                return expression
            case _:
                raise SyntaxError(f"Unexpected token {token.get_value()}")