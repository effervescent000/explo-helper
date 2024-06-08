from pathlib import Path
import re
import os

from journal_reader.journal_models import Log

JOURNAL_NAME_REGEX = r"Journal.\d+-\d+-\d+T\d+\.\d+\.log"


class JournalReader:
    def __init__(self) -> None:
        self.file_location = os.path.join(
            str(Path.home()), "Saved Games/Frontier Developments/Elite Dangerous"
        )

    def get_journal_file_names(self) -> list[str]:
        result: list[str] = []
        for path, _, files in os.walk(self.file_location):
            raw_matches = [re.search(JOURNAL_NAME_REGEX, file) for file in files]
            filtered_files = [x.string for x in raw_matches if x is not None]
            for file in filtered_files:
                result.append(os.path.join(path, file))

        return result

    def compile_journals(self) -> None:
        log = Log()
        for file_name in self.get_journal_file_names():
            with open(file_name, "r") as file:
                for line in file.readlines():
                    log.append(line)
        print(log.events[-1].model_dump())
