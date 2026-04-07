# paper_04_automated_feedback_sql

Data and analysis for the paper “Automated Feedback in Grading: An SQL Clause-Driven Approach”.

## Folder structure

```text
paper_04_automated_feedback_sql/
  README.md
  software/
    socoles
  data/
    raw/
      exam/
      week-1/
      week-2/
      week-3/
      week-4/
      week-5/
      week-6/
    processed/
      eval.csv
      exam/
      week-1/
      week-2/
      week-3/
      week-4/
      week-5/
      week-6/
  outputs/
    figures/
      all/
      exam/
      week-1/
      week-2/
      week-3/
      week-4/
      week-5/
      week-6/
    tables/
  scripts/
    generate_stats.py
    generate_stats_combine.py
    wooclap-socoles-assess.py
```

## Dataset groups

- `data/raw/exam/`: source and support files for the exam tasks
- `data/raw/week-1/` to `data/raw/week-6/`: source and support files for the weekly quiz tasks
- `data/processed/eval.csv`: combined clause-level evaluation output for the study
- `data/processed/exam/`: graded outputs and derived datasets for the exam tasks
- `data/processed/week-1/` to `data/processed/week-6/`: graded outputs and derived datasets for the weekly quiz tasks
- `software/`: shared experiment software
- `outputs/figures/all/`: aggregate figures produced across the study
- `outputs/figures/exam/`: generated plots for the exam tasks
- `outputs/figures/week-1/` to `outputs/figures/week-6/`: generated plots and feedback illustrations for the weekly quiz tasks
- `scripts/`: analysis and data-preparation code
- `outputs/tables/`: generated tables
