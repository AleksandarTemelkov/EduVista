from dataclasses    import dataclass, field
from enum           import Enum


@dataclass
class TableLayout:
    """Formal description of the PDF table structure."""
    id_column:     int = 0
    value_columns: list[int] = field(default_factory=lambda: [1])
    skip_rows:     int = 0

    @classmethod
    def v(cls, n: int, id_col: int = 0, skip: int = 0) -> 'TableLayout':
        """
        Notation v(n) creates a layout with id_col and 
        value_columns from id_col + 1 to id_col + n.
        """
        values = list(range(id_col + 1, id_col + n + 1)) # id_col = 0 : [1, 2, ..., n] 
        return cls(id_column=id_col, value_columns=values, skip_rows=skip)

class TableLayouts(Enum):
    """Commonly-used table layout interfaces."""
    V1 = TableLayout.v(1)
    V2 = TableLayout.v(2)
    V3 = TableLayout.v(3)
    V4 = TableLayout.v(4)

    @property
    def layout(self) -> TableLayout:
        return self.value