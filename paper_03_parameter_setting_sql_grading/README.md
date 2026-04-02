# paper_03_parameter_setting_sql_grading

Data and analysis for the paper “Parameter setting in automated SQL grading”.

## Folder structure

```text
paper_03_parameter_setting_sql_grading/
  README.md
  _previous_import_wrong_source/
  data/
    raw/
      properties/
        2024/
        2024_april/
      property_ordering/
        2024/
        2024_april/
      ted/
        2024/
        2024_april/
    processed/
      properties/
        2024/
        2024_april/
      property_ordering/
        2024/
        2024_april/
      ted/
        2024/
        2024_april/
  scripts/
    properties/
    property_ordering/
    ted/
  outputs/
    figures/
      properties/
        2024/
        2024_april/
      property_ordering/
        2024/
        2024_april/
      ted/
        2024/
        2024_april/
    tables/
```

## Dataset groups

- `data/raw/properties/`: source and support files for the evaluation properties experiments
- `data/raw/property_ordering/`: source and support files for the property-ordering experiments
- `data/raw/ted/`: source files for the text edit distance experiments
- `data/processed/properties/`: graded outputs and derived datasets for the evaluation properties experiments
- `data/processed/property_ordering/`: graded outputs and derived datasets for the property-ordering experiments
- `data/processed/ted/`: graded outputs and derived datasets for the text edit distance experiments
- `scripts/`: family-specific analysis and data-preparation code
- `outputs/figures/`: generated plots for each experiment family and run set
- `outputs/tables/`: generated tables
