import numpy as np
import matplotlib.pyplot as plt

# 1. Your four vote-lists:
data_sets = {
    'Goals':               [2, 9, 2, 2,11, 4,   0, 5, 1, 2, 2, 2,   2, 5, 2,1,0,0,   1,4,5,0,4,0],
    'Progress':            [2, 6, 8, 2, 7, 5,   0, 5, 1, 0, 4, 2,   1, 5, 2,2,0,0,   0,10,1,0,3,0],
    'Missing Elements':    [5, 2, 4, 6, 6, 7,   1, 4, 0, 2, 3, 2,   2, 5, 1,1,1,0,   2,6,1,1,4,0],
    'Next Steps':          [1, 6, 5, 2, 9, 7,   1, 5, 2, 0, 2, 2,   2, 4, 1,1,2,0,   3,7,2,0,2,0],
}

periods = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
choices = [
    'Significant',   # #4575b4
    'Somewhat',      # #91bfdb
    'No effect',     # #e0f3f8
    'Insufficient',  # #fee090
    'No information',# #fc8d59
    'Not applicable' # #d73027
]
hatches = ['/', '\\', '|', '-', '+', 'x']

n_periods = len(periods)
n_choices = len(choices)
bar_width = 0.8 / n_choices
x = np.arange(n_periods)

# 2. Use your custom hex colors in the exact order of `choices`
colors = [
    '#4575b4',  # Significant
    '#91bfdb',  # Somewhat
    '#e0f3f8',  # No effect
    '#fee090',  # Insufficient
    '#fc8d59',  # No information
    '#d73027'   # Not applicable
]

# 3. Loop over each dataset and plot
for title, votes in data_sets.items():
    arr = np.array(votes).reshape(n_periods, n_choices)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for i in range(n_choices):
        ax.bar(
            x + i*bar_width,
            arr[:, i],
            bar_width,
            label=choices[i],
            color=colors[i],
            edgecolor='black',
            hatch=hatches[i]
        )
    
    # center x-ticks under each group:
    ax.set_xticks(x + (n_choices-1)*bar_width/2)
    ax.set_xticklabels(periods, fontsize=18)
    
    ax.set_xlabel('Period', fontsize=18)
    ax.set_ylabel('Votes', fontsize=18)
    ax.tick_params(axis='y', labelsize=18)
    
    ax.legend(title='Choice', fontsize=18, title_fontsize=18, loc='upper center')
    plt.tight_layout()

    filename = title.lower().replace(' ', '_') + '_distribution.png'
    fig.savefig(filename, dpi=300, bbox_inches='tight')
    print(f'Saved figure: {filename}') 
    plt.show()
