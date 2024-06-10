import tkinter as tk

from db.galaxy import Galaxy
from gui import GUI
from journal_reader.journal_reader import JournalReader

root = tk.Tk()

galaxy = Galaxy()
reader = JournalReader()
reader.compile_journals()
observer = reader.monitor_journals()

gui = GUI(reader.log, root, galaxy)
gui.build_trip_summary()


root.mainloop()

observer.stop()
observer.join()
