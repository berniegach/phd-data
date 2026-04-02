import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import seaborn as sns

def find_csv_files(root_dir):
    """
    Find all 'text.csv' files within the given root directory and its subdirectories.
    """
    csv_files = []
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if file == 'quiz_graded.csv':
                csv_files.append(os.path.join(subdir, file))
    return csv_files

def read_and_accumulate_csv_data(csv_files):
    """
    Read each 'quiz_graded.csv' file, concatenates the data into a single DataFrame,
    and adds an "Exercise" column based on file count.
    """
    data_frames = []
    exercise_count = 1  # Start exercise count from 1

    for i, csv_file in enumerate(csv_files):
        data = pd.read_csv(csv_file)

        # Add "Exercise" column with unique counts
        data['Exercise'] = exercise_count
        exercise_count += 1  # Increment count for each file

        data_frames.append(data)

    # Concatenate DataFrames
    df = pd.concat(data_frames, ignore_index=True)

    return df

def plot_cumulative_graph(data, root_dir):
    """
    Plot a cumulative graph from the provided dataframe.
    """
    # Count how many times each score occurs
    counts = data['Score'].value_counts().reset_index()
    counts.columns = ['Score', 'Count']

    # Set the seaborn style
    sns.set(style="whitegrid")

    # Create the bar plot
    plt.figure(figsize=(10,6))
    ax = sns.barplot(x='Score', y='Count', data=counts, palette="deep")
    
    # Add labels to each bar
    for p in ax.patches:
        x = p.get_x() + p.get_width() / 2
        y = p.get_height()
        ax.annotate(str(int(y)), (x, y), ha='center', va='bottom')

    plt.xlabel('Score')
    plt.ylabel('Count')
    #plt.title('Cumulative count')
    #plt.show()

    #save the plot in the same directory as the csv file
    file_dir = os.path.dirname(root_dir)
    output_file = os.path.join(file_dir, 'multiple_bar_graph.png')
    plt.savefig(output_file)

def plot_heatmap(data, root_dir):
    """
    Plot a heatmap from the provided dataframe.
    """

    # Create a pivot table with exercises as columns and questions as rows
    pivot_table = data.pivot_table(values='Score', index='Question', columns='Exercise')


    # Set the seaborn style
    sns.set(style="whitegrid")

    # Create the heatmap
    plt.figure(figsize=(10, 6))  # Adjust figure size as needed
    ax = sns.heatmap(pivot_table, cmap="coolwarm")  # Choose a suitable colormap

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')

    plt.xlabel('Exercise')
    plt.ylabel('Question')
    plt.title('Score Distribution Heatmap')

    # Save the heatmap in the same directory as the CSV files
    file_dir = os.path.dirname(root_dir)
    output_file = os.path.join(file_dir, 'heatmap.png')
    plt.savefig(output_file)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_root_directory>")
        sys.exit(1)

    root_dir = sys.argv[1]
    csv_files = find_csv_files(root_dir)
    if not csv_files:
        print("No 'text.csv' files found in the directory.")
        sys.exit(1)
    
    data = read_and_accumulate_csv_data(csv_files)
    plot_heatmap(data, root_dir)

