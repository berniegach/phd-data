import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata


def read_grades(file_path):
    return pd.read_csv(file_path)

def merge_grades(original_grades, final_grades, question_number):
    # Filter data for the specific question (Note: question_number is now expected to be a string)
    original_specific = original_grades[original_grades['Q #'] == question_number]
    final_specific = final_grades[final_grades['Q #'] == question_number]
    
    # Merge data on 'id'
    merged_data = pd.merge(original_specific, final_specific, on='Org Defined ID', suffixes=('_original', '_final'))
    return merged_data

def export_score_differences_to_csv(merged_grades, file_name='score_differences.csv'):
    # Assuming 'score_difference' column already exists; if not, calculate it
    if 'score_difference' not in merged_grades.columns:
        merged_grades['score_difference'] = merged_grades['Score_final'] - merged_grades['Score_original']
    
    # Filter for non-zero score differences
    non_zero_differences = merged_grades[merged_grades['score_difference'] != 0]
    
    # Select relevant columns for export
    export_columns = ['Org Defined ID','Answer_original', 'Score_original', 'Score_final', 'score_difference']
    # Ensure only existing columns are included
    existing_columns = [col for col in export_columns if col in non_zero_differences.columns]
    
    # Export to CSV, including only non-zero differences
    non_zero_differences[existing_columns].to_csv(file_name, index=False)
    print(f"Score differences exported to {file_name}")


def main(original_file_path, final_grade_files):
    """
    Main function to read grades, merge them, and plot the differences.
    
    Parameters:
    - original_file_path: str, path to the original grades CSV file.
    - final_file_path: str, path to the final grades CSV file.
    - question_number: str, the specific question number to analyze.
    """
    original_grades = read_grades(original_file_path)
    for i, (question_number, file_path) in enumerate(final_grade_files.items(), start=1):
        final_grades = pd.read_csv(file_path)
        merged_grades = merge_grades(original_grades, final_grades, question_number)
        
        # Extract a, b, c values from the file path
        a, b, c = file_path.split('_')[-3:]

        # The filename will be e.g. score_differences_IPC033-289 v1_289_quiz_graded_0_0_0.csv
        filename = f'score_differences_{question_number}_{a}_{b}_{c}.csv'

        # Replace the / with _ in the filename
        filename = filename.replace('/', '_')
        # Remove empty spaces in the filename
        filename = filename.replace(' ', '')
        # Remove specific parts of the filename
        filename = filename.replace('IPC033-', '')
        filename = filename.replace('v1_', '')
        filename = filename.replace('quiz_graded', '')

        export_score_differences_to_csv(merged_grades, filename)


# Define a function to filter out groups with no change in 'score_difference'
def filter_unchanged_score_differences(group):
    return group['score_difference'].nunique() > 1

def merge_all_differences_into_one(output_file_name='all_score_differences.csv'):
    """
    Reads all score difference files from the current directory, merges them, and exports to a single CSV file.
    
    Parameters:
    - output_file_name: str, the name of the output CSV file.
    """
    directory_path = os.getcwd()  # Gets the current working directory
    all_files = [f for f in os.listdir(directory_path) if f.startswith('score_differences') and f.endswith('.csv')]
    all_data_frames = []
    
    for file_name in all_files:
        file_path = os.path.join(directory_path, file_name)
        df = pd.read_csv(file_path)
        # Add a column to each DataFrame to identify the source file
        df['filename'] = file_name
        all_data_frames.append(df)
    
    # Concatenate all DataFrames in the list
    combined_df = pd.concat(all_data_frames, ignore_index=True)
    
    # Sort by 'Org Defined ID' if you want rows with the same ID to follow each other
    combined_df = combined_df.sort_values(by=['Org Defined ID', 'Answer_original'])

    # Group by 'Org Defined ID' and 'Answer_original', then apply the filter function
    filtered_df = combined_df.groupby(['Org Defined ID', 'Answer_original']).filter(filter_unchanged_score_differences)

    # Use regular expression to extract the last two numbers before '.csv'
    filtered_df[['text', 'tree']] = filtered_df['filename'].str.extract(r'.*_(\d+)_(\d+)\.csv$')

    # Convert the new columns to an appropriate type (int or float) if necessary
    filtered_df['text'] = filtered_df['text'].astype(int)
    filtered_df['tree'] = filtered_df['tree'].astype(int)
    filtered_df = filtered_df.sort_values(by=['Org Defined ID', 'Answer_original', 'text', 'tree'])

    # Get a lst of all column names except the first one
    columns = filtered_df.columns[1:]

    #dro the duuplicate rows
    filtered_df = filtered_df.drop_duplicates(subset=columns)

    
    # Export to a single CSV file
    filtered_df.to_csv(output_file_name, index=False)
    print(f"All data merged and exported to {output_file_name}")

def plot_multiple_grade_differences_violin_separate_files(original_grades, final_grade_files, filename, figsize=(24, 8)):
    plt.figure(figsize=figsize, tight_layout=True)  # Adjust the figure size as needed
    
    # Generate new labels (T1, T2, T3, ...) for the questions
    new_labels = [f'Q{i}' for i in range(1, len(final_grade_files) + 1)]
    
    # Keep track of the position for each violin plot
    positions = []
    
    for i, (question_number, file_path) in enumerate(final_grade_files.items(), start=1):
        # Read the final grades for the current question
        final_grades = pd.read_csv(file_path)
        
        # Merge grades for the current question
        merged_grades = merge_grades(original_grades, final_grades, question_number)
        
        # Calculate the difference in scores
        merged_grades['score_difference'] = merged_grades['Score_final'] - merged_grades['Score_original']
        
        # Create a violin plot for the current question's score differences
        parts = plt.violinplot(merged_grades['score_difference'], positions=[i], showmeans=False, showmedians=True)
        
        # Customizing the violin plot appearance
        for pc in parts['bodies']:
            pc.set_facecolor('skyblue')
            pc.set_edgecolor('black')
            pc.set_alpha(0.7)
        
        # Custom median color
        parts['cmedians'].set_color('red')
        
        # Adding individual data points
        plt.scatter([i] * len(merged_grades['score_difference']), merged_grades['score_difference'], alpha=0.4, color='darkblue', s=10)
        
        # Add the position for this plot
        positions.append(i)
    
    plt.xticks(positions, new_labels,fontsize=17)  # Use the new labels for x-ticks
    plt.ylabel('Score Difference',fontsize=17)
    plt.yticks(fontsize=17)
    #plt.title('Violin Plots of Score Differences for Multiple Questions')
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)
    
    # Optionally, save the plot to a file
    plt.savefig(filename)

def summarize_score_differences_in_table(original_grades, final_grade_files, filename):
    summary_data = []  # To store summary data for each question
    squared_differences = []  # To store squared differences for MSE calculation
    absolute_differences = []  # To store absolute differences for MAD calculation
    
    for question_number, file_path in final_grade_files.items():
        final_grades = pd.read_csv(file_path)
        
        merged_grades = merge_grades(original_grades, final_grades, question_number)
        
        # Calculate the difference in scores
        merged_grades['score_difference'] = merged_grades['Score_final'] - merged_grades['Score_original']
        merged_grades['score_difference'] = merged_grades['score_difference'].round(2)

        # Square the differences for the MSE calculation and append to the list
        squared_differences.extend((merged_grades['score_difference'] ** 2).tolist())

        # Calculate the absolute differences for the MAD calculation and append to the list
        absolute_differences.extend(merged_grades['score_difference'].abs().tolist())
        
        # Calculate counts of score differences
        counts = merged_grades['score_difference'].value_counts().sort_index()
        
        # Prepare the summary data for the current question
        summary_for_question = {'Question': question_number}
        for difference, count in counts.items():
            summary_for_question[f' {difference}'] = count
        
        summary_data.append(summary_for_question)
    
    # Calculate and print the Mean Squared Error (MSE)
    mse = sum(squared_differences) / len(squared_differences)
    mad = sum(absolute_differences) / len(absolute_differences)

    # Round to 3 decimal places
    mse = round(mse, 3)
    mad = round(mad, 3)

    # Append MSE and MAD to the summary data
    mse_row = ['MSE', mse] +[np.nan] * (len(summary_data[0]) - 2)
    mad_row = ['MAD', mad] + [np.nan] * (len(summary_data[0]) - 2)

    mse_row_series = pd.Series(mse_row, index=summary_data[0].keys())
    mad_row_series = pd.Series(mad_row, index=summary_data[0].keys())

    summary_data.append(mse_row_series)
    summary_data.append(mad_row_series)

    #summary_data.append({'Question': 'Mean Squared Error (MSE)', 'MSE': mse})
    #summary_data.append({'Question': 'Mean Absolute Difference (MAD)', 'MAD': mad})

    # Convert the summary data to a DataFrame for easy display
    summary_df = pd.DataFrame(summary_data)
    # Convert columns to integers with NaN support

    
    summary_df.to_csv(filename, index=False)
    
    # Display the table
    print(summary_df.to_string(index=False))
    print(f'Mean Squared Error (MSE): {mse}')
    print(f'Mean Absolute Difference (MAD): {mad}')

def summarize_score_frequencies(original_grades, final_grade_files, filename):
    summary_data = []  # To store summary data for each question
    
    for question_number, file_path in final_grade_files.items():
        final_grades = pd.read_csv(file_path)
        
        # Merge original and final grades
        merged_grades = merge_grades(original_grades, final_grades, question_number)
        
        # Calculate counts of score_original grades
        counts_original = merged_grades['Score_original'].value_counts().sort_index()
        
        # Calculate counts of score_final grades
        counts_final = merged_grades['Score_final'].value_counts().sort_index()
        
        # Prepare the summary data for the current question
        summary_for_question = {'Question': question_number}
        
        for score, count in counts_original.items():
            summary_for_question[f'Original {score}'] = count
            
        for score, count in counts_final.items():
            summary_for_question[f'Final {score}'] = count
        
        summary_data.append(summary_for_question)
    
    # Convert the summary data to a DataFrame for easy display
    summary_df = pd.DataFrame(summary_data)
    # Calculate totals for each column
    totals = summary_df.sum(numeric_only=True)
    totals['Question'] = 'Total'
    
    # Convert the totals Series to a DataFrame and set it as the same format as summary_df
    totals_df = pd.DataFrame(totals).transpose()
    
    # Concatenate the totals row to the DataFrame
    summary_df = pd.concat([summary_df, totals_df], ignore_index=True)

    # Save to CSV
    summary_df.to_csv(filename, index=False)
    
    # Display the table
    print(summary_df.to_string(index=False))

def summarize_score_frequency_totals(folder_path, output_filename):
    summary_totals = []
    
    # Get all CSV files in the specified folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Extract the total row
            total_row = df[df['Question'] == 'Total']
            
            if not total_row.empty:
                # Add the filename or some identifier to the total_row
                total_row['File'] = file_name
                summary_totals.append(total_row)
    
    # Concatenate all the totals into a single DataFrame
    if summary_totals:
        summary_totals_df = pd.concat(summary_totals, ignore_index=True)
        
        # Save the summary totals to a CSV file
        summary_totals_df.to_csv(output_filename, index=False)
        
        # Display the summary table
        print(summary_totals_df.to_string(index=False))
    else:
        print("No totals found in the provided files.")

def plot_mse_mad(directory_path):
    # Dictionary to hold our data
    data = {}

    # Iterate over each file in the directory
    for filename in os.listdir(directory_path):
        if filename.startswith("summary_score_differences") and filename.endswith(".csv"):
            # Extracting the edit distances from the filename
            edit_distances = filename.split('__')[-1].replace('.csv', '')
            
            # Read the CSV file
            df = pd.read_csv(os.path.join(directory_path, filename))
            
            # Extracting MSE and MAD values
            mse_value = df[df['Question'] == 'MSE'].iloc[0, 1] if not df[df['Question'] == 'MSE'].empty else None
            mad_value = df[df['Question'] == 'MAD'].iloc[0, 1] if not df[df['Question'] == 'MAD'].empty else None
            
            # Storing the values in the dictionary
            data[edit_distances] = (mse_value, mad_value)
    
    # Sorting data by edit distances for plotting
    sorted_data = sorted(data.items(), key=lambda x: [int(part) for part in x[0].split('_')])
    distances, values = zip(*sorted_data)
    
    # Filter out consecutive duplicate values
    filtered_distances = []
    filtered_mse_values = []
    filtered_mad_values = []
    last_mse_value, last_mad_value = None, None
    
    for distance, (mse_value, mad_value) in zip(distances, values):
        if mse_value != last_mse_value or mad_value != last_mad_value:
            filtered_distances.append(distance)
            filtered_mse_values.append(mse_value)
            filtered_mad_values.append(mad_value)
            last_mse_value = mse_value
            last_mad_value = mad_value
    
    # Plotting
    plt.figure(figsize=(20, 8))
    #plt.figure(figsize=(10, 6))
    # Plot MSE with values
    plt.plot(filtered_distances, filtered_mse_values, label='MSE', marker='o')
    for i, txt in enumerate(filtered_mse_values):
        plt.text(filtered_distances[i], filtered_mse_values[i], f"{txt:.3f}", ha='center', va='bottom')
    # Plot MAD with values
    plt.plot(filtered_distances, filtered_mad_values, label='MAD', marker='o')
    for i, txt in enumerate(filtered_mad_values):
        plt.text(filtered_distances[i], filtered_mad_values[i], f"{txt:.3f}", ha='center', va='bottom')

    plt.xlabel('Edit Distances')
    plt.ylabel('Values')
    #plt.title('MSE and MAD Values by Edit Distance')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('MSE_MAD_plot.png')

def plot_3d_mse_mad(directory_path):
    # Dictionary to store our data
    data = {}

    # Iterate over each file in the directory
    for filename in os.listdir(directory_path):
        if filename.startswith("summary_score_differences") and filename.endswith(".csv"):
            # Extracting the edit distances from the filename
            distances = filename.split('__')[-1].replace('.csv', '').split('_')
            if len(distances) == 2:
                x, y = int(distances[0]), int(distances[1])

                # Read the CSV file
                df = pd.read_csv(os.path.join(directory_path, filename))

                # Extracting MSE and MAD values
                mse_value = df[df['Question'] == 'MSE'].iloc[0, 1] if not df[df['Question'] == 'MSE'].empty else None
                mad_value = df[df['Question'] == 'MAD'].iloc[0, 1] if not df[df['Question'] == 'MAD'].empty else None

                # Storing the values in the dictionary
                data[(x, y)] = (mse_value, mad_value)

    # Preparing data for plotting
    xy, values = zip(*data.items())
    x, y = zip(*xy)
    mse_values, mad_values = zip(*values)

    # Creating grid points for interpolation
    max_x, max_y = max(x), max(y)
    grid_x, grid_y = np.mgrid[0:max_x:50j, 0:max_y:50j]

    # Interpolating MSE and MAD values
    grid_mse = griddata((x, y), mse_values, (grid_x, grid_y), method='cubic')
    grid_mad = griddata((x, y), mad_values, (grid_x, grid_y), method='cubic')

    # Plotting the 3D surface for MSE
    fig_mse = plt.figure(figsize=(12, 8),tight_layout=True)
    ax_mse = fig_mse.add_subplot(111, projection='3d')
    surf_mse = ax_mse.plot_surface(grid_x, grid_y, grid_mse, cmap='viridis')
    fig_mse.colorbar(surf_mse, ax=ax_mse, label='MSE')
    ax_mse.set_xlabel('Text Edit Distance')
    ax_mse.set_ylabel('Tree Edit Distance')
    ax_mse.set_zlabel('MSE Value')
    #plt.title('3D Surface Plot of MSE Values')
    plt.savefig('3D_Surface_MSE_plot.png')

    # Plotting the 3D surface for MAD
    fig_mad = plt.figure(figsize=(12, 8))
    ax_mad = fig_mad.add_subplot(111, projection='3d')
    surf_mad = ax_mad.plot_surface(grid_x, grid_y, grid_mad, cmap='plasma')
    fig_mad.colorbar(surf_mad, ax=ax_mad, label='MAD')
    ax_mad.set_xlabel('Text Edit Distance')
    ax_mad.set_ylabel('Tree Edit Distance')
    ax_mad.set_zlabel('MAD Value')
    #plt.title('3D Surface Plot of MAD Values')
    plt.savefig('3D_Surface_MAD_plot.png')

    plt.show()

def export_mse_mad_to_csv(directory_path, output_file):
    data = {}

    for filename in os.listdir(directory_path):
        if filename.startswith("summary_score_differences") and filename.endswith(".csv"):
            edit_distances = filename.split('__')[-1].replace('.csv', '')
            df = pd.read_csv(os.path.join(directory_path, filename))
            mse_value = df[df['Question'] == 'MSE'].iloc[0, 1] if not df[df['Question'] == 'MSE'].empty else None
            mad_value = df[df['Question'] == 'MAD'].iloc[0, 1] if not df[df['Question'] == 'MAD'].empty else None
            data[edit_distances] = (mse_value, mad_value)
    
    # Sorting the data by edit distances for a consistent output
    sorted_data = sorted(data.items(), key=lambda x: x[0])
    distances, values = zip(*sorted_data)
    mse_values, mad_values = zip(*values)
    
    # Creating a DataFrame from the collected data
    output_df = pd.DataFrame({
        'sn_sm_rs': distances,
        'MSE': mse_values,
        'MAD': mad_values
    })
    
    # Writing the DataFrame to a CSV file
    output_df.to_csv(output_file, index=False)
    print(f"Data exported successfully to {output_file}")



original_grades = read_grades('2024/289/289/original_results.csv')
#original_grades = read_grades('2024_april/updated_original_corrected.csv')
# Initial structure for final_grade_files with placeholders for the numbers to iterate
final_grade_files_template = {
    'IPC033-289 v1': '2024/289/quiz_graded_sn{0}_sm{1}_rs{2}.csv',
    'IPC033-290 v1': '2024/290/quiz_graded_sn{0}_sm{1}_rs{2}.csv',
    'IPC033-291 v1': '2024/291/quiz_graded_sn{0}_sm{1}_rs{2}.csv',
    'IPC033-292 v1': '2024/292/quiz_graded_sn{0}_sm{1}_rs{2}.csv',
    'IPC033-293 v1': '2024/293/quiz_graded_sn{0}_sm{1}_rs{2}.csv',
    'IPC033-294 v1': '2024/294/quiz_graded_sn{0}_sm{1}_rs{2}.csv',
    'IPC033-295 v1': '2024/295/quiz_graded_sn{0}_sm{1}_rs{2}.csv',
    'IPC033-309 v1': '2024/309/quiz_graded_sn{0}_sm{1}_rs{2}.csv'
}
"""final_grade_files_template = {
    'IPC033-231 v1': '2024_april/231/quiz_graded_sn{0}_sm{1}_rs{2}.csv',
    'IPC033-232 v1': '2024_april/232/quiz_graded_sn{0}_sm{1}_rs{2}.csv',
    'IPC033-233 v1': '2024_april/233/quiz_graded_sn{0}_sm{1}_rs{2}.csv',
    'IPC033-234 v1': '2024_april/234/quiz_graded_sn{0}_sm{1}_rs{2}.csv',
    'IPC033-235 v1': '2024_april/235/quiz_graded_sn{0}_sm{1}_rs{2}.csv',
    'IPC033-236 v1': '2024_april/236/quiz_graded_sn{0}_sm{1}_rs{2}.csv',
    'IPC033-246 v1': '2024_april/246/quiz_graded_sn{0}_sm{1}_rs{2}.csv',
    'IPC033-253 v1': '2024_april/253/quiz_graded_sn{0}_sm{1}_rs{2}.csv'
}"""

valid_numbers = [0, 2, 3]

for i in valid_numbers:  # Iterates through 0 to 5 for the first number
    for j in valid_numbers:  # Iterates through 0 to 5 for the second number
        for k in valid_numbers:
            # Generate the final_grade_files for the current iteration
            final_grade_files = {key: value.format(i, j, k) for key, value in final_grade_files_template.items()}
            
            # Generate textfile_name based on the current iteration
            csvfile_name_3 = f'multiple_differences__{i}_{j}_{k}.csv'

            # Generate png file name based on the current iteration
            png_file = f'multiple_grade_differences_violin__{i}_{j}_{k}.png'
            summary_file = f'summary_score_differences__{i}_{j}_{k}.csv'
            frequencies_file = f'summary_score_frequencies__{i}_{j}_{k}.csv'

            # Call the main function with the current iteration's final_grade_files and textfile_name
            #main('289/original_results.csv', final_grade_files)
            # Call the plot function with the original_grades and final_grade_files
            #plot_multiple_grade_differences_violin_separate_files(original_grades, final_grade_files, png_file)
            # Call the summary function with the original_grades and final_grade_files
            #summarize_score_differences_in_table(original_grades, final_grade_files, summary_file)
            summarize_score_frequencies(original_grades, final_grade_files, frequencies_file)
#plot_3d_mse_mad('2024_april/all/')
#export_mse_mad_to_csv('2024_april/all/', 'mse_mad_values.csv')
#export_mse_mad_to_csv('2024_april/253/', 'mse_mad_values.csv')
#merge_all_differences_into_one()
summarize_score_frequency_totals(os.getcwd(), 'summary_totals.csv')            

