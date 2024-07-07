import tkinter as tk
from tkinter import messagebox
from .core import Core

class PatientApp:
    def __init__(self, root, core):
        self.core = core
        self.root = root
        self.root.title("Patient Interface")
        self.root.geometry('200x100+160+300')
        
        # Create title bar for dragging 
        self.title_bar = tk.Frame(root, bg="lightgrey", relief="raised", bd=2, height=40)
        self.title_bar.pack(fill=tk.X)
        self.title_bar_label = tk.Label(self.title_bar, text="Patient Interface", bg="lightgrey")
        self.title_bar_label.pack(side=tk.LEFT, padx=10, pady=10)
        self.make_window_draggable(self.title_bar)

        self.request_bolus_button = tk.Button(root, text="Request Bolus", command=self.request_bolus)
        self.request_bolus_button.pack(pady=5)

    def request_bolus(self):
        return self.core.request_bolus()

    def make_window_draggable(self, widget):
        self.offset_x = 0
        self.offset_y = 0

        def on_mouse_down(event):
            self.offset_x = event.x
            self.offset_y = event.y

        def on_mouse_move(event):
            x = self.root.winfo_x() + event.x - self.offset_x
            y = self.root.winfo_y() + event.y - self.offset_y
            self.root.geometry(f'+{x}+{y}')

        widget.bind('<Button-1>', on_mouse_down)
        widget.bind('<B1-Motion>', on_mouse_move)
if __name__ == "__main__":
    core = Core()
    root = tk.Tk()
    app = PatientApp(root, core)
    root.mainloop()