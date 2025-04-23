import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# files containing extracted years from reviews
files = [
    'processed_filtered_EMNLP2023_llama70b_all.csv', 
    'processed_filtered_ICLR2023_llama70b_all.csv', 
    'processed_filtered_NeurIPS2023_llama70b_all.csv', 
    'processed_filtered_NeurIPS2024_llama70b_all.csv'
]

# set venue names and corresponding years
venues = ["EMNLP2023", "ICLR2023", "NeurIPS2023", "NeurIPS2024"]
venue_years = {
    "EMNLP2023": 2023,
    "ICLR2023": 2023,
    "NeurIPS2023": 2023,
    "NeurIPS2024": 2024
}

actual_years = {}
citation_ages = {}
file_to_venue = {
    'processed_filtered_EMNLP2023_llama70b_all.csv': "EMNLP2023",
    'processed_filtered_ICLR2023_llama70b_all.csv': "ICLR2023",
    'processed_filtered_NeurIPS2023_llama70b_all.csv': "NeurIPS2023",
    'processed_filtered_NeurIPS2024_llama70b_all.csv': "NeurIPS2024"
}

for file in files:
    venue = file_to_venue[file]  # Get venue name based on the file
    venue_data = pd.read_csv(file)
    
    # "suggested years" column and split by commas
    suggested_years = venue_data['suggested_years'].dropna().apply(lambda x: [int(i.strip()) for i in x.split(',')])
    
    # Flatten the list of suggested years and store them in actual_years
    all_suggested_years = [year for sublist in suggested_years for year in sublist]
    actual_years[venue] = all_suggested_years
    
    # Calculate citation ages by subtracting the venue year
    citation_age = [venue_years[venue] - year for year in all_suggested_years]
    citation_ages[venue] = citation_age

# calculate the average and median of the actual years and citation ages
avg_actual_years = {venue: np.mean(years) for venue, years in actual_years.items()}
median_actual_years = {venue: np.median(years) for venue, years in actual_years.items()}

avg_citation_age = {venue: np.mean(ages) for venue, ages in citation_ages.items()}
median_citation_age = {venue: np.median(ages) for venue, ages in citation_ages.items()}

# plotting the results in a single graph with two y-axes
fig, ax1 = plt.subplots(figsize=(10, 6))
bar_width = 0.35
venues_list = list(actual_years.keys())
x = np.arange(len(venues_list))

# actual years (avg. and median) on the left y-axis
bars_avg = ax1.bar([pos - bar_width/2 for pos in x], list(avg_actual_years.values()), bar_width, label='Average Suggested Year', color='skyblue')
bars_median = ax1.bar([pos + bar_width/2 for pos in x], list(median_actual_years.values()), bar_width, label='Median Suggested Year', color='orange')

# annotate exact values on top of the bars
for i, (avg, med) in enumerate(zip(list(avg_actual_years.values()), list(median_actual_years.values()))):
    ax1.text(i - bar_width/2, avg + 1, f'{avg:.1f}', ha='center', color='black')
    ax1.text(i + bar_width/2, med + 1, f'{med:.1f}', ha='center', color='black')

# labels and title for the left y-axis
ax1.set_xlabel('Venue')
ax1.set_ylabel('Year')
ax1.set_title('Citation Years & Citation Ages from Reviews')
ax1.set_xticks(x)
ax1.set_xticklabels(venues_list)
ax1.set_ylim(2000, 2025)  # Set range for left y-axis
ax1.legend(loc='upper left')

# second y-axis for citation age (avg. and median)
ax2 = ax1.twinx()
ax2.set_ylim(0, 10)

# line charts for citation ages (avg. and med.) on the right y-axis
line_avg = ax2.plot(venues_list, list(avg_citation_age.values()), marker='o', linestyle='-', color='red', label='Average Citation Age')
line_median = ax2.plot(venues_list, list(median_citation_age.values()), marker='s', linestyle='--', color='red', label='Median Citation Age')

# labels for the right y-axis
ax2.set_ylabel('Citation Age', color='red')
ax2.tick_params(axis='y', labelcolor='red')

# annotate exact values for the lines
for i, (avg, med) in enumerate(zip(list(avg_citation_age.values()), list(median_citation_age.values()))):
    ax2.text(i, avg + 0.1, f'{avg:.1f}', ha='center', color='red')
    ax2.text(i, med + 0.1, f'{med:.1f}', ha='center', color='red')

ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.tight_layout()
plt.show()