# import numpy as np
import sympy as sp

# The nomograph is set up as a list of x, y pairs of 3 curves
class Nomograph():
    def __init__(self, variables=3):
        self.variables = variables
        self.value_ranges = [(0, 1) for _ in range(variables)]
        # self.matrix = np.ones((3, 3))
        self.matrix = sp.Matrix([
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1]
        ])

    # Updates the range of one of the variables
    def update_range(self, index, new_range):
        if index < self.variables:
            self.value_ranges[index] = new_range

    # Scales the axes
    def scale(self, x, y):
        S = sp.Matrix([
            [x,   0,   0],
            [0,   y,   1],
            [0,   0,   1]
        ])

        self.matrix = self.matrix * S

    # Translates the axes
    def translate(self, x, y):
        T = sp.Matrix([
            [1,   0,   0],
            [0,   1,   0],
            [x,   y,   1]
        ])

        self.matrix = self.matrix * T

    # Rotates around the origin by and angle theta
    def rotate(self, theta):
        R = sp.Matrix([
            [sp.cos(theta), -sp.sin(theta), 0],
            [sp.sin(theta), sp.cos(theta),  0],
            [0,             0,              1]
        ])

        self.matrix = self.matrix * R

    # Shears the axes by their corresponding values
    def shear(self, theta_x, theta_y):
        S = sp.Matrix([
            [sp.cos(theta_x), sp.sin(theta_x),  0],
            [sp.sin(theta_y), sp.cos(theta_y),  0],
            [0,               0,                1]
        ])

        self.matrix = self.matrix * S

    # Flips the two axes (same as a rotation by 90 then a reflection)
    def flip(self):
        R = sp.Matrix([
            [0,   1,   0],
            [1,   0,   0],
            [0,   0,   1]
        ])

        self.matrix = self.matrix * R

    # Aligns an axis with a desired curve (if possible) TODO
    def align(self, index, x, y):
        pass

    # Reduced the matrix to a nomographic form TODO
    def reduce(self):
        pass

    # Draw the nomograph on a screen TODO
    def draw(self, canvas, variables=None):
        # if None, then draw all variables, otherwise just the indexes sent
        if variables == None:
            variables_to_draw = [i for i in range(self.variables)]
        else:
            variables_to_draw = variables[:]

def parallel_builder(F1, F2, F3, u1_range, u2_range, u3_range):
    nomo = Nomograph()

    nomo.update_range(0, u1_range)
    nomo.update_range(1, u2_range)
    nomo.update_range(2, u3_range)


class Parallel(Nomograph):
    def __init__(self, F1, F2, F3, u1_range, u2_range, u3_range):
        super().__init__()

        self.matrix = sp.Matrix([
            [F1, 0, 1],
            [F2, 1, 1],
            [0.5*F3, 0.5, 1]
        ])

        self.value_ranges = [u1_range, u2_range, u3_range]
