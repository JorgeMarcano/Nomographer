import numpy as np
import sympy as sp
# from tkinter import Canvas


# The nomograph is set up as a list of x, y pairs of 3 curves
class Nomograph():
    def __init__(self, name, func_vars, *, other=None, funcs=None, ranges=None):
        self.name = name
        self.t = sp.symbols('t')

        self.funcs = ["t" for _ in func_vars] if (funcs is None) else [sp.parse_expr(func) for func in funcs]

        self.variables = max(func_vars) + 1

        self.value_ranges = [Ticks(0, 1, 0.25, 0.05) for _ in range(self.variables)]
        if not (ranges is None):
            for ind, val_range in enumerate(ranges):
                self.value_ranges[ind].min = val_range[0]
                self.value_ranges[ind].max = val_range[1]

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

        if not (other is None):
            self.copy(other)

        self.transform()

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
    def rotate(self, theta=None, deg=None):
        if not(deg is None):
            theta = deg * sp.pi / 180
        
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

    def project(self, xp, yp, zp):
        P = sp.Matrix([
            [zp,  yp,   1],
            [0,   -xp,  0],
            [0,   0,    -xp]
        ])

        # self.current_matrix = self.current_matrix * F
        # self.transformations.append(F)
        self.current_transformation = P

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
        # easiest way to reduce is simply divide each row by the last column's value
        is_ok = True
        for row in range(self.variables):
            temp_val = self.current_matrix[row, 2]
            if temp_val != 1:
                self.current_matrix[row, 0] /= temp_val
                self.current_matrix[row, 1] /= temp_val

    # Performs the transformations in the queue
    def transform(self):
        # self.current_matrix = self.base_matrix

        # for xfrm in self.transformations:
        #     self.current_matrix = self.current_matrix * xfrm
        self.current_matrix = self.base_matrix * self.transformation_matrix

        if self.current_transformation is not None:
            self.current_matrix = self.current_matrix * self.current_transformation

        self.reduce()

    def reset_transform(self):
        self.transformation_matrix = sp.Matrix([
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1]
        ])

    def get_transform(self):
        self.execute_last_transform()
        return self.current_transformation

    def set_transform(self, transformation):
        self.current_transformation = transformation
        self.transform()

    # Sets the base matrix and recomputes the transformations
    def set_base_matrix(self, base):
        self.base_matrix = base
        self.transform()

    # Draw the nomograph on a screen TODO
    def draw(self, draw_line_func, gui_draw_text, tick_size, variables=None):
        # if None, then draw all variables, otherwise just the indexes sent
        if variables is None:
            variables_to_draw = [i for i in range(self.variables)]
        else:
            variables_to_draw = variables[:]

        for var in variables_to_draw:
            x_func = np.vectorize(sp.lambdify(self.t, self.current_matrix[var, 0], "numpy"))
            y_func = np.vectorize(sp.lambdify(self.t, self.current_matrix[var, 1], "numpy"))

            dxdt = np.vectorize(sp.lambdify(self.t, sp.diff(self.current_matrix[var, 0], self.t), "numpy"))
            dydt = np.vectorize(sp.lambdify(self.t, sp.diff(self.current_matrix[var, 1], self.t), "numpy"))

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

            draw_line_func(self.name, points.tolist())

            # -----------------------------
            # Draw graduations of t
            # -----------------------------
            major_ticks, minor_ticks = self.value_ranges[var].get_ticks()
            px = x_func(major_ticks)
            py = y_func(major_ticks)

            angle = np.arctan2(-dxdt(major_ticks), dydt(major_ticks))
            mx = np.cos(angle)
            my = np.sin(angle)
            points = np.column_stack((major_ticks, px, py, mx, my))

            for ti, px, py, mx, my in points:
                p1x = px + 2*tick_size*mx
                p1y = py + 2*tick_size*my
                p2x = px - 2*tick_size*mx
                p2y = py - 2*tick_size*my

                draw_line_func(self.name, [[p1x, p1y], [p2x, p2y]])

                p1x = px + 4*tick_size*mx
                p1y = py + 4*tick_size*my

                # Label (parameter value)
                gui_draw_text(self.name, p1x, p1y, f"{ti:.2f}")

            px = x_func(minor_ticks)
            py = y_func(minor_ticks)

            angle = np.arctan2(-dxdt(minor_ticks), dydt(minor_ticks))
            mx = np.cos(angle)
            my = np.sin(angle)
            p1x = px + tick_size*mx
            p1y = py + tick_size*my
            p2x = px - tick_size*mx
            p2y = py - tick_size*my
            points = np.column_stack((minor_ticks, p1x, p1y, p2x, p2y, px, py))

            for ti, p1x, p1y, p2x, p2y, px, py in points:
                draw_line_func(self.name, [[p1x, p1y], [p2x, p2y]])

    def update_formula(self, index, func):
        if isinstance(func, str):
            self.funcs[index] = sp.parse_expr(func)
        elif isinstance(func, sp.Symbol):
            self.funcs[index] = func

    def copy(self, other):
        self.value_ranges = other.value_ranges[:]
        self.current_transformation = other.current_transformation
        self.transformation_matrix = other.transformation_matrix

        self.base_matrix = other.base_matrix

        for ind, func in enumerate(other.funcs):
            self.update_formula(ind, func)


class Parallel(Nomograph):
    index_of_func = [(0, 0), (1, 0), (2, 0)]

    def __init__(self, name, func_vars, *, other=None, funcs=None, ranges=None):
        super().__init__(name=name, func_vars=func_vars, funcs=funcs, ranges=ranges)

        if not(other is None):
            self.copy(other)

        self.base_matrix = sp.Matrix([
            [self.funcs[0], 0, 1],
            [self.funcs[1], 1, 1],
            [0.5*self.funcs[2], 0.5, 1]
        ])

        self.transform()

    def update_formula(self, index, func):
        super().update_formula(index, func)

        if index != 2:
            self.base_matrix[Parallel.index_of_func[index]] = self.funcs[index]

        else:
            self.base_matrix[Parallel.index_of_func[index]] = 0.5*self.funcs[index]

        self.transform()


class Z_Chart(Nomograph):
    def __init__(self, name, func_vars, *, other=None, funcs=None, ranges=None):
        super().__init__(name=name, func_vars=func_vars, funcs=funcs, ranges=ranges)

        if not(other is None):
            self.copy(other)

        self.base_matrix = sp.Matrix([
            [0, self.funcs[0], 1],
            [self.funcs[1] / (1+self.funcs[1]), 0, 1],
            [1, -self.funcs[2], 1]
        ])

        self.transform()

    def update_formula(self, index, func):
        super().update_formula(index, func)

        if index == 0:
            self.base_matrix[0, 1] = self.funcs[index]
        elif index == 1:
            self.base_matrix[1, 0] = self.funcs[index] / (1+self.funcs[index])
        elif index == 2:
            self.base_matrix[2, 1] = -1*self.funcs[index]

        self.transform()

class Concurrent(Nomograph):
    def __init__(self, name, func_vars, *, other=None, funcs=None, ranges=None):
        super().__init__(name=name, func_vars=func_vars, funcs=funcs, ranges=ranges)

        if not(other is None):
            self.copy(other)

        self.base_matrix = sp.Matrix([
            [self.funcs[0], 0, 1],
            [self.funcs[1], self.funcs[1], 1],
            [0, self.funcs[2], 1]
        ])

        self.transform()

    def update_formula(self, index, func):
        super().update_formula(index, func)

        if index == 0:
            self.base_matrix[0, 0] = self.funcs[index]
        elif index == 1:
            self.base_matrix[1, 0] = self.funcs[index]
            self.base_matrix[1, 1] = self.funcs[index]
        elif index == 2:
            self.base_matrix[2, 1] = self.funcs[index]

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
