import ttkbootstrap as ttk

from db.galaxy import Galaxy
from gui import GUI
from journal_reader.journal_reader import JournalReader

root = ttk.Window(themename="minty")

galaxy = Galaxy()
reader = JournalReader()
reader.compile_journals()
observer = reader.monitor_journals()

gui = GUI(reader.log, root, galaxy)
gui.build_trip_snapshot()


root.mainloop()

observer.stop()
observer.join()
