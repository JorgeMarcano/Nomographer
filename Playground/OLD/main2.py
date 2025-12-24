import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import json

class FormulaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Formula Editor")

        self.data = {"formulas": []}
        self.current_file = None

        # Hard-coded dropdown options
        self.graph_type = ["f(u) + f(v) = f(w)", "f(u) / f(v) = f(w)", "f(u) / f(w) = f(v) / f(t)", "Determinant"]

        # ----- Menu -----
        menubar = tk.Menu(root)
        file_menu = tk.Menu(menubar, tearoff=0)

        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)

        menubar.add_cascade(label="File", menu=file_menu)

        formula_menu = tk.Meun(menubar, tearoff=0)

        formula_menu.add_command(label="Edit", command=self.open_formula_popup)
        formula_menu.add_command(label="Add", command=self.open_formula_popup)

        menubar.add_cascade(label="Formulas", menu=formula_menu)
        root.config(menu=menubar)

        # ----- Main Button -----
        ttk.Button(
            root,
            text="Add Formula",
            command=self.open_formula_popup,
            width=20
        ).pack(pady=20)

    # ----- Menu Actions -----
    def new_file(self):
        self.data = {"formulas": []}
        self.current_file = None
        messagebox.showinfo("New", "Started a new file")

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")]
        )
        if file_path:
            with open(file_path, "r") as f:
                self.data = json.load(f)
            self.current_file = file_path
            messagebox.showinfo("Open", "File loaded successfully")

    def save_file(self):
        if not self.current_file:
            self.current_file = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json")]
            )

        if self.current_file:
            with open(self.current_file, "w") as f:
                json.dump(self.data, f, indent=4)
            messagebox.showinfo("Save", "File saved successfully")

    # ----- Popup Window -----
    def open_formula_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add Formula")

        tk.Label(popup, text="Formula:").pack(padx=10, pady=5)

        formula_entry = tk.Entry(popup, width=30)
        formula_entry.pack(padx=10, pady=5)

        def add_formula():
            formula = formula_entry.get().strip()
            if formula:
                self.data.setdefault("formulas", []).append(formula)
                popup.destroy()
            else:
                messagebox.showwarning("Input Error", "Formula cannot be empty")

        ttk.Button(popup, text="Add", command=add_formula).pack(pady=10)


# ----- Run App -----
if __name__ == "__main__":
    root = tk.Tk()
    app = FormulaApp(root)
    root.mainloop()
