import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.gridspec as gridspec


def draw_and_save_bar_plot(df, column, title, ax, round_values=False):
    if round_values:
       df[column] = df[column].round(2)
    counts = df[column].value_counts().sort_index()
    counts.plot(kind='bar', edgecolor='black', ax=ax)
    ax.set_title(title, fontsize=14)
    ax.set_xlabel('Correctness Level', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.tick_params(axis='x', rotation=0)

    #add the values at the top of the bars
    for i, v in enumerate(counts):
        ax.text(i, v, str(v), ha='center', va='bottom', fontsize=10)
    #plt.savefig(filename)
    #plt.clf()
def absolute_value(val):
    #calculate the absolute value from a percentage
    total = df_8[['syntax', 'semantic', 'results']].sum().sum()
    absolute = int(round(val*total/100))
    return f'{val:.1f}%\n({absolute:d})'

def draw_and_save_3d_bubble_plot(df, columns, title, ax):
    # create a bubble size based on the frequency of each point
    bubble_size = df[columns].groupby(columns).size().reset_index(name='bubble_size')

    # scatter plot
    sc = ax.scatter(bubble_size[columns[0]], bubble_size[columns[1]], bubble_size[columns[2]], 
                    s=bubble_size['bubble_size']*10, alpha=0.6, edgecolors='w')

    # add the total number and the values of syntax, semantic, and results inside each bubble
    for i in range(len(bubble_size)):
        text = f"{bubble_size.loc[i, 'bubble_size']}\n({bubble_size.loc[i, columns[0]]}, {bubble_size.loc[i, columns[1]]}, {bubble_size.loc[i, columns[2]]})"
        ax.text(bubble_size.loc[i, columns[0]], bubble_size.loc[i, columns[1]], bubble_size.loc[i, columns[2]], text, color='black', ha='center', fontsize=10)

    ax.set_xlabel(columns[0].capitalize(), fontsize=12)
    ax.set_ylabel(columns[1].capitalize(), fontsize=12)
    ax.set_zlabel(columns[2].capitalize(), fontsize=12)
    ax.set_title(title, fontsize=14)


#load the csv files into dataframes
files_8 = ["db_quiz_1_question_9_graded_8.csv", "db_quiz_2_question_6_graded_8.csv", "db_quiz_2_question_7_graded_8.csv", "db_quiz_2_question_8_graded_8.csv", "db_quiz_2_question_9_graded_8.csv", "db_quiz_2_question_10_graded_8.csv"]
files_27 = ["db_quiz_1_question_9_graded_27.csv", "db_quiz_2_question_6_graded_27.csv", "db_quiz_2_question_7_graded_27.csv", "db_quiz_2_question_8_graded_27.csv", "db_quiz_2_question_9_graded_27.csv", "db_quiz_2_question_10_graded_27.csv"]
df_8 = pd.concat([pd.read_csv(f) for f in files_8]) 
df_27 = pd.concat([pd.read_csv(f) for f in files_27])  

#create a new column called 'correctness' based on the values in the 'syntax', 'semantic', and 'results' columns
df_8['correctness'] = df_8.apply(lambda row: 'correct' if row['syntax'] == 1 and row['semantic'] == 1 and row['results'] == 1 else 'incorrect', axis=1)
#create a new column called 'normalized' based on the values in the 'syntax', 'semantic', and 'results' columns
df_8['normalized'] = df_8.apply(lambda row: '1' if row['syntax'] == 1 and row['semantic'] == 1 and row['results'] == 1 else '0', axis=1)

# For 8 graded charts
#fig, axs = plt.subplots(2, 3, figsize=(15, 15))  # Create a figure with 3 rows and 2 columns of subplots
#fig.suptitle('Grading results')  # Set the main title for the figure# Create a figure
fig = plt.figure(figsize=(15, 15))

# Define the grid
gs = gridspec.GridSpec(2, 6)  # 2 rows, 6 columns

# Define the subplots
ax1 = fig.add_subplot(gs[0, 0:2])  # Top row, first 2 columns
ax2 = fig.add_subplot(gs[0, 2:4])  # Top row, next 2 columns
ax3 = fig.add_subplot(gs[0, 4:6])  # Top row, last 2 columns
ax4 = fig.add_subplot(gs[1, 0:3], projection='3d')  # Bottom row, first 3 columns
ax5 = fig.add_subplot(gs[1, 3:6], projection='3d')  # Bottom row, last 3 columns

#draw and save the bar plot
draw_and_save_bar_plot(df_8, 'correctness', 'Bar plot of correctness', ax1)
#draw_and_save_bar_plot(df_8, 'normalized', 'Bar plot of correctness (Normalized)', axs[1, 0])

#1. bar plot for 8 magnitude graded queries
draw_and_save_bar_plot(df_8, 'correctness level', 'Bar plot of 8 magnitude graded queries', ax2)
#2. bar plot for 27 magnitude graded queries
draw_and_save_bar_plot(df_27, 'correctness level', 'Bar plot of 27 magnitude graded queries', ax3)
#3. bar plot for 8 magnitude graded queries for normalized values
#draw_and_save_bar_plot(df_8, 'normalized value', 'Bar plot of 8 magnitude graded queries (Normalized).', axs[1, 1], round_values=True)
#4. bar plot for 27 magnitude graded queries for normalized values
#draw_and_save_bar_plot(df_27, 'normalized value', 'Bar plot of 27 magnitude graded queries (Normalized).', axs[1, 2], round_values=True)
#5 3d scatter plot for 8 magnitude graded queries showing syntax, semantic, and results groups
draw_and_save_3d_bubble_plot(df_8, ['syntax', 'semantic', 'results'], '3D scatter plot of syntax, semantics, and results (8 magnitude)', ax4)
#6 3d scatter plot for 27 magnitude graded queries showing syntax, semantic, and results groups
draw_and_save_3d_bubble_plot(df_27, ['syntax', 'semantic', 'results'], '3D scatter plot of syntax, semantics, and results (27 magnitude)', ax5)

# Save the figure with all subplots
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05, wspace=0.2, hspace=0.2)

plt.savefig('8_graded_charts.png')
plt.clf() 