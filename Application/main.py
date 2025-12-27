import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import Nomograph


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Nomograph Builder")

        self.nomograph = Nomograph.Parallel(name="parallel", func_vars=[0, 1, 2], funcs=["t"] * 3, ranges=[(0, 1)] * 3)
        self.selected_tag = None
        self.nomograph.scale(100, 100)
        self.nomograph.execute_last_transform()

        self.create_menu()

        # Load data
        self.types = self.load_json("Types.json")
        self.type_lookup = {t["name"]: t for t in self.types}

        # Tkinter variables
        self.selected_name = tk.StringVar()
        self.selected_name.set(self.types[0]["name"])
        self.last_selected_name = ""
        self.status_var = tk.StringVar()

        # Build UI
        self.entries = []
        self.ranges = []
        self.create_widgets()
        self.create_canvas()

        # Trace selection changes
        self.selected_name.trace_add("write", self.on_select)

        # Transformation States
        self.last_mouse_pos = None
        self.pan_vector = (0, 0)   # (dx, dy)

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

    # ---------- Create Window Elements ----------
    def create_widgets(self):
        self.child = tk.Toplevel(self)
        self.child.title("Functions Window")
        self.child.resizable(False, False)  # ← prevents resizing
        self.child.protocol(
            "WM_DELETE_WINDOW",
            lambda: messagebox.showwarning(
                "Error",
                "Cannot close this window",
                parent=self.child
            )
        )

        top_frame = ttk.Frame(self.child)
        top_frame.pack(fill="x", padx=10, pady=10)

        # Dropdown
        self.dropdown = ttk.OptionMenu(
            top_frame,
            self.selected_name,
            self.selected_name.get(),
            *self.type_lookup.keys()
        )
        self.dropdown.pack(side="left", padx=10)

        # Description label
        self.description_label = tk.Label(
            top_frame,
            text="",
            wraplength=350,
            justify="left",
            anchor="nw"
        )
        self.description_label.pack(
            side="left", padx=10, fill="x", expand=True)

        # Frame for dynamic entries
        self.input_frame = ttk.Frame(self.child)
        self.input_frame.pack(fill="both", padx=10, pady=10)

        self.entries_frame = ttk.Frame(self.input_frame)
        self.entries_frame.pack(side="left", padx=10, pady=10)

        self.ranges_frame = ttk.Frame(self.input_frame)
        self.ranges_frame.pack(side="left", fill="both", padx=10, pady=10)

    def create_canvas(self):
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # Canvas for the nomograph
        # Canvas (fills remaining space)
        self.canvas = tk.Canvas(
            self.main_frame,
            background="#f0f0f0",
            highlightthickness=1,
            highlightbackground="#999"
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()

        # Optional: show canvas size for demo
        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Control-Button-1>", self.on_mouse_ctrl_press)

        # Display status bar
        self.status_var.set("")
        self.status_message = ttk.Label(self.main_frame, textvariable=self.status_var,
                                        justify=tk.LEFT, anchor='w')
        self.status_message.pack(fill="both", padx=10)

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
        self.build_entries(item["functions"])

        # Get a new nomograph
        if name == "Parallel":
            self.nomograph = Nomograph.Parallel(name="parallel", func_vars=item["functions"], other=self.nomograph)
        elif name == "N or Z":
            self.nomograph = Nomograph.Z_Chart(name="z_chart", func_vars=item["functions"], other=self.nomograph)
        elif name == "Concurrent":
            self.nomograph = Nomograph.Concurrent(name="concurrent", func_vars=item["functions"], other=self.nomograph)

        self.update_canvas()

        # Auto-resize window
        self.update_idletasks()
        self.child.geometry("")

    def validate_numeric(self, value_if_allowed):
        """
        Allow only empty input or numeric values.
        """
        if value_if_allowed == "" or value_if_allowed == "-":
            return True
        try:
            _ = float(value_if_allowed)
            return True
        except ValueError:
            return False

    def build_entries(self, functions):
        count = len(functions)

        old_entries = [entry.get() for entry in self.entries]
        if len(old_entries) < count:
            old_entries += ["t"] * (count - len(old_entries))

        # Clear old entries
        for widget in self.entries_frame.winfo_children():
            widget.destroy()
        for widget in self.ranges_frame.winfo_children():
            widget.destroy()
            
        self.entries.clear()
        self.ranges.clear()

        # Register validation command once
        vcmd = (self.register(self.validate_numeric), "%P")

        if (count <= 0):
            return

        for ind, var in enumerate(functions):
            row = ttk.Frame(self.entries_frame)
            row.pack(anchor="w", pady=2)

            # Main entry (unchanged)
            ttk.Label(row, text=f"F{ind + 1}(t=u{var})=").pack(side="left", padx=(0, 5))
            main_entry = ttk.Entry(row, width=30)
            main_entry.insert(0, old_entries[ind])
            main_entry.pack(side="left", padx=(0, 10))
            main_entry.bind("<Return>", self.update_formulas)
            main_entry.bind("<FocusOut>", self.update_formulas)

            self.entries.append(main_entry)

        range_name_arr = ["Min", "Max", "Maj", "Minor"]
        range_defaults = ["0.0", "1.0", "0.25", "0.05"]
        for var in range(max(functions)+1):
            row = ttk.Frame(self.ranges_frame)
            row.pack(anchor="w", pady=2)
            ttk.Label(row, text=f"u{var} =").pack(side="left", padx=(0, 5))

            temp_entries = []
            for ind, range_name in enumerate(range_name_arr):
                ttk.Label(row, text=range_name).pack(side="left", padx=(0, 2))
                temp_entry = ttk.Entry(
                    row,
                    width=6,
                    validate="key",
                    validatecommand=vcmd
                )
                temp_entry.insert(0, range_defaults[ind])
                temp_entry.pack(side="left", padx=(0, 10))
                temp_entry.bind("<Return>", self.update_ranges)
                temp_entry.bind("<FocusOut>", self.update_ranges)

                temp_entries.append(temp_entry)

            self.ranges.append({
                "min": temp_entries[0],
                "max": temp_entries[1],
                "maj": temp_entries[2],
                "minor": temp_entries[3]
            })

    def update_ranges(self, event):
        # Updates a range, then updates the canvas
        widget = event.widget

        new_val = widget.get()
        if new_val == "" or new_val == "-":
            widget.delete(0, tk.END)
            widget.insert(0, "0.0")
            new_val = 0
        else:
            new_val = float(new_val)

        for row, range_group in enumerate(self.ranges):
            if widget in range_group.values():
                if widget is range_group["min"]:
                    new_val = self.nomograph.get_tick(row).set_min(new_val)
                elif widget is range_group["max"]:
                    new_val = self.nomograph.get_tick(row).set_max(new_val)
                elif widget is range_group["maj"]:
                    new_val = self.nomograph.get_tick(row).set_major_tick(new_val)
                elif widget is range_group["minor"]:
                    new_val = self.nomograph.get_tick(row).set_minor_tick(new_val)

        widget.delete(0, tk.END)
        widget.insert(0, f"{new_val}")

        self.update_canvas()

    def get_funcs(self):
        funcs = [entry["main"].get() for entry in self.entries]

        return funcs

    def update_formulas(self, event):
        # Updates a range, then updates the canvas
        widget = event.widget

        for row, entry_group in enumerate(self.entries):
            if widget is entry_group:
                self.nomograph.update_formula(row, widget.get())

        self.update_canvas()

    def update_canvas(self):
        self.canvas.delete("all")
        self.nomograph.draw(self.gui_draw_line, self.gui_draw_text, 5)

     # ---------- Canvas ----------
    def on_canvas_resize(self, event):
        self.canvas_width = event.width
        self.canvas_height = event.height

        self.status_var.set(f"Canvas size: {event.width} x {event.height}")
        # # Example drawing: centered text showing canvas size
        # self.canvas.delete("all")
        # text = f"Canvas size: {event.width} x {event.height}"
        # self.canvas.create_text(
        #     event.width // 2,
        #     event.height // 2,
        #     text=text,
        #     fill="black"
        # )

        self.update_canvas()

    def gui_draw_line(self, tag, points):
        # Blue for line, red for big tick, green for small tick
        self.canvas.create_line(points, fill="black", width=1, smooth=True, tags=tag)

    def gui_draw_text(self, tag, px, py, text):
        self.canvas.create_text(
            px, py,
            text=text,
            font=("Arial", 8),
            fill="black",
            tags=tag
        )

    def on_mouse_press(self, event):
        self.last_mouse_pos = (event.x, event.y)
        self.nomograph.execute_last_transform()

    def on_mouse_ctrl_press(self, event):
        clicked_item = self.canvas.find_withtag("current")
        if clicked_item:
            # Get all tags associated with that specific item ID
            item_id = clicked_item[0]
            tags = self.canvas.gettags(item_id)
            self.selected_tag = [t for t in tags if t != "current"][0]
            self.canvas.itemconfigure(self.selected_tag, fill="blue")
        else:
            item_id = None
            tags = None
            if self.selected_tag:
                self.canvas.itemconfigure(self.selected_tag, fill="black")
            self.selected_tag = None
        self.status_var.set(f"Clicked item ID: {item_id}, Tags: {tags}, Selected: {self.selected_tag}")

    def on_mouse_drag(self, event):
        x0, y0 = self.last_mouse_pos
        pan_vector = (event.x - x0, event.y - y0)
        px, py = pan_vector

        self.nomograph.translate(px, py)
        self.nomograph.transform()

        self.update_canvas()

    # --------------------
    # ZOOM CALLBACK
    # --------------------

    def on_mouse_wheel(self, event):
        # Zoom direction
        scale = 1.1 if event.delta > 0 else 0.9

        shift_pressed = event.state & 0x0001
        ctrl_pressed = event.state & 0x0004

        if shift_pressed and not ctrl_pressed:
            sx = 1.0
            sy = scale
        elif ctrl_pressed and not shift_pressed:
            sx = scale
            sy = 1.0
        else:
            sx = scale
            sy = scale

        self.nomograph.scale_at_point(sx, sy, event.x, event.y)

        self.nomograph.execute_last_transform()
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
