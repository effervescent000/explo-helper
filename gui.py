from typing import Callable

import ttkbootstrap as tb


from db.galaxy import BioSignal, Galaxy, Planet
from journal_reader.journal_reader import JournalReader
from trip_logger.trip import Trip


def styledLabel(text: str, **kwargs) -> tb.Label:
    return tb.Label(text=text, **kwargs)


class GUI:
    def __init__(self, reader: JournalReader, tk, galaxy: Galaxy) -> None:
        self.log = reader.log
        self.tk_instance = tk
        self.trip = Trip(
            galaxy,
            refresh_func=self.refresh_system_tab,
            add_body_to_ui=self.add_to_system,
            clear_system=self.clear_system,
        )
        reader.set_trip(self.trip)

        self.notebook = tb.Notebook(self.tk_instance)
        self.route_tab = tb.Frame(self.notebook)
        self.system_tab = SystemTab(tb.Frame(self.notebook), self.trip.galaxy)
        self.summary_tab = tb.Frame(self.notebook)

    def clear_system(self) -> None:
        self.system_tab.clear()

    def refresh_system_tab(self) -> None:
        self.system_tab.refresh()

    def add_to_system(self, body: Planet) -> None:
        self.system_tab.append_body(body)

    def build_trip_snapshot(self) -> None:
        events = self.log.get_until_event(
            ["SellExplorationData", "SellOrganicData"], reverse=True
        )
        self.trip.add_entries(events)

        summary_frame = tb.Frame(master=self.tk_instance)
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
        self.system_tab.build_headers()


class SignalLabel:
    def __init__(
        self,
        signal_frame: tb.Frame,
        *,
        signal: BioSignal,
        update_func: Callable[[BioSignal], str],
        dynamic: bool = False,
    ) -> None:
        self.update_func = update_func
        self.signal = signal
        self.dynamic = dynamic
        self.label = tb.Label(signal_frame, text=update_func(self.signal))


class SignalRow:
    def __init__(self, signal_frame: tb.Frame, *, signal: BioSignal) -> None:
        self.signal = signal
        self.y = 0
        self.children = [
            SignalLabel(
                signal_frame,
                signal=self.signal,
                update_func=lambda x: f"{x.species.genus} {x.species.species}",
            ),
            SignalLabel(
                signal_frame,
                signal=self.signal,
                update_func=lambda x: f"{x.species.value:,}",
            ),
        ]

    def place_children(self) -> None:
        for x, child in enumerate(self.children):
            child.label.grid(row=self.y, column=x)

    def destroy(self) -> None:
        for child in self.children:
            child.label.destroy()
        self.children = []


class HeaderLabel:
    def __init__(self, master: tb.Frame, text: str) -> None:
        self.container = tb.Frame(master, style="info")
        self.label = tb.Label(self.container, text=text, style="inverse-info")

    def place_self(self, x: int) -> None:
        self.container.grid(row=0, column=x, sticky="ew")
        self.label.pack()


class BodyLabel:
    def __init__(
        self,
        master: tb.Frame,
        *,
        update_func: Callable[[Planet], str],
        body: Planet,
        dynamic: bool = False,
    ) -> None:
        self.update_func = update_func
        self.body = body
        self.label = tb.Label(master, text=self.update_func(self.body))
        self.dynamic = dynamic

    def do_update(self) -> None:
        self.label.config(text=self.update_func(self.body))


class BodyRow:
    def __init__(self, parent_frame: tb.Frame, *, y: int, body: Planet) -> None:
        self.y = y
        self.body = body
        self.signal_frame = tb.Frame(parent_frame)
        self.signals: list[SignalRow] = [
            SignalRow(self.signal_frame, signal=signal) for signal in self.body.signals
        ]
        self.children: list[BodyLabel] = [
            BodyLabel(
                parent_frame,
                update_func=lambda x: x.name,
                body=self.body,
            ),
            BodyLabel(
                parent_frame,
                update_func=lambda x: x.planet_class
                if x.planet_class is not None
                else "",
                body=self.body,
            ),
            BodyLabel(
                parent_frame,
                update_func=lambda x: f"{x.cartographic_values_estimate.total_value:,}",
                body=self.body,
                dynamic=True,
            ),
            BodyLabel(
                parent_frame,
                update_func=lambda x: f"{x.signal_count or ''}",
                body=self.body,
            ),
            BodyLabel(
                parent_frame,
                update_func=lambda x: x.bio_signal_value_label,
                body=self.body,
            ),
        ]

    def place_children(self) -> None:
        for x, child in enumerate(self.children):
            child.label.grid(row=self.y * 2, column=x)
        if len(self.signals) > 0:
            self.signal_frame.grid(row=self.y * 2 + 1, column=1, columnspan=2)
            for signal in self.signals:
                signal.place_children()

    def do_update(self) -> None:
        for child in self.children:
            if child.dynamic:
                child.do_update()

    def destroy(self) -> None:
        for x in self.signals:
            x.destroy()
        self.signals = []
        self.signal_frame.destroy()

        for x in self.children:
            x.label.destroy()
        self.children = []

    def move_to(self, y: int) -> None:
        self.y = y
        for child in self.children:
            child.label.grid_configure(row=self.y * 2)
        if len(self.signals) > 0:
            self.signal_frame.grid_configure(row=self.y * 2 + 1)


class SystemTab:
    def __init__(self, parent: tb.Frame, galaxy: Galaxy) -> None:
        self.galaxy = galaxy
        self.parent = parent
        self.frame = tb.Frame(self.parent)
        self.frame.pack()
        self.rows: list[BodyRow] = []
        self.headers: list[HeaderLabel] = []

    @property
    def bodies(self) -> dict[int, Planet]:
        return self.galaxy.current_system.planets

    @property
    def body_count(self) -> int:
        return len(self.bodies)

    def clear(self) -> None:
        for body in self.rows:
            body.destroy()
        self.rows = []

    def refresh(self) -> None:
        for body in self.rows:
            body.do_update()

    def append_body(self, body: Planet) -> None:
        row = BodyRow(self.frame, y=self.body_count, body=body)
        self.rows.append(row)
        self.sort_bodies()
        row.place_children()
        # self.instantiate_headers()

    def build_headers(self) -> None:
        headers = ["Name", "Type", "Mapped Value", "Bio Count", "Bio Value"]
        for i, header in enumerate(headers):
            header_label = HeaderLabel(self.frame, text=header)
            self.headers.append(header_label)
            header_label.place_self(i)

    # def instantiate_headers(self) -> None:
    #     for i, header in enumerate(self.headers):
    #         # header.label.pack_forget()
    #         # header.label.pack(fill=X, expand=YES)
    #         header.place_self(i)

    def sort_bodies(self) -> None:
        new_order = sorted(
            [x for x in self.bodies.values()],
            key=lambda x: x.cartographic_values_estimate.total_value,
            reverse=True,
        )
        for row in self.rows:
            row.move_to(new_order.index(row.body) + 1)
