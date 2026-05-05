from dataclasses    import dataclass
from datetime       import date
from enum           import Enum
from score_scale    import ScoreScale
from table_layout   import TableLayout
from subjects       import Subject, Subjects


class AssessmentType(Enum):
    MIDTERM = "Kolokvij"
    EXAM = "Izpit"


@dataclass
class Assessment:
    subject: Subject
    type: AssessmentType
    date: date
    iteration: int
    layout: TableLayout

    @classmethod
    def midterm(cls, subject_enum, date_obj, iteration=1, layout=None):
        """Helper to create a Midterm."""
        return cls(
            subject = subject_enum.value,
            type = AssessmentType.MIDTERM,
            date = date_obj,
            iteration = iteration,
            layout = TableLayout.v(iteration)
        )

    @classmethod
    def exam(cls, subject_enum, date_obj, iteration=1, layout=None):
        """Helper to create an Exam."""
        return cls(
            subject = subject_enum.value,
            type = AssessmentType.EXAM,
            date = date_obj,
            iteration = iteration,
            layout = TableLayout.v(iteration)
        )

    def get_score_scale(self) -> ScoreScale:
        """Determines the scale based on the type stored in this assessment."""
        if self.type == AssessmentType.MIDTERM:
            return self.subject.midterms_score_scale
        return self.subject.exams_score_scale

    def get_title(self) -> str:
        """Generates assessment title."""
        base = f"{self.subject.full_name} – Rezultati"
        if self.type == AssessmentType.MIDTERM:
            return f"{base} {self.iteration}. {self.type.value}a"
        return f"{base} {self.type.value}a z dne {self.date.strftime('%d. %m. %Y')}"
    
    def get_filename(self) -> str:
        """Generates assessment filename."""
        if self.type == AssessmentType.MIDTERM:
            return f"{self.subject.mnemonic}-K{self.iteration}-{self.date.strftime('%Y')}"
        return f"{self.subject.mnemonic}-Izpit-{self.date.strftime('%Y-%m-%d')}"
    

class Assessments:
    PREPJ_K1_2026 = Assessment.midterm(Subjects.PREPJ, date(2026, 4, 8), 1)
    SP_K1_2026    = Assessment.midterm(Subjects.SP, date(2026, 4, 10), 1)
    PRIPJ_K1_2026 = Assessment.midterm(Subjects.PRIPJ, date(2026, 4, 14), 1)
    SA_K1_2026    = Assessment.midterm(Subjects.SA, date(2026, 4, 15), 1)