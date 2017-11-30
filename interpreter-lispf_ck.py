from getch import getche
import click
import pprint
import ox

lexer = ox.make_lexer([
    ('COMMENT', r';(.)*'),
    ('NEW_LINE', r'\n+'),
    ('OPEN_BRACKET', r'\('),
    ('CLOSE_BRACKET', r'\)'),
    ('NAME', r'[a-zA-Z_][a-zA-Z_0-9-]*'),
    ('NUMBER', r'\d+(\.\d*)?'),
])

token_list = [
    'NAME',
    'NUMBER',
    'OPEN_BRACKET',
    'CLOSE_BRACKET',
]

operator = lambda operator: (operator)

parser = ox.make_parser([

    ('tuple : OPEN_BRACKET term CLOSE_BRACKET', lambda openbracket, term, closebracket: term),
    ('tuple : OPEN_BRACKET CLOSE_BRACKET', lambda open_bracket, close_bracket: '()'),
    ('term : atom term', lambda term, other_term: (term, ) + other_term),
    ('term : atom', lambda term: (term, )),
    ('atom : tuple', operator),
    ('atom : NAME', lambda name: name),
    ('atom : NUMBER', lambda x: int(x)),

] , token_list)

data = [0]
ptr = 0
code_ptr = 0
breakpoints = []

@click.command()
@click.argument('source_file',type=click.File('r'))
def build(source_file):

    print_ast = pprint.PrettyPrinter(width=60, compact=True)
    source = source_file.read()

    tokens = lexer(source)
    # print('tokens:')
    # print(tokens)

    tokens = [value for value in tokens if str(value)[:7] != 'COMMENT' and str(value)[:8] != 'NEW_LINE']
    ast = parser(tokens)

    # print_ast.pprint(ast)
    print(ast)
    lf(ast, code_ptr, ptr)


def lf(source, code_ptr, ptr):

    for command in source:

        if isinstance(command, tuple):

            if command[0] == 'add':
                data[ptr] = (data[ptr] + int(command[1])) % 256;
            elif command[0] == 'sub':
                data[ptr] = (data[ptr] - int(command[1])) % 256;
            elif command[0] == 'do':
                i = 1
                while i < len(command):
                    lf(command[i], code_ptr, ptr)
                    i += 1
            elif command[0] == 'do-after':
                i = 0
                while i < len(command[2]):
                    tupla = ('do', command[1], command[2][i])
                    lf(tupla, code_ptr, ptr)
                    i += 1

            elif command[0] == 'do-before':
                i = 0
                while i < len(command[2]):
                    tupla = ('do', command[2][i], command[1])
                    lf(tupla, code_ptr, ptr)
                    i += 1
            elif command[0] == 'def':
                ...
            elif command[0] == 'loop':
                if data[ptr] != 0:
                    i = 1
                    while i < len(command):
                        lf(command, code_ptr, ptr)
                        i += 1

                        if data[ptr] == 0:
                            break

        elif command == 'inc':
            data[ptr] = (data[ptr] + 1) % 256;
        elif command == 'dec':
            data[ptr] = (data[ptr] - 1) % 256;
        elif command == 'right':
            ptr += 1
            if ptr == len(data):
                data.append(0)
        elif command == 'left':
            ptr -= 1
        elif command == 'print':
            print(chr(data[ptr]), end='')
        elif command == 'read':
            data[ptr] = ord(getche())

        code_ptr += 1

if __name__ == '__main__':
    build()
