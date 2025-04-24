import pandas as pd
import ast
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter

# cited papers
files = {
    "ICLR2013": "ICLR2013_submissions_reference_fos.csv",
    "ICLR2014": "ICLR2014_submissions_reference_fos.csv",
    "ICLR2017": "ICLR2017_submissions_reference_fos.csv",
    "ICLR2019": "ICLR2019_submissions_reference_fos.csv",
    "ICLR2023": "ICLR2023_submissions_reference_fos.csv"
}
'''
# recommended papers
files = {
    "ICLR2013": "iclr2013_suggested_titles_annotated_150_output.csv",
    "ICLR2014": "iclr2014_suggested_titles_annotated_150_output.csv",
    "ICLR2017": "iclr2017_suggested_titles_annotated_300_output.csv",
    "ICLR2019": "iclr2019_suggested_titles_annotated_400_output.csv",
    "ICLR2023": "ICLR2023_suggested_citation_400_output.csv"
    # Add more as needed
}
'''

def extract_fields_of_study(paper_details):
    try:
        details = ast.literal_eval(paper_details)
        return details.get("fieldsOfStudy", []) if details else []
    except (SyntaxError, ValueError):
        return []

# First pass: gather all fields to find top 3
global_field_counter = Counter()

dataset_field_data = {}

for label, file_path in files.items():
    df = pd.read_csv(file_path)
    df["fieldsOfStudyList"] = df["paper_details"].apply(extract_fields_of_study)
    all_fields = [field for fields in df["fieldsOfStudyList"] if fields is not None for field in fields]
    field_counts = Counter(all_fields)
    
    global_field_counter.update(field_counts)
    dataset_field_data[label] = field_counts

# Get top 3 fields globally
top_fields = [field for field, _ in global_field_counter.most_common(3)]
print("Top 3 fields:", top_fields)

# comparison data
comparison_results = []

for dataset, field_counts in dataset_field_data.items():
    total = sum(field_counts.values())
    for field in top_fields:
        count = field_counts.get(field, 0)
        percentage = (count / total * 100) if total > 0 else 0
        comparison_results.append({
            "Dataset": dataset,
            "Field": field,
            "Percentage": percentage
        })

comparison_df = pd.DataFrame(comparison_results)

# first plot: top three fields cross the years 
plt.figure(figsize=(10, 6))
sns.barplot(data=comparison_df, x="Dataset", y="Percentage", hue="Field", palette="Set2")

# horizontal dashed lines for min and max percentage
max_val = comparison_df["Percentage"].max()
min_val = comparison_df["Percentage"].min()
plt.axhline(max_val, linestyle="--", color="gray")
plt.text(len(files) - 0.5, max_val + 1, f"{max_val:.1f}%", color="gray")

plt.axhline(min_val, linestyle="--", color="gray")
plt.text(len(files) - 0.5, min_val + 1, f"{min_val:.1f}%", color="gray")


plt.ylabel("Percentage of Papers (%)")
plt.title("Top 3 Fields of Study Across ICLR Datasets")
plt.ylim(0, 100)
plt.legend(title="Field", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()


# second plot: cs vs non cs percentage
results = []

for label, file_path in files.items():
    df = pd.read_csv(file_path)
    df["fieldsOfStudyList"] = df["paper_details"].apply(extract_fields_of_study)
    all_fields = [field for fields in df["fieldsOfStudyList"] if fields is not None for field in fields]
    field_counts = Counter(all_fields)
    
    cs_count = field_counts.get("Computer Science", 0)
    non_cs_count = sum(count for field, count in field_counts.items() if field != "Computer Science")
    total = cs_count + non_cs_count

    results.append({"Dataset": label, "Category": "Computer Science", "Count": cs_count, "Percentage": cs_count / total * 100})
    results.append({"Dataset": label, "Category": "Non-Computer Science", "Count": non_cs_count, "Percentage": non_cs_count / total * 100})

comparison_df = pd.DataFrame(results)

plt.figure(figsize=(10, 6))
sns.barplot(data=comparison_df, x="Dataset", y="Percentage", hue="Category", palette="coolwarm")

# horizontal dashed lines for min and max percentage
max_val = comparison_df["Percentage"].max()
min_val = comparison_df["Percentage"].min()
plt.axhline(max_val, linestyle="--", color="gray")
plt.text(len(files) - 0.5, max_val + 1, f"{max_val:.1f}%", color="gray")

plt.axhline(min_val, linestyle="--", color="gray")
plt.text(len(files) - 0.5, min_val + 1, f"{min_val:.1f}%", color="gray")


plt.ylabel("Percentage of Papers (%)")
plt.title("Computer Science vs Non-Computer Science Across Datasets")
plt.ylim(0, 100)
plt.legend(title="Field Category", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
