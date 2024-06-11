from ttkbootstrap import Frame, Label

from db.galaxy import Galaxy
from journal_reader.journal_models import Log
from trip_logger.trip import Trip


def styledLabel(**kwargs) -> Label:
    return Label(**kwargs)


class GUI:
    def __init__(self, log: Log, tk, galaxy: Galaxy) -> None:
        self.log = log
        self.tk_instance = tk
        self.trip = Trip(galaxy)

    def build_trip_snapshot(self) -> None:
        events = self.log.get_until_event(
            ["SellExplorationData", "SellOrganicData"], reverse=True
        )
        self.trip.add_entries(events)

        summary_frame = Frame(master=self.tk_instance)
        summary_frame.pack()

        planets_scanned_label = styledLabel(
            text=f"Scanned bodies: {self.trip.bodies_scanned}", master=summary_frame
        )

        scanned_value_label = styledLabel(
            text=f"Scanned bodies' value: {self.trip.scanned_value:,}",
            master=summary_frame,
        )

        planets_mapped_count_label = styledLabel(
            text=f"Mapped bodies: {self.trip.bodies_mapped}", master=summary_frame
        )
        planets_mapped_value_label = styledLabel(
            text=f"Mapped bodies' value: {self.trip.mapped_value:,}",
            master=summary_frame,
        )

        scanned_labels = [planets_scanned_label, scanned_value_label]
        for i in range(len(scanned_labels)):
            scanned_labels[i].grid(row=0, column=i)

        mapped_labels = [planets_mapped_count_label, planets_mapped_value_label]
        for i in range(len(mapped_labels)):
            mapped_labels[i].grid(row=1, column=i)
