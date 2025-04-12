"""Implements the Token and Lexer classes to perform lexical analysis on WHILE programs.

Classes:
Token -- Describes the tokens returned by the lexer.
Lexer -- Describes the lexer object, which takes in a WHILE program and
can return tokens from that program one-by-one
"""

from enum import Enum

class Token:
    """Describes tokens that will be returned by the lexer.
    Classes:
    Type -- Describes each type of token in the WHILE language.

    Methods:
    __init__() -- Constructor method that takes in the value and type
    of the token to be assigned.
    get_value() -- Returns the value of the token.
    get_token_type() -- Returns the type of the token.
    """
    class Type(Enum):
        """Describes each type that a token can take in the WHILE language.
        """
        INTEGER = 1
        IDENTIFIER = 2
        PLUS = 3
        MINUS = 4
        TIMES = 5
        FF = 6
        TT = 7
        EQUALS = 8
        LESS_THAN = 9
        GREATER_THAN = 10
        LESS_OR_EQUAL = 11
        GREATER_OR_EQUAL = 12
        NOT = 13
        AND = 14
        ASSIGNMENT = 15
        SKIP = 16
        EOL = 17
        IF = 18
        THEN = 19
        ELSE = 20
        WHILE = 21
        DO = 22
        EOF = 23
        LEFT_BRACKET = 24
        RIGHT_BRACKET = 25
        END = 26

    def __init__(self, value, token_type: Type) -> None:
        """Assigns value and token type from input."""
        self._value = value
        self._token_type = token_type

    def get_value(self):
        """Returns the value of the token."""
        return self._value

    def get_token_type(self) -> Type:
        """Returns the type of the token."""
        return self._token_type

class Lexer:
    """Describes the lexer, which takes in a WHILE program as input,
    and outputs the tokens from that program one-by-one using the next_token() method.

    Methods:
    __init__() -- Constructor method that takes in a program as a string.
    next_token() -- Returns the next token in the given input.
    """

    # Lists all keywords and their associated token types.
    _keywords = {"ff": Token.Type.FF,
                 "tt": Token.Type.TT,
                 "skip": Token.Type.SKIP,
                 "if": Token.Type.IF,
                 "then": Token.Type.THEN,
                 "else": Token.Type.ELSE,
                 "while": Token.Type.WHILE,
                 "do": Token.Type.DO,
                 "end": Token.Type.END}

    # Lists all operators that are two characters or longer and their
    # associated token types.
    _long_operators = {":=": Token.Type.ASSIGNMENT,
                       "<=": Token.Type.LESS_OR_EQUAL,
                       ">=": Token.Type.GREATER_OR_EQUAL}

    # Lists all special characters and their associated token types.
    _special_characters = {"+": Token.Type.PLUS,
                           "-": Token.Type.MINUS,
                           "*": Token.Type.TIMES,
                           "=": Token.Type.EQUALS,
                           "<": Token.Type.LESS_THAN,
                           ">": Token.Type.GREATER_THAN,
                           "¬": Token.Type.NOT,
                           "^": Token.Type.AND,
                           ";": Token.Type.EOL,
                           "(": Token.Type.LEFT_BRACKET,
                           ")": Token.Type.RIGHT_BRACKET}

    def __init__(self, string: str) -> None:
        """Constructor method that takes in a WHILE program as a string,
        and sets the lexer's position to the beginning of the string."""
        self._string = string
        self._position = 0
        self._char = self._string[self._position]

    def _next_char(self) -> None:
        # Moves the lexer to the next character in the string. IF we
        # have reached the end of the string, set the character to None.
        self._position += 1
        if self._position < len(self._string):
            self._char = self._string[self._position]
        else:
            self._char = None

    def _next_chars(self, i: int) -> str:
        # Moves the lexer i chars along and returns the characters it
        # moved over as a string.
        original_position = self._position
        self._position += i
        if self._position < len(self._string):
            self._char = self._string[self._position]
        else:
            self._char = None
        return self._string[original_position:self._position]

    def _previous_chars(self, i: int) -> None:
        # Moves the lexer i chars backwards.
        self._position -= i
        self._char = self._string[self._position]

    def _match_keyword(self, keyword: str, token_type: Token.Type) -> Token | bool:
        # Attempts to match a given keyword from where the lexer
        # currently is. IF it can match it, return the token.
        # Otherwise, return False.

        length = len(keyword)

        # Move the lexer to the end of where the keyword would be, plus one
        # character (to see if there are any characters after the keyword
        # that would make it an identifier).
        next_chars = self._next_chars(length + 1)

        # If this string starts with the keyword, and either contains
        # only the keyword or ends in whitespace or a semicolon...
        if (next_chars[:length] == keyword and
           (len(next_chars) == length or next_chars[length].isspace()
           or next_chars[length] == ";")):

            # Move the lexer back by one character, to not consume the
            # semicolon/whitespace after the keyword
            self._previous_chars(1)

            # Return the token corresponding with the keyword.
            return Token(keyword, token_type)

        # Move the lexer back, since we did not
        # successfully match the keyword.
        self._previous_chars(length + 1)
        return False # Return False, since we did not find the keyword.

    def _match_long_operator(self, operator: str, token_type: Token.Type) -> Token | bool:
        # Attempts to match a given operator from where the lexer
        # currently is. IF it can match it, return the token.
        # Otherwise, return False.

        # This method is separate from _match_keyword because keywords can only
        # be followed by whitespace, otherwise they become identifiers.
        # Meanwhile, operators can be followed by other characters, so they
        # require a separate method to match them properly.

        # Move the lexer to the end of where the operator would be.
        next_chars = self._next_chars(len(operator))

        # If this string is the operator...
        if next_chars == operator:

            # Return the token corresponding with the operator.
            return Token(operator, token_type)

        # Move the lexer back, since we did not
        # successfully match the operator.
        self._previous_chars(len(operator))
        return False # Return False, since we did not find the operator.

    def next_token(self) -> Token:
        """Gets the next token in the WHILE program, and moves the
        lexer's position to after that token.
        """

        # Match EOF token
        if self._char is None:
            return Token(None, Token.Type.EOF)

        # Remove whitespace
        while self._char.isspace():
            self._next_char()

        # Match keyword tokens
        for key, value in self._keywords.items():
            if self._char == key[0]:
                token = self._match_keyword(key, value)
                if token is not False:
                    return token

        # Match long operator tokens
        for key, value in self._long_operators.items():
            if self._char == key[0]:
                token = self._match_long_operator(key, value)
                if token is not False:
                    return token

        # Match special character tokens
        for key, value in self._special_characters.items():
            if self._char == key:
                self._next_char()
                return Token(key, value)

        # Any symbols now will be invalid characters
        if not self._char.isalnum():
            print(self._char)
            raise SyntaxError("Invalid character")

        # Match integer token
        if self._char.isdigit() or self._char == '-':
            num = self._char
            self._next_char()

            # Keep eating characters until whitespace, EOF or a special character is hit
            while not (self._char is None or self._char.isspace()
                       or self._char in self._special_characters):
                if self._char.isdigit():
                    num += self._char
                    self._next_char()
                else:
                    raise SyntaxError("Expected digit")
            return Token(int(num), Token.Type.INTEGER)

        # If no other tokens have been matched, this is an identifier token
        identifier = self._char
        self._next_char()
        while not (self._char is None or self._char.isspace() or not self._char.isalnum()):
            identifier += self._char
            self._next_char()
        return Token(identifier, Token.Type.IDENTIFIER)

if __name__ == "__main__":
    program = input("Input program on one line\n")
    lexer = Lexer(program)
    tokens = []
    while True:
        token = lexer.next_token()
        tokens.append((token.get_value(), token.get_token_type().name))
        if token.get_token_type() == Token.Type.EOF:
            break
    print(tokens)
