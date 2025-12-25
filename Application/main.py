import json
import tkinter as tk
from tkinter import ttk

import Nomograph


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Nomograph Builder")

        self.nomograph = Nomograph.Nomograph()
        Nomograph.parallel_builder("t", "t", "t", (0, 1), (0, 1), (0, 1), self.nomograph)

        # self.create_menu()

        # Load data
        self.types = self.load_json("Types.json")
        self.type_lookup = {t["name"]: t for t in self.types}

        # Tkinter variables
        self.selected_name = tk.StringVar()
        self.selected_name.set(self.types[0]["name"])
        self.last_selected_name = ""

        # Build UI
        self.entries = []
        self.create_widgets()

        # Trace selection changes
        self.selected_name.trace_add("write", self.on_select)

    def load_json(self, path):
        with open(path, "r") as file:
            data = json.load(file)
        return data["types"]

    # ---------- Menu ----------
    def create_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Load", command=self.load_dialog)
        file_menu.add_command(label="Save", command=self.save_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill="x", padx=10, pady=10)

        # Dropdown
        self.dropdown = ttk.OptionMenu(
            top_frame,
            self.selected_name,
            self.selected_name.get(),
            *self.type_lookup.keys()
        )
        self.dropdown.pack(side="left", padx=10)
        self.dropdown.config(state="disabled")

        # Description label
        self.description_label = tk.Label(
            top_frame,
            text="",
            wraplength=350,
            justify="left",
            anchor="nw"
        )
        self.description_label.pack(side="left", padx=10, fill="x", expand=True)

        # Frame for dynamic entries
        self.entries_frame = ttk.Frame(self.main_frame)
        self.entries_frame.pack(fill="both", padx=10, pady=10)

        # Canvas for the nomograph
        # Canvas (fills remaining space)
        self.canvas = tk.Canvas(
            self.main_frame,
            background="#f0f0f0",
            highlightthickness=1,
            highlightbackground="#999"
        )
        self.canvas.pack(fill="both", expand=True)

        # Optional: show canvas size for demo
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # Generate the default selection
        self.on_select()

    # ---------- Callbacks ----------
    def on_select(self, *args):
        name = self.selected_name.get()
        if name not in self.type_lookup:
            return

        # It is the same option, do nothing
        if (name == self.last_selected_name):
            return

        self.last_selected_name = name

        item = self.type_lookup[name]

        # Update description
        self.description_label.config(text=item["description"])

        # Rebuild entries
        self.build_entries(item["variables"])

        # Get a new nomograph

        # Auto-resize window
        self.update_idletasks()
        self.geometry("")


    def validate_numeric(self, value_if_allowed):
        """
        Allow only empty input or numeric values.
        """
        if value_if_allowed == "":
            return True
        return value_if_allowed.replace('.', '', 1).isdigit()
        # return value_if_allowed.isdigit()

    def build_entries(self, count):
        # Clear old entries
        for widget in self.entries_frame.winfo_children():
            widget.destroy()

        self.entries.clear()

        # Register validation command once
        vcmd = (self.register(self.validate_numeric), "%P")

        if (count <= 0):
            return

        for i in range(count):
            row = ttk.Frame(self.entries_frame)
            row.pack(anchor="w", pady=2)

            # Main entry (unchanged)
            ttk.Label(row, text=f"F{i + 1}(x)=").pack(side="left", padx=(0, 5))
            main_entry = ttk.Entry(row, width=30)
            main_entry.insert(0, "x")
            main_entry.pack(side="left", padx=(0, 10))
            main_entry.bind("<Return>", self.update_formulas)
            main_entry.bind("<FocusOut>", self.update_formulas)

             # Min entry (numeric only)
            ttk.Label(row, text="Min").pack(side="left", padx=(0, 2))
            min_entry = ttk.Entry(
                row,
                width=6,
                validate="key",
                validatecommand=vcmd
            )
            min_entry.insert(0, "0.0")
            min_entry.pack(side="left", padx=(0, 10))
            min_entry.bind("<Return>", self.update_ranges)
            min_entry.bind("<FocusOut>", self.update_ranges)

            # Max entry (numeric only)
            ttk.Label(row, text="Max").pack(side="left", padx=(0, 2))
            max_entry = ttk.Entry(
                row,
                width=6,
                validate="key",
                validatecommand=vcmd
            )
            max_entry.insert(0, "1.0")
            max_entry.pack(side="left")
            max_entry.bind("<Return>", self.update_ranges)
            max_entry.bind("<FocusOut>", self.update_ranges)

            self.entries.append({
                "main": main_entry,
                "min": min_entry,
                "max": max_entry
            })

    def update_ranges(self, event):
        # Updates a range, then updates the canvas
        widget = event.widget

        for row, entry_group in enumerate(self.entries):
            if widget in entry_group.values():
                new_min = entry_group["min"].get()
                if new_min == "":
                    entry_group["min"].insert(0, "0.0")
                    new_min = 0
                else:
                    new_min = float(new_min)

                new_max = entry_group["max"].get()
                if new_max == "":
                    entry_group["min"].insert(0, "0.0")
                    new_max = 0
                else:
                    new_max = float(new_max)

                self.nomograph.update_range(row, (new_min, new_max))

        self.update_canvas()

    def update_formulas(self, event):
        # Updates a range, then updates the canvas
        widget = event.widget

        for row, entry_group in enumerate(self.entries):
            if widget in entry_group.values():
                continue

        self.update_canvas()

    def update_canvas(self):
        self.canvas.delete("all")
        self.nomograph.draw(self.canvas, self.canvas_width, self.canvas_height)

     # ---------- Canvas ----------
    def on_canvas_resize(self, event):
        self.canvas.delete("all")

        # Example drawing: centered text showing canvas size
        self.canvas_width = event.width
        self.canvas_height = event.height
        text = f"Canvas size: {event.width} x {event.height}"
        self.canvas.create_text(
            event.width // 2,
            event.height // 2,
            text=text,
            fill="black"
        )

        self.update_canvas()

    # ---------- Menu Actions ----------
    def new_file(self):
        # messagebox.showinfo("New", "New document created.")
        pass

    def load_dialog(self):
        # path = filedialog.askopenfilename(
        #     filetypes=[("JSON Files", "*.json")]
        # )
        # if path:
        #     self.load_file(path)
        pass

    def save_dialog(self):
        # if not self.types:
        #     messagebox.showwarning("Save", "Nothing to save.")
        #     return
        #
        # path = filedialog.asksaveasfilename(
        #     defaultextension=".json",
        #     filetypes=[("JSON Files", "*.json")]
        # )
        # if path:
        #     with open(path, "w") as file:
        #         json.dump({"types": self.types}, file, indent=2)
        #     messagebox.showinfo("Save", "File saved successfully.")
        pass


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
