import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def read_grades(file_path):
    return pd.read_csv(file_path)

def merge_grades(original_grades, final_grades, question_number):
    """
    Merge grades for the same question from two data systems based on student ID.
    
    Parameters:
    - original_grades: DataFrame, grades from the original system.
    - final_grades: DataFrame, grades from the final system.
    - question_number: str, the specific question number to analyze.
    
    Returns:
    - DataFrame with merged grades data for the specific question.
    """
    # Filter data for the specific question (Note: question_number is now expected to be a string)
    original_specific = original_grades[original_grades['Q #'] == question_number]
    final_specific = final_grades[final_grades['Q #'] == question_number]
    
    # Merge data on 'id'
    merged_data = pd.merge(original_specific, final_specific, on='Org Defined ID', suffixes=('_original', '_final'))
    return merged_data


def plot_grade_differences_violin(merged_grades):
    """
    Enhanced violin plot of score differences with individual data points, customized appearance, and a grid for better readability.
    
    Parameters:
    - merged_grades: DataFrame, merged grades data for a specific question.
    """
    # Calculate the difference in scores
    merged_grades['score_difference'] = merged_grades['Score_final'] - merged_grades['Score_original']
    
    # Violin plot
    plt.figure(figsize=(10, 6))
    parts = plt.violinplot(merged_grades['score_difference'], showmeans=False, showmedians=True)
    
    # Customizing the violin plot appearance
    for pc in parts['bodies']:
        pc.set_facecolor('skyblue')
        pc.set_edgecolor('black')
        pc.set_alpha(0.7)
    
    # Custom median color
    parts['cmedians'].set_color('red')
    
    # Adding individual data points
    plt.scatter([1] * len(merged_grades['score_difference']), merged_grades['score_difference'], alpha=0.4, color='darkblue', s=10)
    
    plt.xticks([1], ['Score Difference'])
    plt.ylabel('Score Difference')
    plt.title('Enhanced Violin Plot of Score Differences with Grid')
    
    # Adding a grid
    plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.5)
    
    # Save the plot to a file
    plt.savefig('grade_differences_violin.png')  # Save the plot as a PNG file
    plt.close()  # Close the plot figure to free up memory
   
    
def export_score_differences_to_csv(merged_grades, file_name='score_differences.csv'):
    """
    Export the score differences between the original and final systems to a CSV file.
    
    Parameters:
    - merged_grades: DataFrame, merged grades data including the score differences.
    - file_name: str, the name of the file to save the score differences to.
    """
    # Assuming 'score_difference' column already exists; if not, calculate it
    if 'score_difference' not in merged_grades.columns:
        merged_grades['score_difference'] = merged_grades['Score_final'] - merged_grades['Score_original']
    
    # Select relevant columns for export, if needed
    export_columns = ['Answer_original', 'Score_original', 'Score_final', 'score_difference']
    # Check if all specified columns exist in the DataFrame, adjust as needed
    existing_columns = [col for col in export_columns if col in merged_grades.columns]
    
    # Export to CSV
    merged_grades[existing_columns].to_csv(file_name, index=False)
    print(f"Score differences exported to {file_name}")
    
def plot_multiple_grade_differences_violin_separate_files(original_grades, final_grade_files, figsize=(24, 8)):
    """
    Plot violin plots for multiple questions' score differences in a single figure,
    handling each question's final grades from separate files. Uses custom labels for questions.
    
    Parameters:
    - original_grades: DataFrame, grades from the original system.
    - final_grade_files: dict, a mapping of question numbers to paths of their respective final grades CSV files.
    - figsize: tuple, figure size.
    """
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
    plt.savefig('multiple_grade_differences_violin.png')



def summarize_score_differences_in_table(original_grades, final_grade_files):
    summary_data = []  # To store summary data for each question
    
    for question_number, file_path in final_grade_files.items():
        # Read the final grades for the current question
        final_grades = pd.read_csv(file_path)
        
        # Merge grades for the current question
        merged_grades = merge_grades(original_grades, final_grades, question_number)
        
        # Calculate the difference in scores
        merged_grades['score_difference'] = merged_grades['Score_final'] - merged_grades['Score_original']
        
        # Calculate counts of score differences
        counts = merged_grades['score_difference'].value_counts().sort_index()
        
        # Prepare the summary data for the current question
        summary_for_question = {'Question': question_number}
        for difference, count in counts.items():
            summary_for_question[f' {difference}'] = count
        
        summary_data.append(summary_for_question)
    
    # Convert the summary data to a DataFrame for easy display
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv('summary_score_differences.csv', index=False)
    
    # Display the table
    print(summary_df.to_string(index=False))



def main(original_file_path, final_file_path, question_number):
    original_grades = read_grades(original_file_path)
    final_grades = read_grades(final_file_path)
    merged_grades = merge_grades(original_grades, final_grades, question_number)
    
    plot_grade_differences_violin(merged_grades)
    export_score_differences_to_csv(merged_grades, 'score_differences.csv')
    #export_score_differences_to_csv(merged_grades, 'score_differences.csv')
    

original_grades = read_grades('289/original_results.csv')
final_grade_files = {
    'IPC033-289 v1': '289/quiz_graded.csv',
    'IPC033-290 v1': '290/quiz_graded.csv',
    'IPC033-291 v1': '291/quiz_graded.csv',
    'IPC033-292 v1': '292/quiz_graded.csv',
    'IPC033-293 v1': '293/quiz_graded.csv',
    'IPC033-294 v1': '294/quiz_graded.csv',
    'IPC033-295 v1': '295/quiz_graded.csv',
    'IPC033-309 v1': '309/quiz_graded.csv'
}
plot_multiple_grade_differences_violin_separate_files(original_grades, final_grade_files)
summarize_score_differences_in_table(original_grades, final_grade_files)
main('290/original_results.csv', '290/quiz_graded.csv', question_number='IPC033-290 v1')

# Reversing the color scheme for the pie chart

# Swapping the colors for contrast
colors_reversed = ['#66b3ff', '#ff9999']
sizes = [74, 26]
labels=['Yes, they were fair', 'No']

fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors_reversed)

# Equal aspect ratio ensures that pie is drawn as a circle.
ax.axis('equal')

# Adding a title with black color
plt.title('Do you believe the grades received from the \nautomated grading system were fair?', color='black')

# Saving the pie chart with the reversed colors
plt.savefig('questionnaire.png')





