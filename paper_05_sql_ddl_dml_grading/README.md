# paper_05_sql_ddl_dml_grading

Data and analysis for the paper “Clause-Driven Automated Grading of SQL’s DDL and DML Statements”.

## Folder structure

```text
paper_05_sql_ddl_dml_grading/
  README.md
  data/
    raw/
      lab-2021/
      lab-2022/
      lab-2023/
      lab-2024/
      lab-2025/
    processed/
      lab-2021/
      lab-2022/
      lab-2023/
      lab-2024/
      lab-2025/
  scripts/
    stats.py
    stats2.py
  outputs/
    figures/
      all/
      feedback_charts/
      lab-2021/
      lab-2022/
      lab-2023/
      lab-2024/
      lab-2025/
      parseable_outcome_charts/
    tables/
```

## Dataset groups

- `data/raw/lab-2021/` to `data/raw/lab-2025/`: source and support files for each lab-year dataset
- `data/processed/lab-2021/` to `data/processed/lab-2025/`: graded outputs and derived datasets for each lab-year dataset
- `scripts/`: analysis and data-preparation code
- `outputs/figures/all/`: aggregate figures produced across the study
- `outputs/figures/feedback_charts/`: feedback-oriented summary charts
- `outputs/figures/lab-2021/` to `outputs/figures/lab-2025/`: year-specific figures and supporting images
- `outputs/figures/parseable_outcome_charts/`: parseability outcome charts by question
- `outputs/tables/`: generated tables