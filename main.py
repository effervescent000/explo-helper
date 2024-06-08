import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import SUCCESS, LEFT

root = tk.Tk()

button = ttk.Button(root, text="HELLO WORLD")
button.pack(side=LEFT, padx=5, pady=5)

root.mainloop()