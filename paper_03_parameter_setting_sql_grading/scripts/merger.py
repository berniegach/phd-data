import pandas as pd
import os

# Path to the directory containing the files
folder_path = '289/'

# Read the original results
original_df = pd.read_csv(os.path.join(folder_path, 'original_results.csv'))
# We'll keep only the relevant columns from the original file
original_df = original_df[['Org Defined ID', 'Answer', 'Score']]
original_df.rename(columns={'Score': 'original_score'}, inplace=True)

# Dictionary to hold dataframes for each automated grading file
graded_dfs = {}

# Loop over all files in the directory
for filename in os.listdir(folder_path):
    if filename.startswith('quiz_graded_') and filename.endswith('.csv'):
        # Extract x and y from the filename
        parts = filename.rstrip('.csv').split('_')
        x, y = parts[-2], parts[-1]
        # Read the file
        df = pd.read_csv(os.path.join(folder_path, filename))
        # Keep only the necessary columns
        df = df[['Org Defined ID', 'Answer', 'Score']]
        # Rename 'Score' to 'score_x_y' to differentiate between files
        df.rename(columns={'Score': f'score_{x}_{y}'}, inplace=True)
        # Add the dataframe to our dictionary
        graded_dfs[(x, y)] = df

# Merge all dataframes on 'Org Defined ID' and 'Answer'
final_df = original_df
for key, df in graded_dfs.items():
    final_df = pd.merge(final_df, df, on=['Org Defined ID', 'Answer'], how='left')

# Save the final merged dataframe to a new CSV file
final_df.to_csv(os.path.join(folder_path, 'merged_grades.csv'), index=False)

print("Merging complete and file saved as 'merged_results.csv'.")

