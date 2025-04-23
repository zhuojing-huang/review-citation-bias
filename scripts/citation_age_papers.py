import pandas as pd
import matplotlib.pyplot as plt

# csv files containing all the years of cited papers
file_names = [
    'EMNLP2023_citation_analysis_results.csv', 
    'ICLR2023_citation_analysis_results.csv', 
    'NeurIPS2023_citation_analysis_results.csv', 
    'NeurIPS2024_citation_analysis_results.csv'
]

venue_years = []
venue_name_year = []
avg_citing_years = []
med_citing_years = []
avg_citing_ages = []
med_citing_ages = []

for file in file_names:
    df = pd.read_csv(file)
    
    # extract venue year from the name
    venue_year = int(''.join(filter(str.isdigit, file)))
    venue_years.append(venue_year)

    venue_name = file.split('_')[0]  # Extract part before the first underscore
    venue_name_year.append(venue_name)  # Store it instead of the year

    
    # compute average and median citing year (last column dynamically)
    last_column = df.iloc[:, -1]
    avg_citing_year = last_column.mean()
    med_citing_year = last_column.median()
    avg_citing_years.append(avg_citing_year)
    med_citing_years.append(med_citing_year)
    
    # compute citation age
    df['extracted_years'] = df['extracted_years'].apply(lambda x: list(map(int, x.split(','))))
    df['citation_age'] = df['extracted_years'].apply(lambda years: [venue_year - year for year in years])
    df['citation_age_average'] = df['citation_age'].apply(lambda x: sum(x) / len(x) if len(x) > 0 else 0)
    df['citation_age_median'] = df['citation_age'].apply(lambda x: pd.Series(x).median())
    avg_citing_age = df['citation_age_average'].mean()
    med_citing_age = df['citation_age_median'].mean()
    avg_citing_ages.append(avg_citing_age)
    med_citing_ages.append(med_citing_age)

fig, ax1 = plt.subplots(figsize=(10, 6))

x_indexes = range(len(venue_years))
width = 0.3  

# average and median citing year on 1st y-axis as bars
ax1.bar([x - width/2 for x in x_indexes], avg_citing_years, width=width, color='skyblue', label='Avg. Citation Year')
ax1.bar([x + width/2 for x in x_indexes], med_citing_years, width=width, color='blue', label='Median Citation Year')
ax1.set_xlabel('Venue (Year)')
ax1.set_ylabel('Year', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.set_xticks(x_indexes)
ax1.set_xticklabels(venue_name_year)  
ax1.set_ylim(2000, 2025)

# add bars with values
for i, (avg, med) in enumerate(zip(avg_citing_years, med_citing_years)):
    ax1.text(i - width/2, avg + 1, f'{avg:.1f}', ha='center', color='black')
    ax1.text(i + width/2, med + 1, f'{med:.1f}', ha='center', color='black')

# 2nd y-axis for average and median citing age as lines
ax2 = ax1.twinx()
ax2.plot(x_indexes, avg_citing_ages, marker='o', linestyle='-', color='red', label='Avg. Citation Age')
ax2.plot(x_indexes, med_citing_ages, marker='s', linestyle='--', color='red', label='Median Citation Age')
ax2.set_ylabel('Citation Age', color='red')
ax2.tick_params(axis='y', labelcolor='red')

# add line points with values
for i, (avg, med) in enumerate(zip(avg_citing_ages, med_citing_ages)):
    ax2.text(i, avg + 0.1, f'{avg:.1f}', ha='center', color='red')
    ax2.text(i, med + 0.1, f'{med:.1f}', ha='center', color='red')

ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.title('Citation Years & Citation Ages')
fig.tight_layout()
plt.show()
