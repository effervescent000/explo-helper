from ttkbootstrap import Frame, Label, Notebook

from db.galaxy import Galaxy
from journal_reader.journal_models import Log
from trip_logger.trip import Trip


def styledLabel(text: str, **kwargs) -> Label:
    return Label(text=text, **kwargs)


class GUI:
    def __init__(self, log: Log, tk, galaxy: Galaxy) -> None:
        self.log = log
        self.tk_instance = tk
        self.trip = Trip(galaxy)

        self.notebook = Notebook(self.tk_instance)
        self.route_tab = Frame(self.notebook)
        self.system_tab = Frame(self.notebook)
        self.summary_tab = Frame(self.notebook)

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

    def setup_tabs(self) -> None:
        self.notebook.add(self.route_tab, text="Route")
        self.notebook.add(self.system_tab, text="Current system")
        self.notebook.add(self.summary_tab, text="Summary")

        self.notebook.pack()

    def build_tab_contents(self) -> None:
        self._build_system_tab()

    def _build_system_tab(self) -> None:
        system = self.trip.galaxy.current_system
        headers = ["Name", "Type", "Mapped Value"]
        for i in range(len(headers)):
            styledLabel(text=headers[i], master=self.system_tab).grid(row=0, column=i)
        if system is not None:
            for i, body in enumerate(system.planets.values()):
                labels = [body.name, body.planet_class, f"{body.values.mapped:,}"]
                for j, label in enumerate(labels):
                    styledLabel(text=label, master=self.system_tab).grid(
                        row=i + 1, column=j
                    )
