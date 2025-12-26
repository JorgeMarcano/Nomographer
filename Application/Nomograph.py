import numpy as np
import sympy as sp
# from tkinter import Canvas


# The nomograph is set up as a list of x, y pairs of 3 curves
class Nomograph():
    def __init__(self, variables=3):
        self.t = sp.symbols('t')

        self.variables = variables
        self.value_ranges = [Ticks(0, 1, 0.25, 0.05) for _ in range(variables)]

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

    # Gets the ranges of the desired variables
    def get_tick(self, index):
        if index >= self.variables:
            return None

        return self.value_ranges[index]

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
            x_func = np.vectorize(sp.lambdify(self.t, self.current_matrix[var, 0], "numpy"))
            y_func = np.vectorize(sp.lambdify(self.t, self.current_matrix[var, 1], "numpy"))

            # -----------------------------
            # Parameter range
            # -----------------------------
            t_min = self.value_ranges[var].min
            t_max = self.value_ranges[var].max
            num_points = 1000
            ts = np.linspace(t_min, t_max, num_points)

            # -----------------------------
            # Draw curve
            # -----------------------------
            points = np.column_stack((x_func(ts), y_func(ts)))

            canvas.create_line(points.tolist(), fill="blue", width=2, smooth=True)

            # -----------------------------
            # Draw graduations of t
            # -----------------------------
            marker_radius = 3

            major_ticks, minor_ticks = self.value_ranges[var].get_ticks()
            points = np.column_stack((major_ticks, x_func(major_ticks), y_func(major_ticks)))
            for ti, x, y in points:
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

            marker_radius = 2

            minor_ticks = self.value_ranges[var].get_min_ticks()
            points = np.column_stack((minor_ticks, x_func(minor_ticks), y_func(minor_ticks)))
            for ti, x, y in points:
                # Marker
                canvas.create_oval(
                    x - marker_radius, y - marker_radius,
                    x + marker_radius, y + marker_radius,
                    fill="green", outline=""
                )

    def update_formula(self, index, func):
        pass


class Parallel(Nomograph):
    def __init__(self, funcs, ranges):
        super().__init__()

        for ind, val_range in enumerate(ranges):
            self.value_ranges[ind].min = val_range[0]
            self.value_ranges[ind].max = val_range[1]

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


class Ticks():
    def __init__(self, minimum, maximum, maj_tick, min_tick, is_log=False):
        self.min = minimum
        self.max = maximum
        self.maj_tick = maj_tick
        self.min_tick = min_tick
        self.is_log = is_log

    def get_maj_ticks(self):
        if not self.is_log and self.maj_tick <= 0:
            return np.array([])
        elif self.is_log and self.maj_tick <= 1:
                return np.array([])

        temp = self.min

        ticks = []
        while temp < self.max:
            ticks.append(temp)

            if not self.is_log:
                temp += self.maj_tick
            else:
                temp *= self.maj_tick

        ticks.append(self.max)

        return np.array(ticks)

    def get_min_ticks(self, major_ticks=None):
        if not self.is_log and self.min_tick <= 0:
            return np.array([])
        elif self.is_log and self.min_tick <= 1:
                return np.array([])

        if major_ticks is None:
            major_ticks = []

        temp = self.min

        ticks = []
        while temp < self.max:
            if temp not in major_ticks:
                ticks.append(temp)

            if not self.is_log:
                temp += self.min_tick
            else:
                temp *= self.min_tick

        ticks.append(self.max)

        return np.array(ticks)

    def get_ticks(self):
        major_ticks = self.get_maj_ticks()
        minor_ticks = self.get_min_ticks(major_ticks)

        return major_ticks, minor_ticks

    def set_max(self, new_max):
        self.max = max(self.min, new_max)
        return self.max

    def set_min(self, new_min):
        self.min = min(self.max, new_min)
        return self.min

    def set_major_tick(self, new_val):
        if not self.is_log:
            self.maj_tick = max(new_val, 0)
        else:
            self.maj_tick = max(new_val, 1)
        return self.maj_tick

    def set_minor_tick(self, new_val):
        if not self.is_log:
            self.min_tick = max(new_val, 0)
        else:
            self.min_tick = max(new_val, 1)
        return self.min_tick
