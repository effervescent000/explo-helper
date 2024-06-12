import ttkbootstrap as ttk

from db.galaxy import Galaxy
from gui import GUI
from journal_reader.journal_reader import JournalReader

root = ttk.Window(themename="minty")

galaxy = Galaxy()
reader = JournalReader()
reader.compile_journals()
observer = reader.monitor_journals()

gui = GUI(reader, root, galaxy)
gui.build_trip_snapshot()
gui.setup_tabs()
gui.build_tab_contents()


root.mainloop()

observer.stop()
observer.join()
