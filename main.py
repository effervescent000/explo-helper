import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import SUCCESS, LEFT

from journal_reader.journal_reader import JournalReader

root = tk.Tk()


def handle_click(event: tk.Event):
    reader = JournalReader()
    reader.compile_journals()


button = ttk.Button(root, text="HELLO WORLD")
button.pack(side=LEFT, padx=5, pady=5)
button.bind("<Button-1>", handle_click)

root.mainloop()
