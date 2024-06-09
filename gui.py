from tkinter.ttk import Frame, Label
from journal_reader.journal_models import Log
from trip_logger.trip import Trip


class GUI:
    def __init__(self, log: Log, tk) -> None:
        self.log = log
        self.tk_instance = tk
        self.trip = Trip()

    def build_trip_summary(self) -> None:
        events = self.log.get_until_event(
            ["SellExplorationData", "SellOrganicData"], reverse=True
        )
        self.trip.add_entries(events)

        summary_frame = Frame(master=self.tk_instance)
        summary_frame.pack()
        planets_scanned_label = Label(
            text=str(self.trip.bodies_scanned), master=summary_frame
        )
        planets_scanned_label.pack()
        scanned_value_label = Label(
            text=str(self.trip.scanned_value), master=summary_frame
        )
        scanned_value_label.pack()
