import tkinter as tk
import sympy as sp
import numpy as np

# -----------------------------
# Symbolic parametric functions
# -----------------------------
t = sp.symbols('t')

x_sym = sp.cos(t)
y_sym = sp.sin(2 * t)

x_func = sp.lambdify(t, x_sym, "numpy")
y_func = sp.lambdify(t, y_sym, "numpy")

# -----------------------------
# Tkinter setup
# -----------------------------
WIDTH, HEIGHT = 600, 600
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
SCALE = 200

root = tk.Tk()
root.title("Parametric Curve with Parameter Graduation")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack()

# Axes
canvas.create_line(0, CENTER_Y, WIDTH, CENTER_Y, fill="gray")
canvas.create_line(CENTER_X, 0, CENTER_X, HEIGHT, fill="gray")

# -----------------------------
# Parameter range
# -----------------------------
t_min, t_max = 0, 2 * np.pi
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

    points.extend([cx, cy])

canvas.create_line(points, fill="blue", width=2, smooth=True)

# -----------------------------
# Draw graduations of t
# -----------------------------
graduation_step = 100      # every N points
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

root.mainloop()
