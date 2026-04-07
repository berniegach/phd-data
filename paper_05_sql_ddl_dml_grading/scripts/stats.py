import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import matplotlib as mpl
from matplotlib.patches import Patch
from wordcloud import WordCloud

# ─── Set all fonts to size 20 ─────────────────────────────────────────────────
mpl.rcParams.update({
    'font.size':           20,   # default text
    'axes.titlesize':      20,   # axes title
    'axes.labelsize':      20,   # x & y labels
    'xtick.labelsize':     20,   # tick labels
    'ytick.labelsize':     20,
    'legend.fontsize':     20,
    'figure.titlesize':    20,
})

def classify_outcome(feedback):
    """
    Classify each Feedback string as 'Unparseable' if it contains
    'not parseable', otherwise as 'Correct' if it contains 🟢,
    else 'Incorrect'. We'll treat 'Correct' and 'Incorrect' as
    both being 'Parseable'.
    """
    text = str(feedback).strip().lower()
    if 'not parseable' in text:
        return 'Unparseable'
    if '🟢' in str(feedback):
        return 'Correct'
    return 'Incorrect'

# Years and questions to iterate over
years = [2021, 2022, 2023, 2024, 2025]
questions = [1, 2, 3, 4, 5, 6]

# Base directory for all charts
output_base = "all_charts"
os.makedirs(output_base, exist_ok=True)

# Colors and hatch patterns for parseable/unparseable
parse_color = '#4daf4a'      # green for parseable (strong even in B/W)
unparse_color = '#e41a1c'    # red for unparseable (strong even in B/W)
parse_hatch = '///'          # hatch for parseable
unparse_hatch = '\\\\\\'     # hatch for unparseable

for q in questions:
    # Create a subfolder for this question
    question_dir = os.path.join(output_base, f"Q{q}")
    os.makedirs(question_dir, exist_ok=True)

    # ─── 1. Load & concatenate all years for this question
    dfs = []
    for year in years:
        fp = f'lab-{year}/{q}/grading_results.csv'
        if not os.path.exists(fp):
            print(f"Warning: File not found: {fp}. Skipping year {year}.")
            continue
        df_temp = pd.read_csv(fp)
        df_temp['year'] = year
        dfs.append(df_temp)
    if not dfs:
        continue

    df_q = pd.concat(dfs, ignore_index=True)

    # ─── 2. Classify semantic outcome for each row
    df_q['outcome'] = df_q['Feedback'].apply(classify_outcome)

    # ─── 3. Compute parseable vs unparseable counts per year
    total_counts = df_q.groupby('year').size()
    unparseable_counts = df_q[df_q['outcome'] == 'Unparseable'].groupby('year').size()
    parseable_counts = total_counts.subtract(unparseable_counts, fill_value=0)

    df_counts = pd.DataFrame({
        'Parseable': parseable_counts,
        'Unparseable': unparseable_counts
    }).fillna(0)

    df_pct = df_counts.div(df_counts.sum(axis=1), axis=0)

    # ─── 4. Plot Parseable vs. Unparseable (stacked bar with color + hatch)
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(years))
    vals_parse = df_pct['Parseable'].reindex(years).fillna(0).values
    vals_unparse = df_pct['Unparseable'].reindex(years).fillna(0).values

    ax.bar(
        x, vals_parse, width=0.6,
        label='Parseable',
        facecolor=parse_color,
        edgecolor='black',
        hatch=parse_hatch
    )
    ax.bar(
        x, vals_unparse, width=0.6,
        bottom=vals_parse,
        label='Unparseable',
        facecolor=unparse_color,
        edgecolor='black',
        hatch=unparse_hatch
    )

    # Annotate percentage labels on each segment
    for i in range(len(years)):
        p_val = vals_parse[i]
        if p_val > 0:
            ax.text(
                x[i], p_val / 2, f'{p_val * 100:.1f}%',
                ha='center', va='center', color='white', fontsize=16
            )
        u_val = vals_unparse[i]
        if u_val > 0:
            ax.text(
                x[i], p_val + u_val / 2, f'{u_val * 100:.1f}%',
                ha='center', va='center', color='white', fontsize=16
            )

    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years], rotation=0)
    ax.set_xlabel('Year')
    ax.set_ylabel('Proportion of Queries')
    #ax.set_title(f'Q{q}: Parseable vs. Unparseable (%)')
    legend_handles = [
        Patch(facecolor=parse_color, edgecolor='black', hatch=parse_hatch, label='Parseable'),
        Patch(facecolor=unparse_color, edgecolor='black', hatch=unparse_hatch, label='Unparseable')
    ]
    ax.legend(handles=legend_handles, loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_parseable_outcome.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── 5. Extract clauses, errors, suggestions by regex
    clauses = (
        df_q['Feedback']
          .str.extractall(r'✅\s*(?P<clause>[^\n\r]+)')
          .reset_index()
          .rename(columns={'level_0': 'row'})[['row','clause']]
    )
    clauses['year'] = df_q.loc[clauses['row'], 'year'].values

    errors = (
        df_q['Feedback']
          .str.extractall(r'❌\s*(?P<error>[^\n\r]+)')
          .reset_index()
          .rename(columns={'level_0': 'row'})[['row','error']]
    )
    errors['year'] = df_q.loc[errors['row'], 'year'].values

    suggestions = (
        df_q['Feedback']
          .str.extractall(r'💡\s*(?P<suggestion>.+)')
          .reset_index()
          .rename(columns={'level_0': 'row'})[['row','suggestion']]
    )
    suggestions['year'] = df_q.loc[suggestions['row'], 'year'].values

    # Add per-query counts
    df_q['error_count']      = df_q.index.map(errors.groupby('row').size()).fillna(0).astype(int)
    df_q['suggestion_count'] = df_q.index.map(suggestions.groupby('row').size()).fillna(0).astype(int)
    df_q['clause_count']     = df_q.index.map(clauses.groupby('row').size()).fillna(0).astype(int)

    # ─── 6. Clause-Level Correctness Heatmap
    year_totals   = df_q.groupby('year').size()
    clause_counts = clauses.groupby(['year','clause']).size().unstack(fill_value=0)
    clause_frac   = clause_counts.div(year_totals, axis=0)

    fig, ax = plt.subplots(figsize=(8, 5))
    # Use a sequential blue colormap (Blues) for better B/W conversion
    cax = ax.imshow(clause_frac, aspect='auto', cmap='Blues')
    fig.colorbar(cax, label='Proportion of Queries')
    ax.set_xticks(np.arange(len(clause_frac.columns)))
    ax.set_xticklabels(clause_frac.columns, rotation=45, ha='right')
    ax.set_yticks(np.arange(len(clause_frac.index)))
    ax.set_yticklabels(clause_frac.index)
    #ax.set_xlabel('Clause')
    ax.set_ylabel('Year')
    #ax.set_title(f'Q{q}: Clause-Level Correctness by Year')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_clause_heatmap.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── 7. Error-Category Trends Over Years
    error_counts = errors.groupby(['year','error']).size().unstack(fill_value=0)
    error_pct    = error_counts.div(df_q.groupby('year').size(), axis=0)

    fig, ax = plt.subplots(figsize=(8, 5))
    # Choose three distinct colors for the top‐3 errors; others cycle automatically
    line_colors = ['#377eb8', '#e41a1c', '#4daf4a']  # blue, red, green
    for idx, err in enumerate(error_pct.columns):
        color = line_colors[idx % len(line_colors)]
        ax.plot(error_pct.index, error_pct[err], marker='o', label=err, color=color)
    ax.set_xlabel('Year')
    ax.set_ylabel('Proportion of Queries')
    #ax.set_title(f'Q{q}: Error-Category Trends Over Years')
    ax.legend(bbox_to_anchor=(1, 0.5), loc='center left')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_error_trends.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── 8. Suggestions-per-Query Distribution (boxplot)
    fig, ax = plt.subplots(figsize=(6, 4))
    data = [df_q[df_q['year']==y]['suggestion_count'] for y in years]
    box = ax.boxplot(data, labels=years, patch_artist=True)
    # Color the boxes a medium‐dark blue
    for patch in box['boxes']:
        patch.set_facecolor('#377eb8')
        patch.set_edgecolor('black')
        patch.set_hatch('///')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Suggestions')
    #ax.set_title(f'Q{q}: Suggestions per Query by Year')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_suggestion_boxplot.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── 9. Top-10 Error Phrases & Co-occurrence
    top10 = errors['error'].value_counts().head(10).sort_values()
    total_top10 = top10.sum()

    fig, ax = plt.subplots(figsize=(8, 6))
    # Use a bold navy color for bars (distinct in B/W)
    top10.plot.barh(ax=ax, color='#1f78b4', edgecolor='black', hatch='///')
    ax.set_xlabel('Count')
    ax.set_ylabel('Error Phrase')
    #ax.set_title(f'Q{q}: Top 10 Error Phrases (All Years)')
    for patch in ax.patches:
        width = patch.get_width()
        pct = width / total_top10 * 100
        ax.text(
            width + total_top10 * 0.005,
            patch.get_y() + patch.get_height()/2,
            f"{pct:.1f}%",
            va='center'
        )
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_top10_errors.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    err_matrix = (
        errors
        .assign(flag=1)
        .pivot_table(index='row', columns='error', values='flag', aggfunc='sum', fill_value=0)
    )
    err_matrix = (err_matrix[top10.index] > 0).astype(int)
    co_mat_err = err_matrix.T.dot(err_matrix)

    fig, ax = plt.subplots(figsize=(6, 5))
    # Use a sequential orange colormap (OrRd) for co-occurrence
    cax = ax.imshow(co_mat_err, aspect='equal', cmap='OrRd')
    fig.colorbar(cax, label='Number of Queries')
    labels_err = co_mat_err.index
    ax.set_xticks(np.arange(len(labels_err)))
    ax.set_xticklabels(labels_err, rotation=45, ha='right')
    ax.set_yticks(np.arange(len(labels_err)))
    ax.set_yticklabels(labels_err)
    #ax.set_title(f'Q{q}: Error-Phrase Co-occurrence')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_error_cooccurrence.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── 10. Error-Count Boxplot by Year
    fig, ax = plt.subplots(figsize=(6, 4))
    data_err = [df_q[df_q['year']==y]['error_count'] for y in years]
    box = ax.boxplot(data_err, labels=years, patch_artist=True)
    for patch in box['boxes']:
        patch.set_facecolor('#ff7f00')  # a distinct orange
        patch.set_edgecolor('black')
        patch.set_hatch('xxx')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Errors')
    #ax.set_title(f'Q{q}: Error Count per Query by Year')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_errorcount_boxplot.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── 11. Mean Errors & Suggestions Over Time
    agg = df_q.groupby('year')[['error_count', 'suggestion_count']].mean()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(agg.index, agg['error_count'], marker='o', color='#e7298a', linestyle='--', label='Avg Errors')  # magenta dashed
    ax.plot(agg.index, agg['suggestion_count'], marker='s', color='#66a61e', linestyle='-', label='Avg Suggestions')  # green solid
    ax.set_xlabel('Year')
    ax.set_ylabel('Average Count')
    #ax.set_title(f'Q{q}: Avg Errors & Suggestions per Query')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_avg_err_sugg.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── 12. Errors vs. Suggestions Scatter (by Outcome)
    fig, ax = plt.subplots(figsize=(6, 5))
    markers = {'Correct': 'o', 'Incorrect': 's', 'Unparseable': 'X'}
    colors = {'Correct': '#1b9e77', 'Incorrect': '#d95f02', 'Unparseable': '#7570b3'}
    for outcome, grp in df_q.groupby('outcome'):
        ax.scatter(
            grp['error_count'],
            grp['suggestion_count'],
            label=outcome,
            alpha=0.8,
            s=40,
            marker=markers[outcome],
            edgecolor='black',
            facecolor=colors[outcome]
        )
    ax.set_xlabel('Number of Errors')
    ax.set_ylabel('Number of Suggestions')
    #ax.set_title(f'Q{q}: Errors vs. Suggestions per Query')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_err_vs_sugg_scatter.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── 13. Top-10 Suggestion Phrases & Co-occurrence
    top_sug = suggestions['suggestion'].value_counts().head(10).sort_values()
    total_top_sug = top_sug.sum()

    fig, ax = plt.subplots(figsize=(8, 6))
    # Use a strong teal color for bars
    top_sug.plot.barh(ax=ax, color='#1f78b4', edgecolor='black', hatch='\\\\\\')
    ax.set_xlabel('Count')
    ax.set_ylabel('Suggestion Phrase')
    #ax.set_title(f'Q{q}: Top 10 Suggestion Phrases')
    for patch in ax.patches:
        width = patch.get_width()
        pct = width / total_top_sug * 100
        ax.text(
            width + total_top_sug * 0.005,
            patch.get_y() + patch.get_height()/2,
            f"{pct:.1f}%",
            va='center'
        )
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_top10_suggestions.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    sug_matrix = (
        suggestions
        .assign(flag=1)
        .pivot_table(index='row', columns='suggestion', values='flag', aggfunc='sum', fill_value=0)
    )
    sug_matrix = (sug_matrix[top_sug.index] > 0).astype(int)
    co_mat_sug = sug_matrix.T.dot(sug_matrix)

    fig, ax = plt.subplots(figsize=(6, 5))
    # Use a sequential purple colormap (PuBu) for co-occurrence
    cax = ax.imshow(co_mat_sug, aspect='equal', cmap='PuBu')
    fig.colorbar(cax, label='Number of Queries')
    labels_sug = co_mat_sug.index
    ax.set_xticks(np.arange(len(labels_sug)))
    ax.set_xticklabels(labels_sug, rotation=45, ha='right')
    ax.set_yticks(np.arange(len(labels_sug)))
    ax.set_yticklabels(labels_sug)
    #ax.set_title(f'Q{q}: Suggestion-Phrase Co-occurrence')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_sugg_cooccurrence.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── 14. Statement Type Distribution by Year
    df_q['stmt_type'] = df_q['Query'].str.strip().str.split().str[0].str.upper()
    stmt_counts = df_q.groupby(['year','stmt_type']).size().unstack(fill_value=0)
    stmt_pct    = stmt_counts.div(stmt_counts.sum(axis=1), axis=0)

    fig, ax = plt.subplots(figsize=(8, 4))
    # Use two contrasting colors with different hatch patterns
    stmt_pct.plot(
        kind='bar',
        stacked=True,
        ax=ax,
        color=['#a6cee3', '#1f78b4'],
        edgecolor='black'
    )
    # Apply hatches: first column '///', second '\\\\\'
    for bar_container, hatch in zip(ax.containers, ['///', '\\\\\\']):
        for bar in bar_container:
            bar.set_hatch(hatch)
    ax.set_xlabel('Year')
    ax.set_ylabel('Proportion of Queries')
    #ax.set_title(f'Q{q}: Statement Type Distribution by Year')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_stmt_type_dist.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── 15. Correct Clauses vs. Errors Scatter (by Year)
    fig, ax = plt.subplots(figsize=(6, 5))
    cmap = plt.get_cmap('tab10')
    for idx, (year, grp) in enumerate(df_q.groupby('year')):
        ax.scatter(
            grp['clause_count'], grp['error_count'],
            label=year,
            alpha=0.8,
            s=40,
            marker='o',
            edgecolor='black',
            facecolor=cmap(idx)
        )
    ax.set_xlabel('Number of Correct Clauses')
    ax.set_ylabel('Number of Errors')
    #ax.set_title(f'Q{q}: Correct Clauses vs. Errors')
    ax.legend(title='Year')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_clause_vs_error_scatter.png'), dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── 16. Word Cloud of Suggestion Phrases
    all_sugs = " ".join(suggestions['suggestion'].tolist())
    if len(all_sugs.strip()) > 0:
        wc = WordCloud(
            width=800, height=400,
            background_color='white',
            colormap='viridis'
        ).generate(all_sugs)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        #ax.set_title(f'Q{q}: Word Cloud of Suggestion Phrases')
        plt.tight_layout()
        plt.savefig(os.path.join(question_dir, f'Q{q}_suggestion_wordcloud.png'), dpi=300, bbox_inches='tight')
        plt.close(fig)

    print(f"Finished all charts for Q{q}")
