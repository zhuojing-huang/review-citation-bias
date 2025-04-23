import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# citation years from peer reviews
files = [
    'extracted_EMNLP2023_llama70b_all.csv', 
    'extracted_ICLR2023_llama70b_all.csv', 
    'extracted_NeurIPS2023_llama70b_all.csv', 
    'extracted_NeurIPS2024_llama70b_all.csv'
]

venues = ["EMNLP2023", "ICLR2023", "NeurIPS2023", "NeurIPS2024"]
venue_years = {v: int(''.join(filter(str.isdigit, v))) for v in venues}

actual_years = {}
citation_ages = {}

file_to_venue = dict(zip(files, venues))

for file in files:
    venue = file_to_venue[file]
    venue_data = pd.read_csv(file)
    suggested_years = venue_data['suggested_years'].dropna().apply(lambda x: [int(i.strip()) for i in x.split(',')])
    all_suggested_years = [year for sublist in suggested_years for year in sublist]
    actual_years[venue] = all_suggested_years
    citation_ages[venue] = [venue_years[venue] - year for year in all_suggested_years]

avg_actual_years = {venue: np.mean(years) for venue, years in actual_years.items()}
median_actual_years = {venue: np.median(years) for venue, years in actual_years.items()}
avg_citation_age = {venue: np.mean(ages) for venue, ages in citation_ages.items()}
median_citation_age = {venue: np.median(ages) for venue, ages in citation_ages.items()}

# citation years from submitted papers
file_names = [
    'EMNLP2023_citation_analysis_results.csv', 
    'ICLR2023_citation_analysis_results.csv', 
    'NeurIPS2023_citation_analysis_results.csv', 
    'NeurIPS2024_citation_analysis_results.csv'
]

venue_name_year = []
avg_citing_years, med_citing_years = [], []
avg_citing_ages, med_citing_ages = [], []

for file in file_names:
    df = pd.read_csv(file)
    venue_year = int(''.join(filter(str.isdigit, file)))
    venue_name = file.split('_')[0]
    venue_name_year.append(venue_name)
    
    last_column = df.iloc[:, -1]
    avg_citing_years.append(last_column.mean())
    med_citing_years.append(last_column.median())

    df['extracted_years'] = df['extracted_years'].apply(lambda x: list(map(int, x.split(','))))
    df['citation_age'] = df['extracted_years'].apply(lambda years: [venue_year - year for year in years])
    df['citation_age_average'] = df['citation_age'].apply(lambda x: sum(x) / len(x) if len(x) > 0 else 0)
    df['citation_age_median'] = df['citation_age'].apply(lambda x: pd.Series(x).median())
    avg_citing_ages.append(df['citation_age_average'].mean())
    med_citing_ages.append(df['citation_age_median'].mean())

# Combined plots
fig, ax1 = plt.subplots(figsize=(12, 7))

x = np.arange(len(venues))
bar_width = 0.35

# Bars for actual years of suggested citations from peer reviews (left y-axis)
ax1.bar(x - bar_width/2, list(avg_actual_years.values()), bar_width, label='Average Suggested Year', color='skyblue')
ax1.bar(x + bar_width/2, list(median_actual_years.values()), bar_width, label='Median Suggested Year', color='steelblue')

# Bars for actual years of citations in submitted papers (left y-axis)
ax1.bar(x - bar_width/2, avg_citing_years, bar_width, color='skyblue', edgecolor='red', linestyle='solid', label='Average Citation Year')
ax1.bar(x + bar_width/2, med_citing_years, bar_width, color='steelblue', edgecolor='red',linestyle='solid', label='Median Citation Year')

ax1.set_xlabel('Venue')
ax1.set_ylabel('Year')
ax1.set_xticks(x)
ax1.set_xticklabels(venues)
ax1.set_ylim(2000, 2030)


# Add text labels
for i, (avg1, med1, avg2, med2) in enumerate(zip(avg_actual_years.values(), median_actual_years.values(), avg_citing_years, med_citing_years)):
    ax1.text(i - bar_width/2, avg1 + 1, f'{avg1:.1f}', ha='center', color='black')
    ax1.text(i + bar_width/2, med1 + 1, f'{med1:.1f}', ha='center', color='black')
    ax1.text(i - bar_width/2, avg2 + 1, f'{avg2:.1f}', ha='center', color='black', fontsize=9)
    ax1.text(i + bar_width/2, med2 + 1, f'{med2:.1f}', ha='center', color='black', fontsize=9)

# Second y-axis for citation ages from both papers and reviews
ax2 = ax1.twinx()
ax2.plot(venues, list(avg_citation_age.values()), marker='o', linestyle='-', color='red', label='Average Suggested Age')
ax2.plot(venues, list(median_citation_age.values()), marker='x', linestyle='--', color='red', label='Median Suggested Age')
ax2.plot(venues, avg_citing_ages, marker='o', linestyle='-', color='blue', label='Average Citation Age')
ax2.plot(venues, med_citing_ages, marker='x', linestyle='--', color='blue', label='Median Citation Age')

ax2.set_ylabel('Citation Age')
ax2.tick_params(axis='y')
ax2.set_ylim(0, 13)

# Add annotation for line charts
for i, (avg1, med1, avg2, med2) in enumerate(zip(avg_citation_age.values(), median_citation_age.values(), avg_citing_ages, med_citing_ages)):
    ax2.text(i, avg1 - 0.4, f'{avg1:.1f}', ha='center', color='red')
    ax2.text(i, med1 + 0.1, f'{med1:.1f}', ha='center', color='red')
    ax2.text(i, avg2 + 0.1, f'{avg2:.1f}', ha='center', color='blue')
    ax2.text(i, med2 + 0.1, f'{med2:.1f}', ha='center', color='blue')

# Legends
ax1.legend(loc='upper left',fontsize=10)
ax2.legend(loc='upper right',fontsize=10)

plt.title('Ages of Cited Papers vs. Ages of Suggested Papers')
plt.tight_layout()
plt.show()
