import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import seaborn as sns

def plot_bar_graph(csv_file):
    #read the csv file
    data = pd.read_csv(csv_file)

    # count how many times each answer occurs
    counts = data['Score'].value_counts().reset_index()
    counts.columns = ['Score', 'Count']

    # set the seaborn style
    sns.set(style="whitegrid")

    # create the bar plot
    plt.figure(figsize=(10,6), tight_layout=True)
    ax = sns.barplot(x='Score', y='Count', data=counts, palette="deep")
    
    # add labels to each bar
    for p in ax.patches:
        x = p.get_x() + p.get_width() / 2
        y = p.get_height()
        ax.annotate(str(int(y)), (x, y), ha='center', va='bottom', fontsize=17)


    #plot the graph
    plt.xlabel('Score', fontsize=17)
    plt.ylabel('Count', fontsize=17)
    plt.xticks(fontsize=17)
    plt.yticks(fontsize=17)
    #plt.title('Count of Answers')
    #plt.show()

    
    #save the plot in the same directory as the csv file
    file_dir = os.path.dirname(csv_file)
    output_file = os.path.join(file_dir, 'bar_graph.png')
    plt.savefig(output_file)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_csv_file>")
        sys.exit(1)

    csv_file = sys.argv[1]
    plot_bar_graph(csv_file)
