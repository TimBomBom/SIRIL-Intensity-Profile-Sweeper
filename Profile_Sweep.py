"""
Intensity Profile Sweep GUI for Siril (Python script)

Requires Siril 1.4.0-beta3 or later.
Run from Siril: Scripts → Python Scripts.

This script sweeps intensity profiles between two vectors (V1 and V2),
creating N interpolated profile lines and saving each as profile_i.dat.
"""

import sys
import math
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

import sirilpy as s
from sirilpy import tksiril, SirilError

s.ensure_installed("ttkthemes")
from ttkthemes import ThemedTk

VERSION = "1.0.4"

# Connect to Siril and check SIRIL version ---------------------------------------------------------

siril = s.SirilInterface()

try:
    siril.connect()
except s.SirilConnectionError:
    siril.error_messagebox("Failed to connect to Siril")
    raise SystemExit(1)

if not siril.is_image_loaded():
    siril.error_messagebox("No image is loaded")
    raise SystemExit(1)

try:
    siril.cmd("requires", "1.4.0-beta3")
except s.CommandError:
    siril.error_messagebox("Version not high enough (need at least 1.4.0-beta3)")
    raise SystemExit(1)


# Call Siril's intensity profile function and interpolate between two vectors ----------------------
def generate_profiles(v1, v2, num_steps, is_colour, offset):

    steps = int(num_steps)
    siril.log(f"Number of steps = {steps}")

    oxsteps = (v2["x1"] - v1["x1"]) / steps
    oysteps = (v2["y1"] - v1["y1"]) / steps
    xsteps = (v2["x2"] - v1["x2"]) / steps
    ysteps = (v2["y2"] - v1["y2"]) / steps

    layer_arg = "-layer=col" if is_colour else "-layer=lum"

    for i in range(steps):
        fromx = int(v1["x1"] + i * oxsteps)
        fromy = int(v1["y1"] + i * oysteps)
        tox = int(v1["x2"] + i * xsteps)
        toy = int(v1["y2"] + i * ysteps)

        fromCoords = f"({fromx},{fromy})"
        toCoords = f"({tox},{toy})"

        # for debugging to log what siril just ran in the console
        cmd_str = (
            f"profile -from={fromx},{fromy} -to={tox},{toy} "
            f"{layer_arg} -filename=profile_{i+int(offset)}.dat"
            f"-title=Intensity_Profile_{i+int(offset)}_{fromCoords}-{toCoords}"
        )
        siril.log(cmd_str)

        siril.cmd(
            "profile",
            f"-from={fromx},{fromy}",
            f"-to={tox},{toy}",
            layer_arg,
            f"-filename=profile_{i+int(offset)}.dat",
            f"-title=Intensity_Profile_{i+int(offset)}_{fromCoords}-{toCoords}",
        )



# ----------------------------------------------------------------------
# GUI stuff (taken from siril docs: "Template for Scripts with GUIs")
# ----------------------------------------------------------------------
class TemplateScriptInterface:
    """GUI and callbacks for the Intensity Profile Sweep"""

    def __init__(self, root):
        self.root = root
        self.root.title(f"Intensity Profile Sweep - v{VERSION}")
        self.root.resizable(False, False)
        self.style = tksiril.standard_style()

        self.create_widgets()
        tksiril.match_theme_to_siril(self.root, siril)

    def create_widgets(self):
        """Create the GUI widgets."""
        img = siril.get_image()
        xSize = img.width
        ySize = img.height

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        title_label = ttk.Label(
            main_frame,
            text="Intensity Profile Sweep",
            style="Header.TLabel",
        )
        title_label.pack(pady=(0, 20))

        
        v1_frame = ttk.LabelFrame(main_frame, text="V1 Coordinates", padding=10)
        v1_frame.pack(fill=tk.X, padx=5, pady=5)
        
        v2_frame = ttk.LabelFrame(main_frame, text="V2 Coordinates", padding=10)
        v2_frame.pack(fill=tk.X, padx=5, pady=5)

        # V1 from  ---------------------------------------------------------------------------------
        v1_coordinates_from_frame = ttk.Frame(v1_frame)
        v1_coordinates_from_frame.pack(fill=tk.X, pady=5)

        ttk.Label(v1_coordinates_from_frame, text="From (x,y): ").pack(side=tk.LEFT)

        self.v1_x1 = ttk.Spinbox(
            v1_coordinates_from_frame,
            from_=0,
            to=xSize - 1,
        )
        self.v1_x1.set(0)
        self.v1_x1.pack(side=tk.LEFT, padx=10, expand=True)

        self.v1_y1 = ttk.Spinbox(
            v1_coordinates_from_frame,
            from_=0,
            to=ySize - 1,
        )
        self.v1_y1.set(0)
        self.v1_y1.pack(side=tk.RIGHT, padx=10, expand=True)

        tksiril.create_tooltip(self.v1_x1, "Starting x value of first profile.")
        tksiril.create_tooltip(self.v1_y1, "Starting y value of first profile.")

        # V1 to  -----------------------------------------------------------------------------------
        v1_coordinates_to_frame = ttk.Frame(v1_frame)
        v1_coordinates_to_frame.pack(fill=tk.X, pady=5)

        ttk.Label(v1_coordinates_to_frame, text="To (x,y):    ").pack(side=tk.LEFT)

        self.v1_x2 = ttk.Spinbox(
            v1_coordinates_to_frame,
            from_=0,
            to=xSize - 1,
        )
        self.v1_x2.set(0)
        self.v1_x2.pack(side=tk.LEFT, padx=17, expand=True)

        self.v1_y2 = ttk.Spinbox(
            v1_coordinates_to_frame,
            from_=0,
            to=ySize - 1,
        )
        self.v1_y2.set(0)
        self.v1_y2.pack(side=tk.RIGHT, padx=10, expand=True)

        tksiril.create_tooltip(self.v1_x2, "Ending x value of first profile.")
        tksiril.create_tooltip(self.v1_y2, "Ending y value of first profile.")

        # Button to use the current selection for the coordinates of the first vector
        self.V1_selection = ttk.Button(
            v1_frame,
            text="Use Selection",
            command=self.get_selection_v1,
            style="TButton",
        )        
        self.V1_selection.pack(side=tk.LEFT, pady=10)
        tksiril.create_tooltip(self.V1_selection, "Sets from/to values to upper left and lower right corners of current selection respectively.")

        self.V1_reset = ttk.Button(
            v1_frame,
            text="Reset V1",
            command=self.reset_v1,
            style="TButton"
        )
        self.V1_reset.pack(side=tk.LEFT, padx=10)
        tksiril.create_tooltip(self.V1_reset, "Reset all values to 0 for vector 1")

        # V2 from  ---------------------------------------------------------------------------------
        v2_coordinates_from_frame = ttk.Frame(v2_frame)
        v2_coordinates_from_frame.pack(fill=tk.X, pady=5)

        ttk.Label(v2_coordinates_from_frame, text="From (x,y): ").pack(side=tk.LEFT)

        self.v2_x1 = ttk.Spinbox(
            v2_coordinates_from_frame,
            from_=0,
            to=xSize - 1,
        )
        self.v2_x1.set(0)
        self.v2_x1.pack(side=tk.LEFT, padx=10, expand=True)

        self.v2_y1 = ttk.Spinbox(
            v2_coordinates_from_frame,
            from_=0,
            to=ySize - 1,
        )
        self.v2_y1.set(0)
        self.v2_y1.pack(side=tk.RIGHT, padx=10, expand=True)

        tksiril.create_tooltip(self.v2_x1, "Starting x value of second profile.")
        tksiril.create_tooltip(self.v2_y1, "Starting y value of second profile.")

        # V2 to  -----------------------------------------------------------------------------------
        v2_coordinates_to_frame = ttk.Frame(v2_frame)
        v2_coordinates_to_frame.pack(fill=tk.X, pady=5)

        ttk.Label(v2_coordinates_to_frame, text="To (x,y): ").pack(side=tk.LEFT)

        self.v2_x2 = ttk.Spinbox(
            v2_coordinates_to_frame,
            from_=0,
            to=xSize - 1,
        )
        self.v2_x2.set(0)
        self.v2_x2.pack(side=tk.LEFT, padx=30, expand=True)

        self.v2_y2 = ttk.Spinbox(
            v2_coordinates_to_frame,
            from_=0,
            to=ySize - 1,
        )
        self.v2_y2.set(0)
        self.v2_y2.pack(side=tk.LEFT, padx=20, expand=True)

        tksiril.create_tooltip(self.v2_x2, "Ending x value of second profile.")
        tksiril.create_tooltip(self.v2_y2, "Ending y value of second profile.")

        # Button to use the current selection for the coordinates of the second vector
        self.V2_selection = ttk.Button(
            v2_frame,
            text="Use Selection",
            command=self.get_selection_v2,
            style="TButton",
        )        
        self.V2_selection.pack(side=tk.LEFT, pady=10)
        tksiril.create_tooltip(self.V2_selection, "Sets from/to values to upper left and lower right corners of current selection respectively.")

        self.V2_reset = ttk.Button(
            v2_frame,
            text="Reset V2",
            command=self.reset_v2,
            style="TButton"
        )
        self.V2_reset.pack(side=tk.LEFT, padx=10)
        tksiril.create_tooltip(self.V2_reset, "Reset all values to 0 for vector 2")

        # Options frame  ---------------------------------------------------------------------------
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=5, pady=10)

        cp_frame = ttk.Frame(options_frame)
        cp_frame.pack(fill=tk.X, pady=5)

        steps_frame = ttk.Frame(options_frame)
        steps_frame.pack(fill=tk.X, pady=5)

        offset_frame = ttk.Frame(options_frame)
        offset_frame.pack(fill=tk.X, pady=5)

        self.isColour = tk.BooleanVar(self.root, value=True)
        colour_checkbox = ttk.Checkbutton(
            cp_frame,
            text="Colour Profile",
            variable=self.isColour,
            style="TCheckbutton",
        )
        colour_checkbox.pack(anchor=tk.W, pady=2)
        tksiril.create_tooltip(
            colour_checkbox,
            "Use colour profile (RGB). Disable for luminance (mono) profile.",
        )

        ttk.Label(steps_frame, text="Number of Steps: ").pack(side=tk.LEFT)
        self.steps = ttk.Spinbox(
            steps_frame,
            from_=2,
            to=100,
        )
        self.steps.set(2)
        self.steps.pack(side=tk.LEFT, padx=10, expand=True)
        tksiril.create_tooltip(
            self.steps,
            "Number of profiles to generate between V1 and V2 (2-100).",
        )

        ttk.Label(offset_frame, text="Filename Offset:").pack(side=tk.LEFT)
        self.offset = ttk.Spinbox(
            offset_frame,
            from_=1
        )
        self.offset.set(1)
        self.offset.pack(side=tk.LEFT, padx=9, expand=True)
        tksiril.create_tooltip(
            self.offset,
            "Number to start from when saving profiles as dat files. This allows you to save multiple measurements to the folder without starting from 1 and thus overwriting previous measurements. I.e. if you have 3 profiles saved in the folder, set offset to 4 and it will save subsequent profiles as profile_4, profile_5, ..., etc."
        )

        # Buttons frame  ---------------------------------------------------------------------------
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)

        close_btn = ttk.Button(
            button_frame,
            text="Close",
            command=self.close_dialog,
            style="TButton",
        )
        close_btn.pack(side=tk.LEFT, padx=5)
        tksiril.create_tooltip(
            close_btn,
            "Close the interface and disconnect from Siril. Commands will not be executed.",
        )

        apply_btn = ttk.Button(
            button_frame,
            text="Apply",
            command=self.apply_changes,
            style="TButton",
        )
        apply_btn.pack(side=tk.LEFT, padx=5)
        tksiril.create_tooltip(
            apply_btn,
            "Generate intensity profiles with the set parameters.",
        )


    def get_selection_v1(self):
        try:
            sel = siril.get_siril_selection()
            if sel != None:
                self.v1_x1.set(sel[0])
                self.v1_y1.set(sel[1])
                self.v1_x2.set(sel[0] + sel[2])
                self.v1_y2.set(sel[1] + sel[3])
            else:
                siril.log("No Selection")

        except SirilError as e:
            messagebox.showerror("Error", str(e))


    def get_selection_v2(self):
        try:
            sel = siril.get_siril_selection()
            if sel != None:
                self.v2_x1.set(sel[0])
                self.v2_y1.set(sel[1])
                self.v2_x2.set(sel[0] + sel[2])
                self.v2_y2.set(sel[1] + sel[3])
            else:
                siril.log("No Selection")

        except SirilError as e:
            messagebox.showerror("Error", str(e))

    # Reset the vector coordinates for v1 to 0
    def reset_v1(self):
        try:
            self.v1_x1.set(0)
            self.v1_y1.set(0)
            self.v1_x2.set(0)
            self.v1_y2.set(0)

        except SirilError as e:
            messagebox.showerror("Error", str(e))


    def reset_v2(self):
        try:
            self.v2_x1.set(0)
            self.v2_y1.set(0)
            self.v2_x2.set(0)
            self.v2_y2.set(0)

        except SirilError as e:
            messagebox.showerror("Error", str(e))


    def apply_changes(self):
        """Read GUI values and generate profiles."""
        try:
            isColour = self.isColour.get()
            offset = self.offset.get()

            v1 = {
                "x1": int(self.v1_x1.get()),
                "y1": int(self.v1_y1.get()),
                "x2": int(self.v1_x2.get()),
                "y2": int(self.v1_y2.get()),
            }

            v2 = {
                "x1": int(self.v2_x1.get()),
                "y1": int(self.v2_y1.get()),
                "x2": int(self.v2_x2.get()),
                "y2": int(self.v2_y2.get()),
            }
            steps = int(self.steps.get())
            if v1 == v2:
                siril.log("Both vectors have equal coordinates! No interpolation can occur.")
            else:
                generate_profiles(v1, v2, steps, isColour, offset)

        except SirilError as e:
            messagebox.showerror("Error", str(e))

    def close_dialog(self):
        """Close dialog."""
        self.root.quit()
        self.root.destroy()


# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------
def main():
    try:
        root = ThemedTk()
        TemplateScriptInterface(root)
        root.mainloop()
    except SirilError as e:
        print(f"Error initializing script: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()