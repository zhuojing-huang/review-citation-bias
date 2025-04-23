import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# suggested years
suggested_files = [
    'extracted_EMNLP2023_llama70b_all.csv', 
    'extracted_ICLR2023_llama70b_all.csv', 
    'extracted_NeurIPS2023_llama70b_all.csv', 
    'extracted_NeurIPS2024_llama70b_all.csv'
]

# citation years
citation_files = [
    'EMNLP2023_citation_analysis_results.csv', 
    'ICLR2023_citation_analysis_results.csv', 
    'NeurIPS2023_citation_analysis_results.csv', 
    'NeurIPS2024_citation_analysis_results.csv'
]

# process files and extract years
def extract_years(file_list, year_column, label):
    data = []
    for file in file_list:
        df = pd.read_csv(file)
        extracted_years = df[year_column].dropna()  # Drop NaN values
        all_years = []
        for years_string in extracted_years:
            years_list = map(int, years_string.split(', '))
            all_years.extend(years_list)
        venue = file.split('_')[1] if "extracted" in file else file.split('_')[0]  # Extract venue name
        data.extend([(year, venue, label) for year in all_years])
    return data

suggested_data = extract_years(suggested_files, 'suggested_years', 'Suggested Year')
citation_data = extract_years(citation_files, 'extracted_years', 'Citation Year')

# combine df
df = pd.DataFrame(suggested_data + citation_data, columns=['Year', 'Venue', 'Type'])
palette = {'Suggested Year': 'steelblue', 'Citation Year': 'skyblue'}

# combined violin plot
plt.figure(figsize=(12, 6))
sns.violinplot(x='Venue', y='Year', hue='Type', data=df, split=True, palette=palette, hue_order=['Citation Year', 'Suggested Year']) # left violin for citation years, right violin for suggested years
plt.title('Distribution of Suggested vs Citation Years')
plt.ylabel('Year')
plt.legend(loc='lower center', title=None)
plt.show()
