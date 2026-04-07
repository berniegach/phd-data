import sys
import csv
import re
import pandas as pd
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py input1.csv [input2.csv ...]")
        sys.exit(1)
    
    input_files = sys.argv[1:]
    output_file = "eval.csv"
    
    # Clauses of interest
    clauses = ["select", "from", "where", "group by", "having", "order by"]
    
    # Additional columns to add
    new_columns = [
        "syntax error",
        "All"
    ] + clauses + [
        "parseable", "semantics_error", "num_correct_clauses", "num_incorrect_clauses",
        "goal_present", "detailed_feedback_present"
    ]
    
    # Assuming the input is comma-delimited.
    delimiter = ','
    
    all_rows = []
    final_fieldnames = None
    
    # Process each input file
    for input_file in input_files:
        with open(input_file, 'r', encoding='utf-8-sig', newline='') as infile:
            reader = csv.DictReader(infile, delimiter=delimiter)
            
            # For the first file, determine final fieldnames
            if final_fieldnames is None:
                original_fieldnames = reader.fieldnames[:]  # Make a copy
                # Determine which new columns are not already present
                columns_to_add = [col for col in new_columns if col not in original_fieldnames]
                # Create final fieldnames (original + new at the end)
                final_fieldnames = original_fieldnames + columns_to_add
            
            for row in reader:
                feedback = row.get("Feedback", "")
                
                # Initialize new columns in the row if they are missing
                if "syntax error" not in row:
                    row["syntax error"] = 0
                if "All" not in row:
                    row["All"] = 0
                for c in clauses:
                    if c not in row:
                        row[c] = ""
                if "parseable" not in row:
                    row["parseable"] = 1
                if "semantics_error" not in row:
                    row["semantics_error"] = 0
                if "num_correct_clauses" not in row:
                    row["num_correct_clauses"] = 0
                if "num_incorrect_clauses" not in row:
                    row["num_incorrect_clauses"] = 0
                if "goal_present" not in row:
                    row["goal_present"] = 1 if "### Goal:" in feedback else 0
                if "detailed_feedback_present" not in row:
                    row["detailed_feedback_present"] = 1 if "### Detailed Feedback:" in feedback else 0
    
                # Check for syntax error (case-insensitive)
                if re.search(r"\bsyntax\b", feedback, re.IGNORECASE):
                    row["syntax error"] = 1
    
                # Check parseability
                if "The query is not parseable" in feedback:
                    row["parseable"] = 0
    
                # Check semantics error
                if re.search(r"\bsemantics\b", feedback, re.IGNORECASE):
                    row["semantics_error"] = 1
    
                # If feedback contains "Correct." we mark All = 1
                if "Correct." in feedback:
                    row["All"] = 1
    
                # Identify correctness of clauses
                lines = [l.strip() for l in feedback.splitlines() if l.strip()]
                correct_section = False
                incorrect_section = False
    
                for line in lines:
                    # Check for sections
                    if "You have correctly constructed the following clauses:" in line:
                        correct_section = True
                        incorrect_section = False
                        continue
                    
                    if "There are issues with the following clauses:" in line:
                        incorrect_section = True
                        correct_section = False
                        continue
                    
                    # If in a correct or incorrect section, check for clauses
                    if correct_section or incorrect_section:
                        for cl in clauses:
                            pattern = r"\b" + re.escape(cl) + r"\b"
                            if re.search(pattern, line, re.IGNORECASE):
                                if correct_section:
                                    row[cl] = "correct"
                                    row["num_correct_clauses"] = int(row["num_correct_clauses"]) + 1
                                elif incorrect_section:
                                    row[cl] = "incorrect"
                                    row["num_incorrect_clauses"] = int(row["num_incorrect_clauses"]) + 1
                
                # Ensure all new columns exist in the row, if not set them
                for col in new_columns:
                    if col not in row:
                        # Default values if missing
                        if col in clauses:
                            row[col] = ""
                        elif col == "syntax error" or col == "semantics_error":
                            row[col] = 0
                        elif col == "All" or col == "parseable" or col == "goal_present" or col == "detailed_feedback_present":
                            row[col] = 0
                        elif col == "num_correct_clauses" or col == "num_incorrect_clauses":
                            row[col] = 0
    
                all_rows.append(row)
    
    # Write the updated CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=final_fieldnames, delimiter=delimiter)
        writer.writeheader()
        for r in all_rows:
            writer.writerow(r)
    
    print(f"Processed data has been saved to {output_file}")

    # Create charts from the data using pandas and matplotlib
    df = pd.read_csv(output_file, delimiter=delimiter)   

    # New Chart: Clause Correctness Stacked Bar, including All
    extended_clauses = ["Syntax", "All"] + clauses

    clause_data = []

    # Syntax treated like a clause (no syntax error = correct, syntax error = incorrect)
    syntax_correct_count = (df["syntax error"] == 0).sum()
    syntax_incorrect_count = (df["syntax error"] == 1).sum()
    clause_data.append([syntax_correct_count, syntax_incorrect_count])
    
    # All treated like a clause
    all_correct_count = (df["All"] == 1).sum()
    all_incorrect_count = (df["All"] == 0).sum()
    clause_data.append([all_correct_count, all_incorrect_count])
    
    # Actual clauses
    for c in clauses:
        correct_count = (df[c] == "correct").sum()
        incorrect_count = (df[c] == "incorrect").sum()
        clause_data.append([correct_count, incorrect_count])

    clause_df = pd.DataFrame(clause_data, index=extended_clauses, columns=["correct", "incorrect"])

    ax = clause_df.plot(kind='bar', stacked=True, figsize=(10,6), color=["green", "red"])
    plt.xlabel("Clause / All / Syntax")
    plt.ylabel("Count")

    # Add labels on top of each bar with total count and percentage correct
    for i, c in enumerate(extended_clauses):
        correct_count = clause_df.loc[c, "correct"]
        incorrect_count = clause_df.loc[c, "incorrect"]
        total = correct_count + incorrect_count
        if total > 0:
            correct_pct = (correct_count / total) * 100
            
            # Label above the entire bar (total + percentage)
            ax.text(i, total + 0.5, f"{total}",
                    ha="center", va="bottom", fontsize=10)
            
            # Additional percentage label inside the correct sub-bar
            ax.text(i, correct_count / 2, f"{correct_pct:.1f}%", 
                    ha="center", va="center", fontsize=8, color="white")

    plt.tight_layout()
    plt.savefig("clause_correctness_stacked_bar.png")
    plt.clf()

    print("Charts have been saved as PNG files.")

if __name__ == "__main__":
    main()
