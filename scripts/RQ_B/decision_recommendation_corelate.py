import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind, chi2_contingency

# load csv to df (choose df2 as needed)
df1 = pd.read_csv("cleaned_ICLR2023_with_decision_dense.csv")  # first CSV with 'decision' column -- Accept/Reject csv
df2 = pd.read_csv("ICLR2023_llama70b_rec_num.csv")  # second CSV with 'number of reviewers recommending' column
# df2 = pd.read_csv("ICLR2023_llama70b_with_rec_num_binary.csv")  # second CSV with 'number of reviewers recommending' column -- binary version/whether or not the paper got recommended extra literature

# merge the two df on the 'invitations' (ID) column
merged_df = pd.merge(df1, df2, left_on='invitations', right_on='invitation', how='inner')

# remove nan values from 'decision' and categorize decisions
merged_df = merged_df.dropna(subset=['decision'])
merged_df['decision'] = merged_df['decision'].astype(str).apply(lambda x: 'accept' if 'accept' in x.lower() else x)

# ensure 'number of reviewers recommending' is numeric
merged_df['number of reviewers recommending'] = pd.to_numeric(merged_df['number of reviewers recommending'], errors='coerce')
merged_df = merged_df.dropna(subset=['number of reviewers recommending'])

# group the data by 'number of reviewers recommending' and 'decision'
grouped = merged_df.groupby(['number of reviewers recommending', 'decision']).size().reset_index(name='count')

# normalize the counts within each 'decision' category
total_counts = grouped.groupby('decision')['count'].transform('sum')
grouped['proportion'] = grouped['count'] / total_counts

# bar plot
plt.figure(figsize=(10, 6))
ax = sns.barplot(x='number of reviewers recommending', y='proportion', hue='decision', data=grouped)

plt.xlabel('Did the Paper Receive Suggestion for Citing Another Paper')
plt.ylabel('Proportion')
plt.title('Distribution of Acceptance and Paper Recommendation')
plt.legend(title='Decision')
#plt.xticks([0, 1], ["No", "Yes"], rotation=45)  # use when the tags are binary
plt.xticks(rotation=45)

# add n= labels on each bar using grouped['count']
for bar in ax.patches:
    height = bar.get_height()
    x = bar.get_x() + bar.get_width() / 2

    # get corresponding x and hue value from bar
    bar_label = bar.get_label() if hasattr(bar, 'get_label') else ''
    bar_decision = bar.get_facecolor()  # this is not useful here, so we avoid it

    # get x (number of reviewers recommending) and hue (decision)
    x_val = round(bar.get_x() + bar.get_width() / 2)
    for _, row in grouped.iterrows():
        if abs(row['number of reviewers recommending'] - x_val) < 0.1 and abs(row['proportion'] - height) < 0.01:
            count = row['count']
            ax.text(x, height + 0.01, f'n={count}', ha='center', va='bottom', fontsize=8)
            break

plt.tight_layout()
plt.show()

# binary column: 1 for 'accept', 0 for anything else
merged_df['is_accepted'] = merged_df['decision'].apply(lambda x: 1 if 'accept' in x.lower() else 0)
group_yes = merged_df[merged_df['number of reviewers recommending'] == 1]['is_accepted']
group_no = merged_df[merged_df['number of reviewers recommending'] == 0]['is_accepted']

# chi-square test for independence and statistic significance
contingency = pd.crosstab(merged_df['number of reviewers recommending'], merged_df['is_accepted'])
chi2, chi_p, dof, expected = chi2_contingency(contingency)
print("=== Chi-square Test ===")
print("Contingency Table:")
print(contingency)
print(f"\nChi-square statistic: {chi2:.4f}")
print(f"P-value: {chi_p:.4f}")
