import sympy as sp
import numpy as np

# Define symbols
x = sp.symbols('x')

# Parse the string into a SymPy expression
expr = sp.sympify(formula)

# Convert to a fast numerical function
f = sp.lambdify(x, expr, modules=["numpy"])

from sympy import Eq
from sympy.parsing.sympy_parser import parse_expr

eq_str = "2*x + 3 = 7"

left_str, right_str = eq_str.split("=")

left = parse_expr(left_str)
right = parse_expr(right_str)

equation = Eq(left, right)
print(equation)
