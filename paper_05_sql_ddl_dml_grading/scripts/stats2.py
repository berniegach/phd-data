import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import re
import matplotlib as mpl
from matplotlib.patches import Patch

# ─── Set all fonts to size 20 ─────────────────────────────────────────────────
mpl.rcParams.update({
    'font.size':           20,
    'axes.titlesize':      20,
    'axes.labelsize':      20,
    'xtick.labelsize':     20,
    'ytick.labelsize':     20,
    'legend.fontsize':     20,
    'figure.titlesize':    20,
})

def classify_outcome(feedback):
    text = str(feedback).strip().lower()
    if 'not parseable' in text:
        return 'Unparseable'
    if '🟢' in str(feedback):
        return 'Correct'
    return 'Incorrect'

# Years and questions
years = [2021, 2022, 2023, 2024, 2025]
questions = [1, 2, 3, 4, 5, 6]

# Base directory for charts
output_base = "feedback_charts"
os.makedirs(output_base, exist_ok=True)

# Colors and hatches
parse_color = '#4daf4a'
unparse_color = '#e41a1c'
parse_hatch = '///'
unparse_hatch = '\\\\\\'

error_bar_color = '#1f78b4'
error_bar_hatch = '///'
sug_bar_color = '#33a02c'
sug_bar_hatch = '\\\\\\'
error_box_color = '#ff7f00'
error_box_hatch = 'xxx'
sug_box_color = '#377eb8'
sug_box_hatch = '///'
zero_err_color = '#a6cee3'
zero_err_hatch = '||'
feedback_len_color = '#b15928'

stmt_colors = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99']
stmt_hatches = ['///', '\\\\\\', 'xxx', '---', '|||']

for q in questions:
    question_dir = os.path.join(output_base, f"Q{q}")
    os.makedirs(question_dir, exist_ok=True)

    # ─── Load & concatenate all years for question q
    dfs = []
    for year in years:
        fp = f'lab-{year}/{q}/grading_results.csv'
        if not os.path.exists(fp):
            continue
        df_temp = pd.read_csv(fp)
        df_temp['year'] = year
        dfs.append(df_temp)
    if not dfs:
        continue
    df_q = pd.concat(dfs, ignore_index=True)

    # ─── Classify semantic outcome
    df_q['outcome'] = df_q['Feedback'].apply(classify_outcome)

    # ─── Extract errors, suggestions, clauses
    errors = (
        df_q['Feedback']
          .str.extractall(r'❌\s*(?P<error>[^\n\r]+)')
          .reset_index()
          .rename(columns={'level_0': 'row'})[['row', 'error']]
    )
    suggestions = (
        df_q['Feedback']
          .str.extractall(r'💡\s*(?P<suggestion>.+)')
          .reset_index()
          .rename(columns={'level_0': 'row'})[['row', 'suggestion']]
    )
    clauses = (
        df_q['Feedback']
          .str.extractall(r'✅\s*(?P<clause>[^\n\r]+)')
          .reset_index()
          .rename(columns={'level_0': 'row'})[['row', 'clause']]
    )

    df_q['error_count'] = df_q.index.map(errors.groupby('row').size()).fillna(0).astype(int)
    df_q['suggestion_count'] = df_q.index.map(suggestions.groupby('row').size()).fillna(0).astype(int)
    df_q['clause_count'] = df_q.index.map(clauses.groupby('row').size()).fillna(0).astype(int)

    # ─── Chart 1: Parseable vs Unparseable
    total_counts = df_q.groupby('year').size()
    unparseable_counts = df_q[df_q['outcome'] == 'Unparseable'].groupby('year').size()
    parseable_counts = total_counts.subtract(unparseable_counts, fill_value=0)
    df_counts = pd.DataFrame({
        'Parseable': parseable_counts,
        'Unparseable': unparseable_counts
    }).fillna(0)
    df_pct = df_counts.div(df_counts.sum(axis=1), axis=0)

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(years))
    vals_parse = df_pct['Parseable'].reindex(years).fillna(0).values
    vals_unparse = df_pct['Unparseable'].reindex(years).fillna(0).values

    ax.bar(x, vals_parse, width=0.6, facecolor=parse_color, edgecolor='black', hatch=parse_hatch)
    ax.bar(x, vals_unparse, width=0.6, bottom=vals_parse,
           facecolor=unparse_color, edgecolor='black', hatch=unparse_hatch)

    for i in range(len(years)):
        p_val = vals_parse[i]
        if p_val > 0:
            ax.text(x[i], p_val/2, f'{p_val*100:.1f}%', ha='center', va='center',
                    color='white', fontsize=16)
        u_val = vals_unparse[i]
        if u_val > 0:
            ax.text(x[i], p_val + u_val/2, f'{u_val*100:.1f}%', ha='center', va='center',
                    color='white', fontsize=16)

    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years], rotation=0)
    ax.set_xlabel('Year')
    ax.set_ylabel('Proportion of Queries')
    legend_handles = [
        Patch(facecolor=parse_color, edgecolor='black', hatch=parse_hatch, label='Parseable'),
        Patch(facecolor=unparse_color, edgecolor='black', hatch=unparse_hatch, label='Unparseable')
    ]
    ax.legend(handles=legend_handles, loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_parseable_outcome.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── Chart 2: Average Errors & Suggestions per Query
    agg = df_q.groupby('year')[['error_count', 'suggestion_count']].mean()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(agg.index, agg['error_count'], marker='o', linestyle='--',
            color='#e7298a', label='Avg Errors')
    ax.plot(agg.index, agg['suggestion_count'], marker='s', linestyle='-',
            color='#66a61e', label='Avg Suggestions')
    ax.set_xlabel('Year')
    ax.set_ylabel('Average Count')
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_avg_err_sugg.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── Chart 3: Top-10 Error Phrases
    top10_err = errors['error'].value_counts().head(10).sort_values()
    total_err = top10_err.sum()
    fig, ax = plt.subplots(figsize=(8, 6))
    top10_err.plot.barh(ax=ax, color=error_bar_color, edgecolor='black', hatch=error_bar_hatch)
    ax.set_xlabel('Count')
    ax.set_ylabel('Error Phrase')
    for patch in ax.patches:
        width = patch.get_width()
        pct = width / total_err * 100
        ax.text(width + total_err * 0.005,
                patch.get_y() + patch.get_height()/2,
                f'{pct:.1f}%', va='center')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_top10_errors.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── Chart 4a: Top-10 Suggestion Phrases
    top10_sug = suggestions['suggestion'].value_counts().head(10).sort_values()
    total_sug = top10_sug.sum()
    fig, ax = plt.subplots(figsize=(8, 6))
    top10_sug.plot.barh(ax=ax, color=sug_bar_color, edgecolor='black', hatch=sug_bar_hatch)
    ax.set_xlabel('Count')
    ax.set_ylabel('Suggestion Phrase')
    for patch in ax.patches:
        width = patch.get_width()
        pct = width / total_sug * 100
        ax.text(width + total_sug * 0.005,
                patch.get_y() + patch.get_height()/2,
                f'{pct:.1f}%', va='center')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_top10_suggestions.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── Chart 4b: Suggestion Co-occurrence Heatmap
    if not top10_sug.empty:
        # Build pivot: rows = query index, cols = suggestion, cells = count
        sug_rows = suggestions.copy()
        sugs_pivot = sug_rows.pivot_table(
            index='row', columns='suggestion', values='row',
            aggfunc='count', fill_value=0
        )
        # Keep only top10 suggestions that appear
        common_sugs = [s for s in top10_sug.index if s in sugs_pivot.columns]
        sugs_pivot = sugs_pivot[common_sugs] > 0
        co_mat_sug = sugs_pivot.T.dot(sugs_pivot)

        fig, ax = plt.subplots(figsize=(8, 6))
        cax = ax.imshow(co_mat_sug, aspect='equal', cmap='PuBu')
        plt.colorbar(cax, label='Number of Queries')
        labels_sug = co_mat_sug.index
        ax.set_xticks(np.arange(len(labels_sug)))
        ax.set_xticklabels(labels_sug, rotation=45, ha='right')
        ax.set_yticks(np.arange(len(labels_sug)))
        ax.set_yticklabels(labels_sug)
        plt.tight_layout()
        plt.savefig(os.path.join(question_dir, f'Q{q}_sugg_cooccurrence.png'),
                    dpi=300, bbox_inches='tight')
        plt.close(fig)

    # ─── Chart 5: Error Co-occurrence Heatmap (Top-10 Errors)
    if not top10_err.empty:
        err_rows = errors.copy()
        errs_pivot = err_rows.pivot_table(
            index='row', columns='error', values='row',
            aggfunc='count', fill_value=0
        )
        common_errs = [e for e in top10_err.index if e in errs_pivot.columns]
        errs_pivot = errs_pivot[common_errs] > 0
        co_mat_err = errs_pivot.T.dot(errs_pivot)

        fig, ax = plt.subplots(figsize=(8, 6))
        cax = ax.imshow(co_mat_err, aspect='equal', cmap='OrRd')
        plt.colorbar(cax, label='Number of Queries')
        labels_err = co_mat_err.index
        ax.set_xticks(np.arange(len(labels_err)))
        ax.set_xticklabels(labels_err, rotation=45, ha='right')
        ax.set_yticks(np.arange(len(labels_err)))
        ax.set_yticklabels(labels_err)
        plt.tight_layout()
        plt.savefig(os.path.join(question_dir, f'Q{q}_err_cooccurrence.png'),
                    dpi=300, bbox_inches='tight')
        plt.close(fig)

    # ─── Chart 6: Error → Suggestion Mapping Matrix
    if not top10_err.empty and not top10_sug.empty:
        common_errs_map = [e for e in top10_err.index]
        common_sugs_map = [s for s in top10_sug.index]
        mapping = pd.DataFrame(0, index=common_errs_map, columns=common_sugs_map)
        for _, row in errors.iterrows():
            err_phrase = row['error']
            if err_phrase not in mapping.index:
                continue
            row_idx = row['row']
            sug_list = suggestions[suggestions['row'] == row_idx]['suggestion'].tolist()
            for s in sug_list:
                if s in mapping.columns:
                    mapping.loc[err_phrase, s] += 1

        fig, ax = plt.subplots(figsize=(10, 8))
        cax = ax.imshow(mapping.values, aspect='auto', cmap='Greens')
        plt.colorbar(cax, label='Count')
        ax.set_xticks(np.arange(len(mapping.columns)))
        ax.set_xticklabels(mapping.columns, rotation=45, ha='right')
        ax.set_yticks(np.arange(len(mapping.index)))
        ax.set_yticklabels(mapping.index)
        plt.tight_layout()
        plt.savefig(os.path.join(question_dir, f'Q{q}_err_to_sug_mapping.png'),
                    dpi=300, bbox_inches='tight')
        plt.close(fig)

    # ─── Chart 7: Distribution of Errors Per Query (Boxplot)
    fig, ax = plt.subplots(figsize=(6, 4))
    data_err = [df_q[df_q['year'] == y]['error_count'] for y in years]
    bp = ax.boxplot(data_err, labels=years, patch_artist=True)
    for patch in bp['boxes']:
        patch.set_facecolor(error_box_color)
        patch.set_edgecolor('black')
        patch.set_hatch(error_box_hatch)
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Errors')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_errorcount_boxplot.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── Chart 8: Distribution of Suggestions Per Query (Boxplot)
    fig, ax = plt.subplots(figsize=(6, 4))
    data_sug = [df_q[df_q['year'] == y]['suggestion_count'] for y in years]
    bp2 = ax.boxplot(data_sug, labels=years, patch_artist=True)
    for patch in bp2['boxes']:
        patch.set_facecolor(sug_box_color)
        patch.set_edgecolor('black')
        patch.set_hatch(sug_box_hatch)
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Suggestions')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_suggestion_boxplot.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── Chart 9: Percent of Queries with Zero Errors (Bar Chart)
    zero_err_frac = []
    for y in years:
        df_year = df_q[df_q['year'] == y]
        parseable_year = df_year[df_year['outcome'] != 'Unparseable']
        total = len(parseable_year)
        zero = len(parseable_year[parseable_year['error_count'] == 0])
        frac = zero / total if total > 0 else 0
        zero_err_frac.append(frac)
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(years))
    bars = ax.bar(x, zero_err_frac, width=0.6, facecolor=zero_err_color,
                  edgecolor='black', hatch=zero_err_hatch)
    for i, h in enumerate(zero_err_frac):
        ax.text(x[i], h/2, f'{h*100:.1f}%', ha='center', va='center', color='black', fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years], rotation=0)
    ax.set_xlabel('Year')
    ax.set_ylabel('Fraction of Parseable Queries with Zero Errors')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_pct_zero_errors.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── Chart 10: Histogram of Feedback Length (Total Lines)
    df_q['feedback_length'] = df_q['Feedback'].str.count(r'\n') + 1
    lengths = df_q['feedback_length']
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(lengths, bins=range(1, lengths.max() + 2),
            color=feedback_len_color, edgecolor='black')
    ax.set_xlabel('Total Lines in Feedback')
    ax.set_ylabel('Count of Queries')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_feedback_length_hist.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── Chart 11: Statement Type Distribution of Errors (Stacked Bar)
    df_q['stmt_type'] = df_q['Query'].str.strip().str.split().str[0].str.upper()
    stmt_err = errors.copy()
    stmt_err['stmt_type'] = df_q.loc[stmt_err['row'], 'stmt_type'].values
    top5_err = errors['error'].value_counts().head(5).index
    stmt_err_top5 = stmt_err[stmt_err['error'].isin(top5_err)]
    stmt_counts = stmt_err_top5.groupby(['stmt_type', 'error']).size().unstack(fill_value=0)
    stmt_totals = stmt_err_top5.groupby('stmt_type').size()
    stmt_pct = stmt_counts.div(stmt_totals, axis=0)

    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = np.zeros(len(stmt_pct))
    stmt_types = stmt_pct.index.tolist()
    for i, err in enumerate(stmt_pct.columns):
        vals = stmt_pct[err].values
        ax.bar(stmt_types, vals, bottom=bottom, label=err,
               color=stmt_colors[i % len(stmt_colors)],
               edgecolor='black', hatch=stmt_hatches[i % len(stmt_hatches)])
        bottom += vals
    ax.set_xlabel('Statement Type')
    ax.set_ylabel('Proportion of Error Occurrences')
    ax.legend(bbox_to_anchor=(1, 0.5), loc='center left')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_stmt_err_stack.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── Chart 12: Cumulative Unique Error Phrases Over Time
    unique_errors_by_year = []
    seen = set()
    for y in years:
        errs_y = set(errors[errors['row'].isin(df_q[df_q['year'] == y].index)]['error'].unique())
        seen |= errs_y
        unique_errors_by_year.append(len(seen))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(years, unique_errors_by_year, marker='o', color='#e7298a')
    ax.set_xlabel('Year')
    ax.set_ylabel('Cumulative Unique Error Phrases')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_cumulative_errors.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── Chart 13: Error → Suggestion Answer Rate (Top-5 Errors)
    error_to_sug_count = {}
    for err in top5_err:
        total_err_occ = len(errors[errors['error'] == err])
        rows_with_err = errors[errors['error'] == err]['row'].unique()
        had_sug = sum(1 for r in rows_with_err if len(suggestions[suggestions['row'] == r]) > 0)
        error_to_sug_count[err] = (had_sug, total_err_occ)
    errs = list(error_to_sug_count.keys())
    rates = [error_to_sug_count[e][0] / error_to_sug_count[e][1] if error_to_sug_count[e][1] > 0 else 0 for e in errs]

    fig, ax = plt.subplots(figsize=(8, 6))
    x = np.arange(len(errs))
    bars = ax.bar(x, rates, width=0.6, facecolor='#1b9e77', edgecolor='black', hatch='///')
    for i, r in enumerate(rates):
        ax.text(x[i], r/2, f'{r*100:.1f}%', ha='center', va='center', color='white', fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels(errs, rotation=45, ha='right')
    ax.set_xlabel('Error Phrase')
    ax.set_ylabel('Fraction of Occurrences with ≥1 Suggestion')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_err_sug_answer_rate.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ─── Chart 14: Pareto (Cumulative Proportion) of Error Phrases
    all_err_counts = errors['error'].value_counts()
    cum_counts = all_err_counts.cumsum()
    total_all_err = all_err_counts.sum()
    cum_pct = cum_counts / total_all_err

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(all_err_counts.index, cum_pct.values, marker='o', color='#fdbf6f')
    ax.axhline(0.8, color='gray', linestyle='--')
    ax.set_xticks(np.arange(len(all_err_counts.index)))
    ax.set_xticklabels(all_err_counts.index, rotation=45, ha='right')
    ax.set_xlabel('Error Phrase (sorted by frequency)')
    ax.set_ylabel('Cumulative Proportion of All Errors')
    plt.tight_layout()
    plt.savefig(os.path.join(question_dir, f'Q{q}_pareto_errors.png'),
                dpi=300, bbox_inches='tight')
    plt.close(fig)

    print(f"Finished feedback charts for Q{q}")
