import tkinter as tk
from tkinter import ttk

def create_formula_window(root):
    block = ttk.Frame(formula_frame)
    block.pack(side="top", fill="x", pady=6)

    # Formula entry
    row1 = ttk.Frame(block)
    row1.pack(fill="x")

    ttk.Label(row1, text=f"Formula:").pack(side="left")

    formula_entry = ttk.Entry(row1)
    formula_entry.pack(side="left", fill="x", expand=True, padx=5)
    formula_entry.bind("<Return>", on_formula_change)

    # Scale
    scale_var = tk.DoubleVar(value=0.0)
    scale = ttk.Scale(
        block,
        from_=0,
        to=1,
        orient="horizontal",
        variable=scale_var,
        command=lambda v: on_formula_change()
    )
    scale.pack(fill="x", padx=20)

    # Min / Max entries
    row3 = ttk.Frame(block)
    row3.pack(fill="x", padx=20)

    ttk.Label(row3, text="min").pack(side="left")
    min_entry = ttk.Entry(row3, width=6)
    min_entry.pack(side="left", padx=(2, 10))
    min_entry.bind("<Return>", on_formula_change)

    ttk.Label(row3, text="max").pack(side="left")
    max_entry = ttk.Entry(row3, width=6)
    max_entry.pack(side="left", padx=(2, 0))
    max_entry.bind("<Return>", on_formula_change)

    return {
        "formula": formula_entry,
        "scale": scale_var,
        "min": min_entry,
        "max": max_entry
    }

def on_formula_change(event=None):
    """
    Called when:
    - Enter is pressed in any entry
    - A radio button selection changes
    """

    active = selected_type.get()

    formulas = [f["formula"].get() for f in formula_widgets]
    mins = [f["min"].get() for f in formula_widgets]
    maxs = [f["max"].get() for f in formula_widgets]
    scales = [f["scale"].get() for f in formula_widgets]

    print("Active formula:", active + 1)
    for i in range(3):
        print(
            f"Formula {i+1}: {formulas[i]} | "
            f"min={mins[i]} max={maxs[i]} scale={scales[i]}"
        )
    print("-" * 40)

    # This is where you would:
    # - parse the formula
    # - evaluate or plot it
    # - redraw the canvas

# Main window
root = tk.Tk()
root.title("Formula Evaluator")
root.geometry("700x450")

# ---- Top container ----
top_frame = ttk.Frame(root, padding=10)
top_frame.pack(side="top", fill="x")

# Left: formula entries
formula_frame = ttk.Frame(top_frame)
formula_frame.pack(side="left", fill="x", expand=True)

formula_widgets = []

for i in range(3):
    formula_widgets.append(create_formula_window(formula_frame))

# Right: radio buttons
radio_frame = ttk.Frame(top_frame, padding=(10, 0))
radio_frame.pack(side="right", fill="y")

selected_type = tk.IntVar(value=0)

ttk.Label(radio_frame, text="Type").pack(anchor="w")

types = ["//", "Z/N", "prop", "conc", "det"]
for ind, type in enumerate(types):
    rb = ttk.Radiobutton(
        radio_frame,
        text=type,
        variable=selected_type,
        value=ind,
        command=on_formula_change  # Called when selection changes
    )
    rb.pack(anchor="w")

# ---- Canvas ----
canvas = tk.Canvas(root, bg="white")
canvas.pack(side="top", fill="both", expand=True)

canvas.create_text(
    350, 200,
    text="Canvas Area",
    fill="gray",
    font=("Arial", 16)
)

root.mainloop()
