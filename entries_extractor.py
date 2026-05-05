from collections.abc import Callable
from enum            import Enum, auto
from score_scale     import ScoreScale
from table_layout    import TableLayout
import pdfplumber # pyright: ignore[reportMissingImports]

# Helper Classes
"""Helper classes to represent entries and their types, as well as to manage collections of entries."""
class EntryType(Enum):
    SCORE = auto()    # A valid numeric grade
    ABSENT = auto()   # Represented by '/'
    INVALID = auto()  # Non-numeric or unexpected junk data

class Entry:
    def __init__(self, 
            student_id: str,
            entry_type: EntryType,
            value: float | str,
            source_col: int
        ):
        self.student_id = student_id
        self.entry_type = entry_type
        self.value = value
        self.source_col = source_col

class Entries:
    def __init__(self, entries: list[Entry], condition: Callable[[Entry], bool] = None):
        self.entries = (self._filter_entries(entries, condition) if condition is not None else entries)

    @staticmethod
    def _filter_entries(entries: list[Entry], condition: Callable[[Entry], bool]) -> list[Entry]:
        return [e for e in entries if condition(e)]

    def len(self):
        return len(self.entries)

    def toString(self) -> str:
        n: int = self.len()
        result = "["

        for i, entry in enumerate(self.entries):
            result += f"({entry.student_id}, {entry.entry_type.name}, {entry.value})"
            if (i != n - 1): result += ", "
        
        result += "]"
        return result
    
    def print(self):
        print(self.toString())

class EntriesCategory(Enum):
    ALL = "entries_all"
    POSITIVE = "entries_positive"
    NEGATIVE = "entries_negative"
    ABSENT = "entries_absent"

class StatCategory(Enum):
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    RANGE = "range"
    STDDEV = "stddev"
    SKEWNESS = "skewness"
    PERCENTILE = "percentile"

class EntriesExtractor:
    def __init__(self, layout: TableLayout, score_scale: ScoreScale) -> None:
        self.layout =      layout
        self.score_scale = score_scale

    def _sanitize_input(self, student_id: str, value: str) -> Entry:
        """Categorizes and cleans raw PDF strings."""
        if value == "/": return Entry(student_id, EntryType.ABSENT, "/", self.layout.value_columns[0])
        
        try:
            # Try converting to float (e.g., "85.5" -> 85.5)
            num_value = float(value)

            def is_valid_score(score: float) -> bool:
                return self.score_scale.score_min <= score <= self.score_scale.score_max

            if not is_valid_score(num_value):
                return Entry(student_id, EntryType.INVALID, value, self.layout.value_columns[0])

            return Entry(student_id, EntryType.SCORE, num_value, self.layout.value_columns[0])
        except (ValueError, TypeError):
            # If it's not a slash and not a number, it's a general string
            return Entry(student_id, EntryType.INVALID, value, self.layout.value_columns[0])

    def extract_pdf(self, file_path: str) -> list[Entry]:
        all_entries = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if not table: continue
                
                for row in table[self.layout.skip_rows:]:
                    student_id = row[self.layout.id_column]
                    
                    # Extract all specified columns for this student
                    for col_idx in self.layout.value_columns:
                        raw_val = row[col_idx]
                        if raw_val is not None:
                            # You can now tag entries by their column index 
                            # or just collect them all
                            entry = self._sanitize_input(student_id, raw_val)
                            all_entries.append(entry)
        
        return all_entries