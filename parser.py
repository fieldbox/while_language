from lexer import Token, Lexer

class Parser:
    class ProgramNode:
        def __init__(self, statements): self.statements = statements

    class AssignStatementNode:
        def __init__(self, left, right):
            self.left = left
            self.right = right

    class IfStatementNode:
        def __init__(self, condition, if_body, else_body):
            self.condition = condition
            self.if_body = if_body
            self.else_body = else_body

    class WhileStatementNode:
        def __init__(self, condition, body):
            self.condition = condition
            self.body = body

    class ArithmeticExpressionNode:
        def __init__(self, left, operation, right):
            self.left = left
            self.operation = operation
            self.right = right

    class IntNode:
        def __init__(self, value): self.value = value

    class VarNode:
        def __init__(self, value): self.value = value

    def __init__(self, program):
        self.program = program
        self.position = 0
        self.current_token = self.program[self.position]

    def _consume_token(self, token_types, error_message):
        if self.current_token.get_token_type() in token_types:
            old_token = self.program[self.position]
            self.position += 1
            self.current_token = self.program[self.position]
            return old_token
        else:
            raise SyntaxError(error_message)

    def parse_program(self):
        statements = []
        while self.current_token.get_token_type() != Token.Type.EOF:
            stmt = self._parse_statement()
            self._consume_token([Token.Type.EOL], "Expected semicolon")
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
        left_token = self._consume_token([Token.Type.IDENTIFIER], "")
        self._consume_token([Token.Type.ASSIGNMENT], "Expected :=")
        right_token = self._consume_token([Token.Type.IDENTIFIER,
                                     Token.Type.INTEGER],
                                    "Expected identifier or integer")
        left_node = Parser.VarNode(left_token.get_value())
        if right_token.get_token_type() == Token.Type.IDENTIFIER:
            right_node = Parser.VarNode(right_token.get_value())
        else:
            right_node= Parser.IntNode(right_token.get_value())
        return Parser.AssignStatementNode(left_node, right_node)
