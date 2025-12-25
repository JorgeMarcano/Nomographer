import numpy as np
import sympy as sp
from tkinter import Canvas


# The nomograph is set up as a list of x, y pairs of 3 curves
class Nomograph():
    def __init__(self, variables=3):
        self.t = sp.symbols('t')

        self.variables = variables
        self.value_ranges = [(0, 1) for _ in range(variables)]

        self.base_matrix = sp.Matrix([
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1]
        ])

        self.transformations = []

        self.current_matrix = self.base_matrix

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

        self.current_matrix = self.current_matrix * S
        self.transformations.append(S)

    # Translates the axes
    def translate(self, x, y):
        T = sp.Matrix([
            [1,   0,   0],
            [0,   1,   0],
            [x,   y,   1]
        ])

        self.current_matrix = self.current_matrix * T
        self.transformations.append(T)

    # Rotates around the origin by and angle theta
    def rotate(self, theta):
        R = sp.Matrix([
            [sp.cos(theta), -sp.sin(theta), 0],
            [sp.sin(theta), sp.cos(theta),  0],
            [0,             0,              1]
        ])

        self.current_matrix = self.current_matrix * R
        self.transformations.append(R)

    # Shears the axes by their corresponding values
    def shear(self, theta_x, theta_y):
        S = sp.Matrix([
            [sp.cos(theta_x), sp.sin(theta_x),  0],
            [sp.sin(theta_y), sp.cos(theta_y),  0],
            [0,               0,                1]
        ])

        self.current_matrix = self.current_matrix * S
        self.transformations.append(S)

    # Flips the two axes (same as a rotation by 90 then a reflection)
    def flip(self):
        F = sp.Matrix([
            [0,   1,   0],
            [1,   0,   0],
            [0,   0,   1]
        ])

        self.current_matrix = self.current_matrix * F
        self.transformations.append(F)

    # Aligns an axis with a desired curve (if possible) TODO
    def align(self, index, x, y):
        pass

    # Reduced the matrix to a nomographic form TODO
    def reduce(self):
        pass

    # Performs the transformations in the queue
    def transform(self):
        self.current_matrix = self.base_matrix

        for xfrm in self.transformations:
            self.current_matrix = self.current_matrix * xfrm

    # Sets the base matrix and recomputes the transformations
    def set_base_matrix(self, base):
        self.base_matrix = base
        self.transform()

    # Draw the nomograph on a screen TODO
    def draw(self, canvas, width, height, variables=None):
        # if None, then draw all variables, otherwise just the indexes sent
        if variables == None:
            variables_to_draw = [i for i in range(self.variables)]
        else:
            variables_to_draw = variables[:]

        CENTER_X = width // 2
        CENTER_Y = height // 2
        SCALE = 100

        # Axes
        canvas.create_line(0, CENTER_Y, width, CENTER_Y, fill="gray")
        canvas.create_line(CENTER_X, 0, CENTER_X, height, fill="gray")

        for var in variables_to_draw:
            x_func = sp.lambdify(self.t, self.current_matrix[var, 0], "numpy")
            y_func = sp.lambdify(self.t, self.current_matrix[var, 1], "numpy")

            # -----------------------------
            # Parameter range
            # -----------------------------
            t_min = self.value_ranges[var][0]
            t_max = self.value_ranges[var][1]
            num_points = 1000
            ts = np.linspace(t_min, t_max, num_points)

            # -----------------------------
            # Draw curve
            # -----------------------------
            points = []

            for ti in ts:
                x = x_func(ti)
                y = y_func(ti)

                cx = CENTER_X + x * SCALE
                cy = CENTER_Y - y * SCALE

                # points.extend([x, y])
                points.extend([cx, cy])

            canvas.create_line(points, fill="blue", width=2, smooth=True)

            # -----------------------------
            # Draw graduations of t
            # -----------------------------
            graduation_step = 250      # every N points
            marker_radius = 3

            for i in range(0, num_points, graduation_step):
                ti = ts[i]
                x = x_func(ti)
                y = y_func(ti)

                cx = CENTER_X + x * SCALE
                cy = CENTER_Y - y * SCALE

                # Marker
                canvas.create_oval(
                    cx - marker_radius, cy - marker_radius,
                    cx + marker_radius, cy + marker_radius,
                    fill="red", outline=""
                )

                # Label (parameter value)
                canvas.create_text(
                    cx + 10, cy - 10,
                    text=f"{ti:.2f}",
                    font=("Arial", 8),
                    fill="black"
                )


def parallel_builder(F1, F2, F3, u1_range, u2_range, u3_range, nomo=None):
    if nomo == None:
        nomo = Nomograph()

    nomo.update_range(0, u1_range)
    nomo.update_range(1, u2_range)
    nomo.update_range(2, u3_range)



    matrix = sp.Matrix([
        [sp.parse_expr(F1), 0, 1],
        [sp.parse_expr(F2), 1, 1],
        [0.5*sp.parse_expr(F3), 0.5, 1]
    ])

    nomo.set_base_matrix(matrix)

    return nomo
