import numpy as np
import sympy as sp
# from tkinter import Canvas


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

        self.transformation_matrix = sp.Matrix([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])
        # self.transformations = []
        self.current_transformation = None

        self.current_matrix = self.base_matrix

    # Updates the range of one of the variables
    def update_range(self, index, new_range):
        if index < self.variables:
            self.value_ranges[index] = new_range

    # Scales the axes
    def scale(self, x, y):
        S = sp.Matrix([
            [x,   0,   0],
            [0,   y,   0],
            [0,   0,   1]
        ])

        # self.current_matrix = self.current_matrix * S
        # self.transformations.append(S)
        self.current_transformation = S

    # Scales the axes while keeping a point without moving
    def scale_at_point(self, sx, sy, px, py):
        S = sp.Matrix([
            [sx,        0,          0],
            [0,         sy,         0],
            [(1-sx)*px, (1-sy)*py,  1]
        ])

        # self.current_matrix = self.current_matrix * S
        # self.transformations.append(S)
        self.current_transformation = S

    # Translates the axes
    def translate(self, x, y):
        T = sp.Matrix([
            [1,   0,   0],
            [0,   1,   0],
            [x,   y,   1]
        ])

        # self.current_matrix = self.current_matrix * T
        # self.transformations.append(T)
        self.current_transformation = T

    # Rotates around the origin by and angle theta
    def rotate(self, theta):
        R = sp.Matrix([
            [sp.cos(theta), -sp.sin(theta), 0],
            [sp.sin(theta), sp.cos(theta),  0],
            [0,             0,              1]
        ])

        # self.current_matrix = self.current_matrix * R
        # self.transformations.append(R)
        self.current_transformation = R

    # Shears the axes by their corresponding values
    def shear(self, theta_x, theta_y):
        S = sp.Matrix([
            [sp.cos(theta_x), sp.sin(theta_x),  0],
            [sp.sin(theta_y), sp.cos(theta_y),  0],
            [0,               0,                1]
        ])

        # self.current_matrix = self.current_matrix * S
        # self.transformations.append(S)
        self.current_transformation = S

    # Flips the two axes (same as a rotation by 90 then a reflection)
    def flip(self):
        F = sp.Matrix([
            [0,   1,   0],
            [1,   0,   0],
            [0,   0,   1]
        ])

        # self.current_matrix = self.current_matrix * F
        # self.transformations.append(F)
        self.current_transformation = F

    def execute_last_transform(self):
        if self.current_transformation is None:
            return

        # self.transformations.append(self.current_transformation)
        self.transformation_matrix = self.transformation_matrix * self.current_transformation
        self.current_transformation = None

        self.transform()

    # Aligns an axis with a desired curve (if possible) TODO
    def align(self, index, x, y):
        pass

    # Reduced the matrix to a nomographic form TODO
    def reduce(self):
        pass

    # Performs the transformations in the queue
    def transform(self):
        # self.current_matrix = self.base_matrix

        # for xfrm in self.transformations:
        #     self.current_matrix = self.current_matrix * xfrm
        self.current_matrix = self.base_matrix * self.transformation_matrix

        if self.current_transformation is not None:
            self.current_matrix = self.current_matrix * self.current_transformation

    def reset_transform(self):
        self.transformation_matrix = sp.Matrix([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])

    # Sets the base matrix and recomputes the transformations
    def set_base_matrix(self, base):
        self.base_matrix = base
        self.transform()

    # Draw the nomograph on a screen TODO
    def draw(self, canvas, width, height, variables=None):
        # if None, then draw all variables, otherwise just the indexes sent
        if variables is None:
            variables_to_draw = [i for i in range(self.variables)]
        else:
            variables_to_draw = variables[:]

        # CENTER_X = width // 2
        # CENTER_Y = height // 2
        # SCALE = 100

        # Axes
        # canvas.create_line(0, CENTER_Y, width, CENTER_Y, fill="gray")
        # canvas.create_line(CENTER_X, 0, CENTER_X, height, fill="gray")

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

                # cx = CENTER_X + x * SCALE
                # cy = CENTER_Y - y * SCALE
                # cx = x * SCALE
                # cy = y * SCALE

                # points.extend([x, y])
                points.extend([x, y])

            canvas.create_line(points, fill="blue", width=2, smooth=True)

            # -----------------------------
            # Draw graduations of t
            # -----------------------------
            graduation_step = 250      # every N points
            marker_radius = 3

            marker_set = set(range(0, num_points, graduation_step))
            # Add last point to ensure label is placed for it too
            marker_set.add(num_points - 1)
            for i in marker_set:
                ti = ts[i]
                x = x_func(ti)
                y = y_func(ti)

                # cx = CENTER_X + x * SCALE
                # cy = CENTER_Y - y * SCALE
                # cx = x * SCALE
                # cy = y * SCALE

                # Marker
                canvas.create_oval(
                    x - marker_radius, y - marker_radius,
                    x + marker_radius, y + marker_radius,
                    fill="red", outline=""
                )

                # Label (parameter value)
                canvas.create_text(
                    x + 10, y - 10,
                    text=f"{ti:.2f}",
                    font=("Arial", 8),
                    fill="black"
                )

    def update_formula(self, index, func):
        pass


class Parallel(Nomograph):
    def __init__(self, funcs, ranges):
        super().__init__()

        for ind, val_range in enumerate(ranges):
            self.update_range(ind, val_range)

        self.base_matrix = sp.Matrix([
            [sp.parse_expr(funcs[0]), 0, 1],
            [sp.parse_expr(funcs[1]), 1, 1],
            [0.5*sp.parse_expr(funcs[2]), 0.5, 1]
        ])

        self.index_of_func = [(0, 0), (1, 0), (2, 0)]

        self.transform()

    def update_formula(self, index, func):
        self.base_matrix[self.index_of_func[index]] = func

        self.transform()
