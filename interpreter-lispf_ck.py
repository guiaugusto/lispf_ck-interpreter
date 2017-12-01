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

identity = lambda x: x

parser = ox.make_parser([

    ('tuple : OPEN_BRACKET elements CLOSE_BRACKET', lambda a, x, b: x),
    ('tuple : OPEN_BRACKET CLOSE_BRACKET', lambda a, b: '[]'),
    ('elements : term elements', lambda x, xs: [x] + xs),
    ('elements : term', lambda x: [x]),
    ('term : atom', identity),
    ('term : tuple', identity),
    ('atom : NAME', identity),
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

    tokens = [value for value in tokens if str(value)[:7] != 'COMMENT' and str(value)[:8] != 'NEW_LINE']
    ast = parser(tokens)

    print_ast.pprint(ast)
    lf(ast, ptr)

function_definition = {}

def lf(source, ptr):

    for command in source:

        if isinstance(command, list):

            if command[0] == 'add':
                data[ptr] = (data[ptr] + int(command[1])) % 256;
            elif command[0] == 'sub':
                data[ptr] = (data[ptr] - int(command[1])) % 256;
            elif command[0] == 'do':
                i = 1
                while i < len(command):
                    lf(command[i], ptr)
                    i += 1
            elif command[0] == 'do-after':
                i = 0
                while i < len(command[2]):
                    lista = ['do', command[1], command[2][i]]
                    lf(tupla, ptr)
                    i += 1

            elif command[0] == 'do-before':
                i = 0
                while i < len(command[2]):
                    lista = ['do', command[2][i], command[1]]
                    lf(lista, ptr)
                    i += 1
            elif command[0] == 'def':
                function_definition[command[1]] = [command[2], command[3]]
            elif command[0] == 'loop':
                if data[ptr] != 0:
                    i = 1
                    while i < len(command):
                        lf(command, ptr)
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
        elif command in function_definition:
            # print(function_definition[command][1])
            lista = function_definition[command][1]
            lf(lista, ptr)


if __name__ == '__main__':
    build()
