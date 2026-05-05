<hr>

# EduVista

## Educational Data Visualization Tool for Score Analysis

EduVista transforms raw student assessment data into insightful statistical visualizations. It generates professional-grade histograms with normal distribution curves, sigma bands, and comprehensive statistical metrics.

<hr>

### 1: Features

- **Automated Assessment Parsing** – Dynamically parses assessment data from PDF files.
- **Adaptive Score Scaling** – Automatically applies proper score scaling for midterms and exams.
- **Statistical Analysis** – Mean, median, mode, standard deviation, percentiles, skewness, pass rates, ...
- **Concise Visualizations** – Histograms with normal curve overlay & sigma bands (1σ, 2σ, 3σ).
- **Subject Theming** – Custom plot themeing per subject.
- **One-Click Export** – 's'-key-press to save high-resolution PNG with automatic versioning.

<hr>

### 2: Assessments

**Naming Convention:** `{Subject}_{Type}{Iteration}_{Year}`

**Assessment Types:**
- `K` – Kolokvij (Midterm)
- `I` – Izpit (Exam)

**Subjects:**
- `PriPJ` – Principi Programskih Jezikov
- `PrePJ` – Prevajanje Programskih Jezikov
- `SA` – Sistemska Administracija
- `SP` – Spletno Programiranje

**Currently Available:**
- `PriPJ_K1_2026`
- `PrePJ_K1_2026`
- `SP_K1_2026`

<hr>

### 3: Quick Start

#### Prerequisites

```
pip install pdfplumber numpy scipy seaborn matplotlib
```

#### Program Start

```bash
# Generic usage
python3 main.py --assessment <assessment>

# Example usage
python3 main.py --assessment PriPJ_K1_2026
```

<hr>
