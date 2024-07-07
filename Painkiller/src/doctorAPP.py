import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from .core import Core
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
class DoctorApp:
    def __init__(self, root, core):
        self.core = core
        self.root = root

        self.root.title("Doctor Interface")
        self.root.geometry('1400x950+0+0')  # Adjusted size to provide more space

        # Create title bar for dragging with larger height
        self.title_bar = tk.Frame(root, bg="lightgrey", relief="raised", bd=2, height=40)
        self.title_bar.pack(fill=tk.X)
        self.title_bar_label = tk.Label(self.title_bar, text="Doctor Interface", bg="lightgrey")
        self.title_bar_label.pack(side=tk.LEFT, padx=10, pady=10)
        self.make_window_draggable(self.title_bar)

        button_width = 25  # Set a uniform button width
        self.simulate_speed = 1000  # Default simulation speed

        # Frame for the buttons with border
        self.button_frame = tk.Frame(root, bd=2, relief="groove", width=200, height=700)
        self.button_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=10, pady=10)
        self.button_frame.pack_propagate(0)

        # Subframe for doctor-related buttons
        self.doctor_button_frame = tk.Frame(self.button_frame, bd=2, relief="groove", width=200, height=300)
        doctor_title = tk.Label(self.doctor_button_frame, text="Doctor Controls", bg="lightgrey")
        doctor_title.pack(side=tk.TOP, fill=tk.X)
        self.doctor_button_frame.pack(side=tk.TOP, fill=tk.Y, expand=False, padx=10, pady=5)
        self.doctor_button_frame.pack_propagate(0)

        # Subframe for system-related buttons
        self.system_button_frame = tk.Frame(self.button_frame, bd=2, relief="groove", width=200, height=230)
        system_title = tk.Label(self.system_button_frame, text="System Controls", bg="lightgrey")
        system_title.pack(side=tk.TOP, fill=tk.X)
        self.system_button_frame.pack(side=tk.TOP, fill=tk.Y, expand=False, padx=10, pady=5)
        self.system_button_frame.pack_propagate(0)

        # Create buttons
        self.set_baseline_button = tk.Button(self.doctor_button_frame, text="Set Baseline", command=self.show_baseline_scale, width=button_width)
        self.set_baseline_button.pack(pady=5)
        self.set_bolus_button = tk.Button(self.doctor_button_frame, text="Set Bolus", command=self.show_bolus_scale, width=button_width)
        self.set_bolus_button.pack(pady=5)
        self.baseline_on_button = tk.Button(self.doctor_button_frame, text="Baseline On", command=self.baseline_on, width=button_width)
        self.baseline_on_button.pack(pady=5)
        self.baseline_off_button = tk.Button(self.doctor_button_frame, text="Baseline Off", command=self.baseline_off, width=button_width)
        self.baseline_off_button.pack(pady=5)
        self.graph_button = tk.Button(self.doctor_button_frame, text="Graph", command=self.show_graph, width=button_width)
        self.graph_button.pack(pady=5)
        self.stop_graph_button = tk.Button(self.doctor_button_frame, text="Stop Graph", command=self.stop_graph, width=button_width)
        self.stop_graph_button.pack(pady=5)

        self.start_button = tk.Button(self.system_button_frame, text="Start", command=self.start_simulate, width=button_width)
        self.start_button.pack(pady=5)
        self.set_simulate_speed_button = tk.Button(self.system_button_frame, text="Set Simulate Speed", command=self.show_simulate_speed_scale, width=button_width)
        self.set_simulate_speed_button.pack(pady=5)
        self.pause_button = tk.Button(self.system_button_frame, text="Pause", command=self.pause, width=button_width)
        self.pause_button.pack(pady=5)
        self.reset_button = tk.Button(self.system_button_frame, text="Reset", command=self.reset, width=button_width)
        self.reset_button.pack(pady=5)

        # Frame for the right part of the interface
        self.right_frame = tk.Frame(root, bd=2, relief="groove", width=1200, height=950)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.right_frame.pack_propagate(0)

        # Frame for text and graph controls
        self.text_frame = tk.Frame(self.right_frame, bd=2, relief="groove", width=1100, height=250)
        self.text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False, padx=10, pady=10)
        self.text_frame.pack_propagate(0)

        # Frame for the dynamic part of the interface with border
        self.dynamic_frame = tk.Frame(self.text_frame, bd=2, relief="groove", width=500, height=250)
        self.dynamic_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.dynamic_frame.pack_propagate(0)

        # Create a subframe for the scale controls
        self.scale_frame = tk.Frame(self.text_frame, bd=2, relief="groove", width=500, height=250)
        self.scale_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=10, pady=10)
        self.scale_frame.pack_propagate(0)

        # Create a subframe for the graph controls
        self.graph_frame = tk.Frame(self.right_frame, bd=2, relief="groove", width=1200, height=650)
        self.graph_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False, padx=10, pady=10)
        self.graph_frame.pack_propagate(0)
        self.resume_button = None
        self.pause_label = None
        self.showing_graph = 'off'  # Graph is not being shown
        self.paused = False
        self.start = False
        self.canvas = None
        self.ax1 = None
        self.ax2 = None
        self.stop_graph_button.config(state=tk.DISABLED)
        self.display_realtime_info()

    def display_realtime_info(self):
        if not self.paused:
            self.display_status()

    def display_status(self):
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()
        status = self.core.status()
        # Create and pack the labels with units
        units = {
            'Time': 'min',
            'Baseline Rate': 'mL/min',
            'Bolus Amount': 'mL',
            'Hourly Amount': 'mL',
            'Daily Amount': 'mL',
            'Baseline Status': ''
        }
        for key, value in status.items():
            unit = units.get(key, '')
            label = tk.Label(self.dynamic_frame, text=f"{key}: {value} {unit}", anchor='w', width=50)
            label.pack(fill='x', padx=5, pady=5)

        if self.start:
            self.root.after(self.simulate_speed, self.display_realtime_info)
            self.core.update_by_minute()

    def start_simulate(self):
        # Update every second
        self.start = True
        self.display_realtime_info()
        if self.showing_graph == 'on':
            self.update_graphs()
        self.start_button.config(state=tk.DISABLED)
        self.show_message("Simulation started.")

    def update_graph(self, fig, frame):
        if self.canvas is None:
            self.canvas = FigureCanvasTkAgg(fig, master=frame)
            self.canvas.get_tk_widget().place(relx=0.5, rely=0.5, anchor=tk.CENTER)

            self.ax1, self.ax2 = self.core.initialize_axes(fig)
        else:
            self.core.update_axes(self.ax1, self.ax2)
            self.canvas.get_tk_widget().place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            self.canvas.draw()

    def show_graph(self):
        self.showing_graph = 'on'
        self.stop_graph_button.config(state=tk.NORMAL)
        self.graph_button.config(state=tk.DISABLED)
        self.update_graphs()

    def update_graphs(self):
        if self.showing_graph == 'on':
            fig = self.core.figure
            self.update_graph(fig, self.graph_frame)
            if self.start:
                self.root.after(self.simulate_speed, self.update_graphs)  # Update graph every second

    def stop_graph(self):
        self.showing_graph = 'off'
        self.graph_button.config(state=tk.NORMAL)
        self.stop_graph_button.config(state=tk.DISABLED)
        if hasattr(self, 'canvas'):
            self.canvas.figure.clf()
            self.core.figure.clf()
            self.core.figure = plt.Figure(figsize=(10, 5))

            self.canvas.get_tk_widget().destroy()
            self.canvas = None  
            self.ax1 = None
            self.ax2 = None
        self.show_message("Graph stopped.")

    def show_baseline_scale(self):
        self.clear_scale_frame()
        baseline_label = tk.Label(self.scale_frame, text="Set Baseline (0.01-0.1 mL/min):")
        baseline_label.pack(pady=20, anchor=tk.CENTER)
        self.baseline_scale = tk.Scale(self.scale_frame, from_=0.01, to=0.1, resolution=0.01, orient=tk.HORIZONTAL, length=300)
        self.baseline_scale.pack(pady=5, anchor=tk.CENTER)

        self.set_button = tk.Button(self.scale_frame, text="Set Baseline", command=self.set_baseline)
        self.set_button.pack(pady=5, anchor=tk.CENTER)

    def show_bolus_scale(self):
        self.clear_scale_frame()
        bolus_label = tk.Label(self.scale_frame, text="Set Bolus (0.2-0.5 mL):")
        bolus_label.pack(pady=20, anchor=tk.CENTER)
        self.bolus_scale = tk.Scale(self.scale_frame, from_=0.2, to=0.5, resolution=0.01, orient=tk.HORIZONTAL, length=300)
        self.bolus_scale.pack(pady=5, anchor=tk.CENTER)

        self.set_button = tk.Button(self.scale_frame, text="Set Bolus", command=self.set_bolus)

        self.set_button.pack(pady=5, anchor=tk.CENTER)

    def show_simulate_speed_scale(self):
        self.clear_scale_frame()
        speed_label = tk.Label(self.scale_frame, text="Set the simulation speed (1x to 5x):")
        speed_label.pack(pady=20, anchor=tk.CENTER)
        self.speed_scale = tk.Scale(self.scale_frame, from_=1, to=5, resolution=1, orient=tk.HORIZONTAL, length=300)
        self.speed_scale.pack(pady=5, anchor=tk.CENTER)

        self.set_button = tk.Button(self.scale_frame, text="Set Speed", command=self.set_simulate_speed)
        self.set_button.pack(pady=5, anchor=tk.CENTER)

    def set_baseline(self):
        baseline = self.baseline_scale.get()
        message = self.core.set_baseline(baseline)
        if not self.start:
            self.display_realtime_info()
        self.show_message(message)

    def set_bolus(self):
        bolus = self.bolus_scale.get()
        message = self.core.set_bolus(bolus)
        if not self.start:
            self.display_realtime_info()
        self.show_message(message)

    def baseline_on(self):
        self.core.baseline_on()
        if not self.start:
            self.display_realtime_info()
        self.show_message("Baseline injection turned on.")

    def baseline_off(self):
        self.core.baseline_off()
        if not self.start:
            self.display_realtime_info()
        self.show_message("Baseline injection turned off.")

    def reset(self):
        self.start = False
        self.paused = False
        self.resume_button = None
        self.pause_label = None

        self.start_button.config(state=tk.NORMAL)
        self.simulate_speed = 1000
        if self.showing_graph == 'on':
            self.stop_graph()
        self.showing_graph = 'off'
        self.graph_button.config(state=tk.NORMAL)
        self.stop_graph_button.config(state=tk.DISABLED)
        self.core.reset()
        self.clear_dynamic_frame()
        self.clear_scale_frame()
        self.display_realtime_info()
        self.show_message("System reset.")

    def pause(self):
        self.paused = True
        self.disable_buttons()
        if self.showing_graph == 'on':
            self.showing_graph = 'pause'  # Stop updating the graph when paused
        self.clear_scale_frame()
        self.pause_label = tk.Label(self.scale_frame, text="Simulation is paused. Press the \"Resume\" button to restart the system.", wraplength=400, justify=tk.LEFT)
        self.pause_label.place(relx=0.5, rely=0.15, anchor=tk.CENTER)
        self.resume_button = tk.Button(self.scale_frame, text="Resume", command=self.resume)
        self.resume_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER) 
        # Use a different message method to not clear the resume button

    def resume(self):
        self.paused = False
        self.enable_buttons()
        self.clear_scale_frame()
        self.show_message("Simulation resumed.")
        self.display_realtime_info()
        if self.showing_graph == 'pause':
            self.showing_graph = 'on'  # Resume updating the graph
            self.graph_button.config(state=tk.DISABLED)
            self.update_graphs()
        elif self.showing_graph == 'off':
            
            self.stop_graph_button.config(state=tk.DISABLED)
        if self.start:
            self.start_button.config(state=tk.DISABLED)

    def set_simulate_speed(self):
        multiplier = self.speed_scale.get()
        self.simulate_speed = int(1000 / multiplier)
        self.show_message(f"Simulation speed set to {multiplier}x.")

    def disable_buttons(self):
        self.set_baseline_button.config(state=tk.DISABLED)
        self.set_bolus_button.config(state=tk.DISABLED)
        self.baseline_on_button.config(state=tk.DISABLED)
        self.baseline_off_button.config(state=tk.DISABLED)
        self.graph_button.config(state=tk.DISABLED)
        self.stop_graph_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.DISABLED)
        self.set_simulate_speed_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        

    def enable_buttons(self):
        self.set_baseline_button.config(state=tk.NORMAL)
        self.set_bolus_button.config(state=tk.NORMAL)
        self.baseline_on_button.config(state=tk.NORMAL)
        self.baseline_off_button.config(state=tk.NORMAL)
        self.graph_button.config(state=tk.NORMAL)
        self.stop_graph_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.NORMAL)
        self.set_simulate_speed_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)
        

    def clear_dynamic_frame(self):
        for widget in self.dynamic_frame.winfo_children():
            widget.pack_forget()

    def clear_scale_frame(self):
        if self.scale_frame.winfo_children():
            for widget in self.scale_frame.winfo_children():
                if (self.pause_label and widget == self.pause_label )or (self.resume_button and widget == self.resume_button):
                    widget.place_forget()
                else:
                    widget.pack_forget()
        if hasattr(self, 'message_frame'):
            self.message_frame.destroy()

    def show_message(self, message):
        self.clear_scale_frame()
        if hasattr(self, 'message_frame'):
            self.message_frame.destroy()

        self.message_frame = tk.Frame(self.scale_frame, bd=2, relief="groove")
        self.message_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # Center the frame

        label = tk.Label(self.message_frame, text=message)
        label.pack(pady=5)

        def clear_message():
            if hasattr(self, 'message_frame'):
                self.message_frame.destroy()
                delattr(self, 'message_frame')

        self.root.after(3000, clear_message)

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
    root = tk.Tk()
    core = Core()
    app = DoctorApp(root, core)
    root.mainloop()
