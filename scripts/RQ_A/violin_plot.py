import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# files
file_names = [
    'EMNLP2023_citation_analysis_results.csv', 
    'ICLR2023_citation_analysis_results.csv', 
    'NeurIPS2023_citation_analysis_results.csv', 
    'NeurIPS2024_citation_analysis_results.csv'
]

# initialize a list to store the data for each file
year_data = []

# loop through each file
for file in file_names:
    df = pd.read_csv(file)

    # extract the "extracted_years" column 
    extracted_years = df['extracted_years']

    # list to hold the integer years
    all_years = []

    # loop through each entry in the "extracted_years" column
    for years_string in extracted_years:
        # split the string by commas and convert each value to an integer
        years_list = map(int, years_string.split(', '))
        # append the years to the all_years list
        all_years.extend(years_list)
    
    # add the processed data to the list
    year_data.append(all_years)

# create a combined list of years with corresponding file labels
combined_data = []
labels = []

for file, data in zip(file_names, year_data):
    combined_data.extend(data)
    labels.extend([file.split('_')[0]] * len(data))

# create a DataFrame for plotting
df = pd.DataFrame({'Year': combined_data, 'Dataset': labels})

# Violin Plot
plt.figure(figsize=(10, 6))
sns.violinplot(x='Dataset', y='Year', data=df)
plt.title('Violin Plot for Citation Years')
plt.ylabel('Year')
plt.show()