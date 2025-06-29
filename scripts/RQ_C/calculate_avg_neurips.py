import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# change manually for different NeurIPS subsets
df = pd.read_csv("NeurIPS2024_accept_score.csv") 
categories = ["contribution", "presentation", "soundness", "rating"] # the numerical columns; the review scores

# Extract numerical scores and compute averages
for cat in categories:
    for i in range(1, 10):
        col = f"reviewer{i}_{cat}"
        if col in df.columns:
            df[col] = df[col].astype(str).str.extract(r"^(\d)").astype(float)
    cols = [f"reviewer{i}_{cat}" for i in range(1, 10) if f"reviewer{i}_{cat}" in df.columns]
    df[f"avg_{cat}"] = df[cols].mean(axis=1)

# round averaged years to nearest integer; aggregate consecutive years that have few data points 
def custom_round_year(year):
    if year < 2010.5:
        return "until 2010"
    elif 2022 <= year < 2024:
        return "2022"
    else:
        return str(int(np.ceil(year)))

df["rounded_year"] = df["average_year"].apply(custom_round_year)

# Bootstrapping
def bootstrap_ci(data, n_bootstrap=1000, ci=95):
    boot_means = [data.sample(frac=1, replace=True).mean() for _ in range(n_bootstrap)]
    lower = np.percentile(boot_means, (100 - ci) / 2)
    upper = np.percentile(boot_means, 100 - (100 - ci) / 2)
    return np.mean(boot_means), lower, upper

# Bootstrap and aggregate for plotting 
results = []
for year in sorted(df["rounded_year"].unique()):
    subset = df[df["rounded_year"] == year]
    row = {"year": year}
    for cat in ["avg_contribution", "avg_presentation", "avg_soundness"]:
        mean, lower, upper = bootstrap_ci(subset[cat].dropna())
        row[f"{cat}_mean"] = mean
        row[f"{cat}_lower"] = lower
        row[f"{cat}_upper"] = upper
    results.append(row)

boot_df = pd.DataFrame(results)
boot_df = boot_df.sort_values(by="year", key=lambda x: x.replace("until 2010", "0000"))

# Plotting average scores (contribution, presentation, soundness) 
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(boot_df["year"]))
width = 0.25

# Identify global min and max values and their positions
extreme_values = {}
for cat in ["avg_contribution", "avg_presentation", "avg_soundness"]:
    max_val = boot_df[f"{cat}_mean"].max()
    min_val = boot_df[f"{cat}_mean"].min()
    max_idx = boot_df[f"{cat}_mean"].idxmax()
    min_idx = boot_df[f"{cat}_mean"].idxmin()
    extreme_values[cat] = {
        "max": (boot_df.loc[max_idx, "year"], max_val, max_idx),
        "min": (boot_df.loc[min_idx, "year"], min_val, min_idx)
    }

# three bars per year with proper spacing
ax.bar(x - width, boot_df["avg_contribution_mean"], width,
       yerr=[boot_df["avg_contribution_mean"] - boot_df["avg_contribution_lower"],
             boot_df["avg_contribution_upper"] - boot_df["avg_contribution_mean"]],
       capsize=5, label="contribution", color="skyblue")

ax.bar(x, boot_df["avg_presentation_mean"], width,
       yerr=[boot_df["avg_presentation_mean"] - boot_df["avg_presentation_lower"],
             boot_df["avg_presentation_upper"] - boot_df["avg_presentation_mean"]],
       capsize=5, label="presentation", color="salmon")

ax.bar(x + width, boot_df["avg_soundness_mean"], width,
       yerr=[boot_df["avg_soundness_mean"] - boot_df["avg_soundness_lower"],
             boot_df["avg_soundness_upper"] - boot_df["avg_soundness_mean"]],
       capsize=5, label="soundness", color="gold")

ax.set_xticks(x)
ax.set_xticklabels(boot_df["year"], rotation=0)
ax.set_title("Reviewer Scores For Different Average Citing Years in NeurIPS 2024 (Accepted)")
ax.set_ylabel("Average Score")
ax.set_xlabel("Rounded Average Year")
ax.set_ylim(1, 4)
ax.legend()

# add sample size labels
for i, year in enumerate(boot_df["year"]):
    count = df[df["rounded_year"] == year].shape[0]
    ax.text(i, 1.05, f'n={count}', ha='center', fontsize=8, rotation=90)


# Annotate global min and max for each category with vertical shift for 2nd and 3rd
boot_df_reset = boot_df.reset_index(drop=True)  # Ensure 0-based indexing

for i, (cat, color, offset) in enumerate(zip(
    ["avg_contribution", "avg_presentation", "avg_soundness"],
    ["skyblue", "salmon", "gold"],
    [-width, 0, width]
)):
    y_shift = 0 if i == 0 else 0.05  # Shift 2nd and 3rd categories up

    for kind in ["min", "max"]:
        year_label, value, orig_idx = extreme_values[cat][kind]
        idx = boot_df_reset.index[boot_df_reset["year"] == year_label][0]
        x_pos = x[idx] + offset
        ax.text(
            x_pos,
            value + 0.05 + y_shift,
            f"{kind}: {value:.2f}",
            ha='center',
            fontsize=8,
            color='black',
            fontweight='bold'
        )


plt.tight_layout()
plt.show()

# Bootstrap and plot recommendation score 
recom_results = []
for year in sorted(df["rounded_year"].unique()):
    subset = df[df["rounded_year"] == year]
    mean, lower, upper = bootstrap_ci(subset["avg_rating"].dropna())
    recom_results.append({
        "year": year,
        "mean": mean,
        "lower": lower,
        "upper": upper
    })

recom_df = pd.DataFrame(recom_results)
recom_df = recom_df.sort_values(by="year", key=lambda x: x.replace("until 2010", "0000"))

# Plotting recommendation scores 
fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(recom_df["year"]))

bars = ax.bar(
    x,
    recom_df["mean"],
    yerr=[
        recom_df["mean"] - recom_df["lower"],
        recom_df["upper"] - recom_df["mean"]
    ],
    capsize=5,
    color="mediumseagreen"
)

ax.set_xticks(x)
ax.set_xticklabels(recom_df["year"], rotation=0)
ax.set_title("Final Recommendation Scores For Different Average Citing Years of NeurIPS 2024 (Accepted)")
ax.set_ylabel("Average Score")
ax.set_xlabel("Rounded Average Year")
ax.set_ylim(1, 10)

# Add sample size labels
for i, year in enumerate(recom_df["year"]):
    count = df[df["rounded_year"] == year].shape[0]
    ax.text(i, 1.05, f'n={count}', ha='center', fontsize=8, rotation=90)

# Highlight specific years with dashed lines
highlight_years = ["2021", "until 2010"]
for i, row in recom_df.iterrows():
    if row["year"] in highlight_years:
        idx = recom_df.index.get_loc(i)
        mean_val = row["mean"]
        ax.axhline(y=mean_val, color="gray", linestyle="--", linewidth=1)
        ax.text(
            x=idx + 0.25, y=mean_val + 0.1,
            s=f"{mean_val:.2f}",
            color="gray", fontsize=8
        )

plt.tight_layout()
plt.show()

from scipy.stats import chi2_contingency

def chi_square_test(df, score_column, year_column="rounded_year", bins=[1, 2, 3, 4, 5, 6, 7, 8]):
    # Bin scores into discrete categories
    binned_scores = pd.cut(df[score_column], bins=bins, right=False, include_lowest=True)
    contingency_table = pd.crosstab(df[year_column], binned_scores)

    # Perform chi-square test
    chi2, p, dof, expected = chi2_contingency(contingency_table)
    
    print(f"Chi-square test for {score_column}:")
    print(f"Chi2 statistic: {chi2:.3f}, p-value: {p:.4f}, degrees of freedom: {dof}")
    return chi2, p, dof, expected


def chi_square_test_sep(df, score_column, year_column="rounded_year", bins=[1, 2, 3, 4]):
    # Bin scores into discrete categories
    binned_scores = pd.cut(df[score_column], bins=bins, right=False, include_lowest=True)
    contingency_table = pd.crosstab(df[year_column], binned_scores)

    # Perform chi-square test
    chi2, p, dof, expected = chi2_contingency(contingency_table)
    
    print(f"Chi-square test for {score_column}:")
    print(f"Chi2 statistic: {chi2:.3f}, p-value: {p:.4f}, degrees of freedom: {dof}")
    return chi2, p, dof, expected

chi_square_test_sep(df, "avg_contribution")
chi_square_test_sep(df, "avg_presentation")
chi_square_test_sep(df, "avg_soundness")
chi_square_test(df, "avg_rating")
