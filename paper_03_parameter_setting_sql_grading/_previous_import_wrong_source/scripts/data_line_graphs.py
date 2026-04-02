"""import pandas as pd
import matplotlib.pyplot as plt

def plot_csv_data(file_path):
    # Read the CSV file into a DataFrame
    data = pd.read_csv(file_path)
    
    # Set the 'Question' column as the index
    data.set_index('Question', inplace=True)
    
    # Transpose the DataFrame to get questions as columns for plotting
    data = data.T
    
    # Create a figure and a set of subplots
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    # Plot the first metric on the primary y-axis
    ax1.plot(data.index, data['Min MSE'], marker='o', label='Min MSE', color='blue')
    ax1.plot(data.index, data['Min MAD'], marker='o', label='Min MAD', color='orange')
    ax1.set_xlabel('Questions')
    ax1.set_ylabel('Min MSE and Min MAD', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    
    # Instantiate a second y-axis that shares the same x-axis
    ax2 = ax1.twinx()
    
    # Plot the second metric on the secondary y-axis
    ax2.plot(data.index, data['Text ED MSE'], marker='x', linestyle='--', label='Text ED MSE', color='green')
    ax2.plot(data.index, data['Text ED MAD'], marker='x', linestyle='--', label='Text ED MAD', color='red')
    ax2.set_ylabel('Text ED MSE and Text ED MAD', color='green')
    ax2.tick_params(axis='y', labelcolor='green')
    
    # Instantiate a third y-axis that shares the same x-axis
    ax3 = ax1.twinx()
    ax3.spines['right'].set_position(('outward', 60))  # Offset the third y-axis to the right
    
    # Plot the third metric on the third y-axis
    ax3.plot(data.index, data['Tree ED MSE'], marker='^', linestyle=':', label='Tree ED MSE', color='purple')
    ax3.plot(data.index, data['Tree ED MAD'], marker='^', linestyle=':', label='Tree ED MAD', color='brown')
    ax3.set_ylabel('Tree ED MSE and Tree ED MAD', color='purple')
    ax3.tick_params(axis='y', labelcolor='purple')

    # Instantiate a fourth y-axis that shares the same x-axis
    ax4 = ax1.twinx()
    ax4.spines['right'].set_position(('outward', 120))  # Offset the fourth y-axis further to the right
    
    # Plot the additional metrics on the fourth y-axis
    ax4.plot(data.index, data['Words'], marker='s', linestyle='-.', label='Words', color='pink')
    ax4.plot(data.index, data['Characters'], marker='d', linestyle='-', label='Characters', color='cyan')
    ax4.plot(data.index, data['Clauses'], marker='p', linestyle='--', label='Clauses', color='gray')
    ax4.plot(data.index, data['Keywords'], marker='h', linestyle=':', label='Keywords', color='olive')
    ax4.plot(data.index, data['Variables'], marker='*', linestyle='-', label='Variables', color='teal')
    ax4.set_ylabel('Words, Characters, Clauses, Keywords, Variables', color='pink')
    ax4.tick_params(axis='y', labelcolor='pink')
    
    # Add a title and show the legend
    fig.suptitle('Metrics from CSV Data with Different Scales')
    fig.tight_layout()
    fig.subplots_adjust(top=0.9)  # Adjust the top to make room for the title
    
    # Combine legends from all axes
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    lines4, labels4 = ax4.get_legend_handles_labels()
    ax1.legend(lines + lines2 + lines3 + lines4, labels + labels2 + labels3 + labels4, loc='upper left')

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Show the plot
    plt.show()

# Example usage
file_path = 'data.csv'  # Replace with the path to your CSV file
plot_csv_data(file_path)
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_correlations(file_path):
    # Read the CSV file into a DataFrame
    data = pd.read_csv(file_path)
    
    # Set the 'Question' column as the index
    data.set_index('Question', inplace=True)
    
    # Transpose the DataFrame to get questions as rows and metrics as columns
    data = data.T
    
    # Compute the correlation matrix
    corr_matrix = data.corr()
    
    # Plot the heatmap
    plt.figure(figsize=(12, 12))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
            annot_kws={"size": 18},  # Change annotation font size
            cbar_kws={'label': 'Correlation'})  # Customize colorbar label size)
    plt.title('Correlation Matrix')
    #plt.tight_layout()
    plt.xticks(fontsize = 18, rotation=45)
    plt.yticks(fontsize = 18, rotation=0)
    plt.show()

# Example usage
file_path = 'data2.csv'  # Replace with the path to your CSV file
plot_correlations(file_path)

