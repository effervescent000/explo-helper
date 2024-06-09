from pathlib import Path
import re
import os


from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from journal_reader.journal_models import Log

JOURNAL_NAME_REGEX = r"Journal.\d+-\d+-\d+T\d+\.\d+\.log"


class JournalEventHandler(FileSystemEventHandler):
    def __init__(self, log: Log) -> None:
        super().__init__()
        self.log = log

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
                self.log.append(e)

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

    def monitor_journals(self) -> BaseObserver:
        event_handler = JournalEventHandler(log=self.log)
        observer = Observer()
        observer.schedule(event_handler, self.file_location)
        observer.start()

        return observer
