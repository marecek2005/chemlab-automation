import tkinter as tk
from pathlib import Path
import subprocess
import sys


import os

def run_usb_test(choice):
    script_path = Path(__file__).with_name("dmm6500_logger.py")
    print(f"Kliknuto na {choice}, spouštím měření...")
    
    # Použijeme přesně ten 'python', který funguje v terminálu
    # a předáme mu kompletní prostředí (PATH, USB ovladače atd.)
    env = os.environ.copy()
    
    subprocess.Popen([sys.executable, str(script_path), choice], 
                     env=env,
                     cwd=str(script_path.parent))

def run_plot():
    script_path = Path(__file__).with_name("realtime_plot.py")
    print("Otevírám graf...")
    
    env = os.environ.copy()
    
    subprocess.Popen([sys.executable, str(script_path)], 
                     env=env,
                     cwd=str(script_path.parent))



root = tk.Tk()
root.title("Basic Tkinter Window")


voltage_graph_button = tk.Button(root, text="Voltage", width=20, command=lambda: run_usb_test("VOLTAGE"))
voltage_graph_button.pack(padx=20, pady=(0, 10))

current_graph_button = tk.Button(root, text="Current", width=20, command=lambda: run_usb_test("CURRENT"))
current_graph_button.pack(padx=20, pady=(0, 20))

plot_button = tk.Button(root, text="Open Plot", width=20, command=run_plot)
plot_button.pack(padx=20, pady=(0, 30))


root.mainloop()
