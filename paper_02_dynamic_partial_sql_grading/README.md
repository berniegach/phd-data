# paper_02_dynamic_partial_sql_grading

Data and analysis for the paper “Dynamic and Partial Grading of SQL Queries”.

## Folder structure

```text
paper_02_dynamic_partial_sql_grading/
  README.md
  data/
    raw/
      questionnaire/
        post-grading_question.csv
      quizzes/
        2023/
    processed/
      quizzes/
        2023/
  scripts/
    sanitize_quiz_exports.py
  outputs/
    figures/
      quizzes/
        2023/
      all/
    tables/
```

## Dataset groups

- `data/raw/questionnaire/`: questionnaire data collected for the study
- `data/raw/quizzes/2023/` contains source attempt exports, reference answers, and related raw quiz files.
- `data/processed/quizzes/2023/` contains graded outputs such as `quiz_graded.csv` files and other derived CSVs.
- `scripts/`: analysis code
- `outputs/figures/quizzes/2023/` contains per-question charts such as `bar_graph.png`, organized with the same relative quiz folder structure.
- `outputs/figures/all/` contains top-level aggregate figures such as `multiple_bar_graph.png`.
- `outputs/tables/`: generated tables
