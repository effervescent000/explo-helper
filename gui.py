from typing import Callable
from ttkbootstrap import Frame, Label, Notebook

from db.galaxy import Galaxy, Planet
from journal_reader.journal_reader import JournalReader
from trip_logger.trip import Trip


def styledLabel(text: str, **kwargs) -> Label:
    return Label(text=text, **kwargs)


class GUI:
    def __init__(self, reader: JournalReader, tk, galaxy: Galaxy) -> None:
        self.log = reader.log
        self.tk_instance = tk
        self.trip = Trip(galaxy, refresh_func=self.refresh_system_tab)
        reader.set_trip(self.trip)

        self.notebook = Notebook(self.tk_instance)
        self.route_tab = Frame(self.notebook)
        self.system_tab = SystemTab(Frame(self.notebook), self.trip.galaxy)
        self.summary_tab = Frame(self.notebook)

    def refresh_system_tab(self) -> None:
        self.system_tab.refresh()

    def build_trip_snapshot(self) -> None:
        events = self.log.get_until_event(
            ["SellExplorationData", "SellOrganicData"], reverse=True
        )
        self.trip.add_entries(events)

        summary_frame = Frame(master=self.tk_instance)
        summary_frame.pack()

        planets_scanned_label = styledLabel(
            text=f"Scanned bodies: {self.trip.bodies_scanned_count}",
            master=summary_frame,
        )
        scanned_value_label = styledLabel(
            text=f"Scanned bodies' value: {self.trip.bodies_scanned_value:,}",
            master=summary_frame,
        )
        planets_mapped_count_label = styledLabel(
            text=f"Mapped bodies: {self.trip.bodies_mapped_count}", master=summary_frame
        )
        planets_mapped_value_label = styledLabel(
            text=f"Mapped bodies' value: {self.trip.bodies_mapped_value:,}",
            master=summary_frame,
        )
        bonuses_label = styledLabel(
            text=f"Bonuses: {self.trip.bonuses:,}", master=summary_frame
        )

        scanned_labels = [planets_scanned_label, scanned_value_label]
        for i in range(len(scanned_labels)):
            scanned_labels[i].grid(row=i, column=0)

        mapped_labels = [planets_mapped_count_label, planets_mapped_value_label]
        for i in range(len(mapped_labels)):
            mapped_labels[i].grid(row=i, column=1)

        bonuses_label.grid(row=1, column=2, rowspan=2)

    def setup_tabs(self) -> None:
        self.notebook.add(self.route_tab, text="Route")
        self.notebook.add(self.system_tab.parent, text="Current system")
        self.notebook.add(self.summary_tab, text="Summary")

        self.notebook.pack()

    def build_tab_contents(self) -> None:
        self.system_tab.build_contents()


class BodyLabel(Label):
    def __init__(
        self, master: Frame, update_func: Callable[[Planet], str], body: Planet
    ) -> None:
        self.update_func = update_func
        self.body = body
        super().__init__(master, text=self.update_func(self.body))

    def do_update(self) -> None:
        self.config(text=self.update_func(self.body))


class SystemTab:
    def __init__(self, parent: Frame, galaxy: Galaxy) -> None:
        self.galaxy = galaxy
        self.parent = parent
        self.frame = Frame(self.parent)
        self.frame.pack()
        self.children: list[BodyLabel] = []

    def refresh(self) -> None:
        for child in self.children:
            child.do_update()

    def build_contents(self) -> None:
        headers = ["Name", "Type", "Mapped Value", "Biosignal Count"]
        system = self.galaxy.current_system
        for i in range(len(headers)):
            styledLabel(text=headers[i], master=self.frame).grid(row=0, column=i)
            if system is not None:
                for i, body in enumerate(system.planets.values()):
                    labels = [
                        BodyLabel(self.frame, lambda x: x.name, body),
                        BodyLabel(
                            self.frame,
                            lambda x: x.planet_class
                            if x.planet_class is not None
                            else "",
                            body,
                        ),
                        BodyLabel(
                            self.frame,
                            lambda x: f"{x.values_estimate.total_value:,}",
                            body,
                        ),
                        BodyLabel(
                            self.frame, lambda x: f"{x.signal_count or ''}", body
                        ),
                    ]
                    self.children.extend(labels)
                    signals_frame = Frame(self.frame)
                    signals_frame.grid(row=i * 2 + 2, column=1, columnspan=2)
                    for j, label in enumerate(labels):
                        label.grid(row=i * 2 + 1, column=j)

                    for j in range(len(body.signals)):
                        signal_label = BodyLabel(
                            signals_frame,
                            lambda x: f"{x.signals[j].species.genus} {x.signals[j].species.species}",
                            body,
                        )
                        signal_label.grid(row=j, column=0)
                        self.children.append(signal_label)
