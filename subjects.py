from dataclasses    import dataclass
from enum           import Enum
from score_scale    import ScoreScale


@dataclass(frozen=True)
class Subject:
    mnemonic: str
    full_name: str
    midterms_score_scale: ScoreScale
    exams_score_scale: ScoreScale
    color: str


class Subjects(Enum):
    PREPJ = Subject(
        mnemonic = "PrePJ",
        full_name = "Prevajanje Programskih Jezikov",
        midterms_score_scale = ScoreScale(0, 100, 35),
        exams_score_scale = ScoreScale(0, 100, 50),
        color = "#b4bec3",
    )
    PRIPJ = Subject(
        mnemonic = "PriPJ",
        full_name = "Principi Programskih Jezikov",
        midterms_score_scale = ScoreScale(0, 100, 35),
        exams_score_scale = ScoreScale(0, 100, 50),
        color = "#9eeaea"
    )
    SA = Subject(
        mnemonic = "SA",
        full_name = "Sistemska Administracija",
        midterms_score_scale = ScoreScale(0, 100, 35),
        exams_score_scale = ScoreScale(0, 100, 50),
        color = "#f285aa"
    )
    SP = Subject(
        mnemonic = "SP",
        full_name = "Spletno Programiranje",
        midterms_score_scale = ScoreScale(0, 100, 35),
        exams_score_scale = ScoreScale(0, 100, 50),
        color = "#53b596"
    )
