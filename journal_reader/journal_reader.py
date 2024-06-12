import json
from pathlib import Path
import re
import os


from pydantic import BaseModel
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from journal_reader.journal_models import EventType, JournalEvent, event_mapping
from trip_logger.trip import Trip


JOURNAL_NAME_REGEX = r"Journal.\d+-\d+-\d+T\d+\.\d+\.log"


class Log(BaseModel):
    events: list[JournalEvent] = []

    def convert_str_to_event(self, data: str | JournalEvent) -> JournalEvent | None:
        if isinstance(data, JournalEvent):
            return data
        parsed = json.loads(data)
        event_type = event_mapping.get(parsed["event"], None)
        if event_type is not None:
            return event_type(**parsed)

    def append(self, data: str | JournalEvent, trip: Trip | None = None) -> None:
        event = self.convert_str_to_event(data)
        if event is not None:
            self.events.append(event)
            if trip is not None:
                trip.add_entries([event])

    def find_event(
        self, data: str | JournalEvent, reverse: bool = False
    ) -> JournalEvent | None:
        """
        Pass in either a raw journal str or processed event, receive the first matching event
        (from oldest to newest by default).
        """
        event = self.convert_str_to_event(data) if isinstance(data, str) else data
        if event is None:
            return

        dataset = [*self.events]
        if reverse:
            dataset = list(reversed(dataset))
        for logged_event in dataset:
            if (
                event.timestamp == logged_event.timestamp
                and event.event == logged_event.event
            ):
                return logged_event

    def get_until_event(
        self, event_types: list[EventType], reverse: bool = False
    ) -> list[JournalEvent]:
        """Get all events (from start by default) until event of target type is found."""
        matching_events: list[JournalEvent] = []
        dataset = [*self.events]
        if reverse:
            dataset = list(reversed(dataset))

        for event in dataset:
            if event.event in event_types:
                break
            matching_events.append(event)

        if reverse:
            matching_events = list(reversed(matching_events))
        return matching_events


class JournalEventHandler(FileSystemEventHandler):
    def __init__(self, log: Log, trip: Trip | None = None) -> None:
        super().__init__()
        self.log = log
        self.trip = trip

    def set_trip(self, trip: Trip) -> None:
        self.trip = trip

    def handler(self, event: FileSystemEvent) -> None:
        if re.search(JOURNAL_NAME_REGEX, event.src_path) is not None:
            events_to_add: list[str] = []
            with open(event.src_path, "r") as file:
                for line in list(reversed(file.readlines())):
                    match = self.log.find_event(line)
                    if match is not None:
                        break
                    events_to_add.append(line)

            for e in list(reversed(events_to_add)):
                self.log.append(e, self.trip)

    def on_created(self, event: FileSystemEvent) -> None:
        self.handler(event)

    def on_modified(self, event: FileSystemEvent) -> None:
        self.handler(event)


class JournalReader:
    def __init__(self) -> None:
        self.file_location = os.path.join(
            str(Path.home()), "Saved Games/Frontier Developments/Elite Dangerous"
        )
        self.log = Log()
        self.event_handler = JournalEventHandler(log=self.log)

    def get_journal_file_names(self) -> list[str]:
        result: list[str] = []
        for path, _, files in os.walk(self.file_location):
            raw_matches = [re.search(JOURNAL_NAME_REGEX, file) for file in files]
            filtered_files = [x.string for x in raw_matches if x is not None]
            for file in filtered_files:
                result.append(os.path.join(path, file))

        return result

    def compile_journals(self) -> None:
        for file_name in self.get_journal_file_names():
            with open(file_name, "r") as file:
                for line in file.readlines():
                    self.log.append(line)

    def set_trip(self, trip: Trip) -> None:
        self.event_handler.set_trip(trip)

    def monitor_journals(self) -> BaseObserver:
        observer = Observer()
        observer.schedule(self.event_handler, self.file_location)
        observer.start()

        return observer
