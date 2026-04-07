import sys
import pandas as pd
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) != 5:
        print("Usage: python compare_quizzes_side_by_side.py eval_quiz1.csv eval_quiz2.csv eval_quiz3.csv eval_quiz4.csv")
        sys.exit(1)

    quiz_files = sys.argv[1:]  # 4 CSV files, one per quiz
    quiz_names = ["Quiz1-week1", "Quiz2-week2", "Quiz3-week3", "Quiz4-week4"]

    # Clauses 
    clauses = ["select", "from", "where", "group by", "having", "order by"]
    #clauses = []
    extended_clauses = ["Syntax", "All"] + clauses
    extended_clauses = clauses

    # We'll keep track of [correct, incorrect] for each (clause, quiz).
    correct_counts = {cl: [0, 0, 0, 0] for cl in extended_clauses}
    incorrect_counts = {cl: [0, 0, 0, 0] for cl in extended_clauses}

    # ---- Read each quiz file and compute the correct/incorrect counts exactly like original code ----
    for q_idx, csv_file in enumerate(quiz_files):
        df = pd.read_csv(csv_file, encoding="utf-8-sig")

        # 1) Syntax
        """syntax_correct = (df["syntax error"] == 0).sum()
        syntax_incorrect = (df["syntax error"] == 1).sum()
        correct_counts["Syntax"][q_idx] = syntax_correct
        incorrect_counts["Syntax"][q_idx] = syntax_incorrect

        # 2) All
        all_correct = (df["All"] == 1).sum()
        all_incorrect = (df["All"] == 0).sum()
        correct_counts["All"][q_idx] = all_correct
        incorrect_counts["All"][q_idx] = all_incorrect"""

        # 3) Actual clauses
        for c in clauses:
            c_correct = (df[c] == "correct").sum()
            c_incorrect = (df[c] == "incorrect").sum()
            correct_counts[c][q_idx] = c_correct
            incorrect_counts[c][q_idx] = c_incorrect

    # ---- Create a figure with side-by-side stacked bars for each clause ----
    fig, ax = plt.subplots(figsize=(14, 8))

    # Number of clauses to display on the x-axis
    x_indices = range(len(extended_clauses))  # 0..(8 if we have Syntax + All + 6 clauses)
    bar_width = 0.2  # each quiz bar's width

    # We'll offset each quiz so they appear side by side:
    # For 4 quizzes, offsets like: -1.5*bar_width, -0.5*bar_width, 0.5*bar_width, 1.5*bar_width
    offsets = [(-1.5 + i)*bar_width for i in range(4)]

    # Define distinct hatch patterns for each quiz
    # e.g. '/', '\\', 'x', '.', 'o', '...', etc.
    hatch_patterns = ["////", "\\\\", "xx", ".."]

    for q_idx in range(4):
        quiz_name = quiz_names[q_idx]

        correct_vals = [correct_counts[clause][q_idx] for clause in extended_clauses]
        incorrect_vals = [incorrect_counts[clause][q_idx] for clause in extended_clauses]

        # We'll draw the green portion (correct)
        green_bar = ax.bar(
            [x + offsets[q_idx] for x in x_indices],  # shift horizontally
            correct_vals,
            width=bar_width,
            color="green",
            edgecolor="black",
            hatch=hatch_patterns[q_idx],   # apply quiz-specific hatch
            #label=quiz_name if q_idx == 0 else None  # we only label the first so we get the quiz name in legend
        )

        # Now the red portion (incorrect) stacked on top of green
        red_bar = ax.bar(
            [x + offsets[q_idx] for x in x_indices],
            incorrect_vals,
            width=bar_width,
            bottom=correct_vals,
            color="red",
            edgecolor="black",
            hatch=hatch_patterns[q_idx],   # same hatch for the same quiz
        )

        # Add text labels for each bar
        for idx, rect in enumerate(green_bar):
            c_val = correct_vals[idx]
            i_val = incorrect_vals[idx]
            total = c_val + i_val

            if total == 0:
                continue  # skip labeling if no data

            x_center = rect.get_x() + rect.get_width() / 2
            green_top = c_val  # the top of the green portion

            # Put the correct count and % in the middle of the green portion
            if c_val > 0:
                pct = (c_val / total) * 100
                ax.text(
                    x_center,
                    green_top / 2,  # halfway in green
                    f"{pct:.0f}%",
                    ha="center", va="center", color="white", fontsize=20
                )

            # Also label the total on top
            ax.text(
                x_center,
                c_val + i_val + 0.5,
                f"{total}",
                ha="center", va="bottom", fontsize=18, color="black"
            )

    # ---- X-axis ticks and labels ----
    ax.set_xticks([x for x in x_indices])
    ax.set_xticklabels(extended_clauses, rotation=0)  # or rotate if you prefer

    ax.set_xlabel("Correctness", fontsize=24)
    ax.set_ylabel("Queries' count", fontsize=24)
    # Possibly rotate x-axis labels if crowded
    plt.xticks(rotation=45, ha='right')
    # Tick labels
    ax.tick_params(axis='x', labelsize=20)
    ax.tick_params(axis='y', labelsize=20)

    # Build a legend that includes:
    #  1) The 4 quizzes (first bar label),
    #  2) "Correct portion" vs. "Incorrect portion",
    #  3) The distinct hatch patterns for the 4 quizzes.
    import matplotlib.patches as mpatches
    correct_patch = mpatches.Patch(facecolor="green", edgecolor="black", label="Correct portion")
    incorrect_patch = mpatches.Patch(facecolor="red", edgecolor="black", label="Incorrect portion")
    # We already have "Quiz1" label in the green bar for the first quiz only,
    # so let's add a separate patch for each quiz's hatch for clarity:
    quiz_legend_handles = []
    for i in range(4):
        quiz_legend_handles.append(
            mpatches.Patch(
                facecolor="white", edgecolor="black", 
                hatch=hatch_patterns[i], 
                label=quiz_names[i]
            )
        )

    # Retrieve existing bar labels from the axes
    existing_handles, existing_labels = ax.get_legend_handles_labels()
    # Add the correct/incorrect patch
    existing_handles.append(correct_patch)
    existing_handles.append(incorrect_patch)
    existing_labels.append("Correct")
    existing_labels.append("Incorrect")
    # Add quiz-specific patches
    # so that each quiz's hatch is shown in the legend
    existing_handles.extend(quiz_legend_handles)
    existing_labels.extend(quiz_names)

    ax.legend(
        existing_handles, 
        existing_labels, 
        loc="upper right", 
        fontsize=20
       #bbox_to_anchor=(1.6, 1)
    )

    plt.tight_layout()
    plt.savefig("comparison_quizzes_clauses_side_by_side.png", dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()
