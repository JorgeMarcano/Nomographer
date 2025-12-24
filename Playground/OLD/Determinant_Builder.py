import sympy as sp
import numpy as np
from sympy.parsing.sympy_parser import parse_expr

variable_count = int(input("How many variables (max 5)? "))
variable_list = ["u", "v", "w", "s", "t"]
variable_list = variable_list[:variable_count]

# Define symbols
vars = []
for var in variable_list:
    vars.append(sp.symbols(var))

print(f"Use the variables '{', '.join(variable_list)}'")

# Parse the string into a SymPy expression
formula = input("Formula: ")

left_str, right_str = formula.split("=")
left = parse_expr(left_str)
right = parse_expr(right_str)

equation = sp.Eq(left, right)
print(equation)

# # Convert to a fast numerical function
# f = sp.lambdify(vars, expr, modules=["numpy"])

while True:
    subs = {}
    for i in variable_list[:-1]:
        subs[i] = float(input(f"{i} = "))

    output = sp.solve(equation.subs(subs), vars[-1])
    print(output)
