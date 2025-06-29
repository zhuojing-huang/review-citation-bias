import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import numpy as np 

# load csv
csv1 = pd.read_csv("NeurIPS2024_submissions.csv")
csv2 = pd.read_csv("NeurIPS2024_recommended_topics.csv")

# Extract relevant columns
col1 = csv1['primary_area']
col2 = csv2['topic 1 ']

# Compute normalized value counts (frequencies)
freq1 = col1.value_counts(normalize=True)
freq2 = col2.value_counts(normalize=True)

# Get Top 15 categories from each
top10_freq1 = freq1.head(15)
top10_freq2 = freq2.head(15)

def simplify_label(label):
    # Remove text in parentheses
    label = re.sub(r"\s*\(.*?\)", "", label)
    # Strip leading/trailing spaces and collapse any redundant spaces
    label = re.sub(r"\s+", " ", label.strip())
    return label


# Simplify x-axis labels
top10_freq1.index = [simplify_label(label) for label in top10_freq1.index]
top10_freq2.index = [simplify_label(label) for label in top10_freq2.index]

# Plot 1: Top 15 categories in csv1
plt.figure(figsize=(10, 5))
sns.barplot(x=top10_freq1.index, y=top10_freq1.values, color='skyblue')
plt.title('Top 15 Topics - Submitted Papers for NeurIPS2024')
plt.ylabel('Frequency')
plt.xlabel('Category')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
#plt.show()

# Plot 2: Top 15 categories in csv2
plt.figure(figsize=(10, 5))
sns.barplot(x=top10_freq2.index, y=top10_freq2.values, color='skyblue')
plt.title('Top 15 Topics - Recommended Papers for NeurIPS2024')
plt.ylabel('Frequency')
plt.xlabel('Category')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
#plt.show()

# Step 1: Simplify and aggregate frequency Series
freq1_simplified = freq1.groupby(freq1.index.map(simplify_label)).sum()
freq2_simplified = freq2.groupby(freq2.index.map(simplify_label)).sum()

# Step 2: Get top categories from each (after simplification)
top10_labels1 = freq1_simplified.nlargest(10).index
top10_labels2 = freq2_simplified.nlargest(10).index

# Step 3: Union of top categories
top_categories = set(top10_labels1).union(set(top10_labels2))

# Step 4: Create aligned DataFrame
combined_df = pd.DataFrame({
    'CSV1': freq1_simplified.reindex(top_categories).fillna(0),
    'CSV2': freq2_simplified.reindex(top_categories).fillna(0)
}).reset_index().rename(columns={'index': 'Category'})

# Step 5: Melt for seaborn plotting
melted = combined_df.melt(id_vars='Category', var_name='Source', value_name='Frequency')

# Step 6: Plotting
topics = combined_df['Category']
values1 = combined_df['CSV1'].values
values2 = combined_df['CSV2'].values
x = np.arange(len(topics))
width = 0.35

# Multiply frequencies by 100 to get percentages
values1 = combined_df['CSV1'].values * 100
values2 = combined_df['CSV2'].values * 100

plt.figure(figsize=(12, 6))
bars1 = plt.bar(x - width/2, values1, width, label='Submitted Papers', color='steelblue')
bars2 = plt.bar(x + width/2, values2, width, label='Recommended Papers', color='orange')

# Add percentage labels on top of each bar
for bar in bars1:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height, f'{height:.1f}%', ha='center', va='bottom', fontsize=8)

for bar in bars2:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height, f'{height:.1f}%', ha='center', va='bottom', fontsize=8)

plt.xticks(x, topics, rotation=45, ha='right')
plt.ylabel('Percentage (%)')
plt.title('Topic Comparison for Submitted and Recommended Papers in NeurIPS2024')
plt.legend()
plt.tight_layout()
plt.show()

