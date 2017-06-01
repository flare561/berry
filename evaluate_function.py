from collections import namedtuple
import math
import re


Operator = namedtuple('Operator', ['name', 'function', 'associativity', 'precedence'])
Function = namedtuple('Function', ['name', 'function', 'arity'])
reg = re.compile('''((?:-?[0-9.]+)|(?:[a-zA-Z]+)|(?:\+|\-|\/|\*|\^|\(|\)|,|%))''')

operators = {
    '+': Operator('+', lambda a, b: a + b, associativity='left', precedence=2),
    '-': Operator('-', lambda a, b: a - b, associativity='left', precedence=2),
    '*': Operator('*', lambda a, b: a * b, associativity='left', precedence=3),
    '/': Operator('/', lambda a, b: a / b, associativity='left', precedence=3),
    '^': Operator('^', lambda a, b: a ** b, associativity='right', precedence=4),
    '%': Operator('%', lambda a, b: a % b, associativity='left', precedence=3)
    }

functions = {
    'min': Function('min', min, arity=2),
    'max': Function('max', max, arity=2),
    'sqrt': Function('sqrt', math.sqrt, arity=1),
    'floor': Function('floor', math.floor, arity=1),
    'ceil': Function('ceil', math.ceil, arity=1),
    'sin': Function('sin', math.sin, arity=1),
    'cos': Function('cos', math.cos, arity=1),
    'tan': Function('tan', math.tan, arity=1),
    'asin': Function('asin', math.asin, arity=1),
    'acos': Function('acos', math.acos, arity=1),
    'atan': Function('atan', math.atan, arity=1),
    'pi': Function('pi', lambda: math.pi, arity=0),
    'e': Function('e', lambda: math.e, arity=0),
    'ln': Function('ln', math.log, arity=1),
    'log': Function('log', math.log10, arity=1)
    }


def parse_infix(equation):
    matches = reg.findall(equation)
    prev = None
    for match in matches:
        try:
            if float(match) < 0 and prev is not None and float(prev):
                yield '+'
        except ValueError:
            pass
        prev = match
        yield match


def shunting_yard(equation):
    stack = []
    for item in equation:
        if item in operators:
            op = operators[item]
            while (stack and
                   ((type(stack[-1]) is Operator and
                    (op.associativity == 'left' and
                     stack[-1].precedence >= op.precedence) or
                    (op.associativity == 'right' and
                     stack[-1].precedence > op.precedence)) or
                    type(stack[-1]) is Function)):
                yield stack.pop()
            stack.append(op)
        elif item == ',':
            while stack and stack[-1] != '(':
                yield stack.pop()
            if not stack or (stack and stack[-1] != '('):
                raise ValueError("Unexpected Argument Separator Or Mismatched Parenthesis")
        elif item in functions:
            stack.append(functions[item])
        elif item == '(':
            stack.append('(')
        elif item == ')':
            while stack and stack[-1] != '(':
                yield stack.pop()
            if stack and stack[-1] == '(':
                stack.pop()
            else:
                raise ValueError("Mismatched Parenthesis")
            if stack and type(stack[-1]) is Function:
                yield stack.pop()
        else:
            yield float(item)
    while stack and stack[-1] != '(':
        yield stack.pop()
    if stack:
        raise(ValueError("Mismatched Parenthesis"))


def evaluate(parsed_equation):
    stack = []
    for item in parsed_equation:
        if type(item) is Operator:
            b = stack.pop()
            a = stack.pop()
            stack.append(item.function(a, b))
        elif type(item) is Function:
            if item.arity > 0:
                params = stack[-item.arity:]
                del stack[-item.arity:]
                if len(params) != item.arity:
                    raise ValueError("Inappropriate number of function arguments")
            else:
                params = []
            stack.append(item.function(*params))
        else:
            stack.append(item)
    if len(stack) > 1:
        raise ValueError("Invalid function")
    return stack[0]


def solve_equation(input_equation):
    parsed_infix = parse_infix(input_equation)
    parsed_postfix = shunting_yard(parsed_infix)
    return evaluate(parsed_postfix)
