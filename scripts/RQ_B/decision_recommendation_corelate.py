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
#plt.xticks([0, 1], ["No", "Yes"], rotation=45)
plt.xticks(rotation=45)

# Add n= labels on each bar using grouped['count']
for bar in ax.patches:
    height = bar.get_height()
    x = bar.get_x() + bar.get_width() / 2

    # Get corresponding x and hue value from bar
    bar_label = bar.get_label() if hasattr(bar, 'get_label') else ''
    bar_decision = bar.get_facecolor()  # this is not useful here, so we avoid it

    # Get x (number of reviewers recommending) and hue (decision)
    x_val = round(bar.get_x() + bar.get_width() / 2)
    for _, row in grouped.iterrows():
        if abs(row['number of reviewers recommending'] - x_val) < 0.1 and abs(row['proportion'] - height) < 0.01:
            count = row['count']
            ax.text(x, height + 0.01, f'n={count}', ha='center', va='bottom', fontsize=8)
            break

plt.tight_layout()
plt.show()


# Step 7: Confusion Matrix (Row-wise Percentage)
# Create a confusion matrix comparing 'decision' and 'number of reviewers recommending'
decision_labels = merged_df['decision'].unique()
reviewer_counts = merged_df['number of reviewers recommending'].unique()

# Convert categorical values to indices
decision_mapping = {label: idx for idx, label in enumerate(decision_labels)}
reviewer_mapping = {count: idx for idx, count in enumerate(reviewer_counts)}

merged_df['decision_idx'] = merged_df['decision'].map(decision_mapping)
merged_df['reviewer_idx'] = merged_df['number of reviewers recommending'].map(reviewer_mapping)

# Compute confusion matrix
cm = confusion_matrix(merged_df['decision_idx'], merged_df['reviewer_idx'])

# Normalize row-wise (within each decision category)
cm_percent = cm.astype('float') / cm.sum(axis=1, keepdims=True) * 100

# Plot heatmap
plt.figure(figsize=(10, 6))
sns.heatmap(cm_percent, annot=True, fmt='.2f', xticklabels=reviewer_counts, yticklabels=decision_labels, cmap='Blues')
plt.xlabel('Number of Reviewers Recommending')
plt.ylabel('Decision Category')
plt.title('Decisions vs. Reviewer Recommendations')
plt.show()


# Step 7: Confusion Matrix (Column-wise Percentage)
# Create a confusion matrix comparing 'decision' and 'number of reviewers recommending'
decision_labels = merged_df['decision'].unique()
reviewer_counts = merged_df['number of reviewers recommending'].unique()

# Convert categorical values to indices
decision_mapping = {label: idx for idx, label in enumerate(decision_labels)}
reviewer_mapping = {count: idx for idx, count in enumerate(reviewer_counts)}

merged_df['decision_idx'] = merged_df['decision'].map(decision_mapping)
merged_df['reviewer_idx'] = merged_df['number of reviewers recommending'].map(reviewer_mapping)

# Compute confusion matrix
cm = confusion_matrix(merged_df['decision_idx'], merged_df['reviewer_idx'])

# Normalize column-wise (within each reviewer recommendation count)
cm_percent = cm.astype('float') / cm.sum(axis=0, keepdims=True) * 100

# Plot heatmap
plt.figure(figsize=(10, 6))
sns.heatmap(cm_percent, annot=True, fmt='.2f', xticklabels=reviewer_counts, yticklabels=decision_labels, cmap='Greens')
plt.xlabel('Number of Reviewers Recommending')
plt.ylabel('Decision Category')
plt.title('Decisions vs. Reviewer Recommendations (Column-wise %)')
plt.show()



# Create binary column: 1 for 'accept', 0 for anything else
merged_df['is_accepted'] = merged_df['decision'].apply(lambda x: 1 if 'accept' in x.lower() else 0)

# Split into two groups based on recommendation
group_yes = merged_df[merged_df['number of reviewers recommending'] == 1]['is_accepted']
group_no = merged_df[merged_df['number of reviewers recommending'] == 0]['is_accepted']

# Perform independent t-test
t_stat, p_val = ttest_ind(group_yes, group_no, equal_var=False)
print("=== Independent t-test ===")
print(f"T-statistic: {t_stat:.4f}")
print(f"P-value: {p_val:.4f}")
print()

# Chi-square test for independence
contingency = pd.crosstab(merged_df['number of reviewers recommending'], merged_df['is_accepted'])
chi2, chi_p, dof, expected = chi2_contingency(contingency)
print("=== Chi-square Test ===")
print("Contingency Table:")
print(contingency)
print(f"\nChi-square statistic: {chi2:.4f}")
print(f"P-value: {chi_p:.4f}")
