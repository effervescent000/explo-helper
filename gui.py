from tkinter.ttk import Frame, Label
from db.galaxy import Galaxy
from journal_reader.journal_models import Log
from trip_logger.trip import Trip


class GUI:
    def __init__(self, log: Log, tk, galaxy: Galaxy) -> None:
        self.log = log
        self.tk_instance = tk
        self.trip = Trip(galaxy)

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
            text=f"{self.trip.scanned_value:,}", master=summary_frame
        )
        scanned_value_label.pack()

        planets_mapped_count_label = Label(
            text=str(self.trip.bodies_mapped), master=summary_frame
        )
        planets_mapped_count_label.pack()

        planets_mapped_value_label = Label(
            text=f"{self.trip.mapped_value:,}", master=summary_frame
        )
        planets_mapped_value_label.pack()
