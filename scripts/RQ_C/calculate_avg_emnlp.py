import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# emnlp only has one meaningful subset for this RQ
df = pd.read_csv("EMNLP2023_scores.csv")
categories = ["soundness", "excitement", "reproducibility"] # numerical columns with review scores

# extract numerical scores and compute averages
for cat in categories:
    for i in range(1, 10):
        col = f"reviewer{i}_{cat}"
        if col in df.columns:
            df[col] = df[col].astype(str).str.extract(r"^(\d)").astype(float)
    cols = [f"reviewer{i}_{cat}" for i in range(1, 10) if f"reviewer{i}_{cat}" in df.columns]
    df[f"avg_{cat}"] = df[cols].mean(axis=1)

# Overall mean score across categories
df["avg_score"] = df[[f"avg_{cat}" for cat in categories]].mean(axis=1)

# round years to the nearest integer
def custom_round_year(year):
    if year < 2010.5:
        return "until 2010"
    elif 2022 <= year < 2023:
        return "2022"
    else:
        return str(int(np.ceil(year)))

df["rounded_year"] = df["average_year"].apply(custom_round_year)

# Bootstrapping function 
def bootstrap_ci(data, n_bootstrap=1000, ci=95):
    boot_means = [data.sample(frac=1, replace=True).mean() for _ in range(n_bootstrap)]
    lower = np.percentile(boot_means, (100 - ci) / 2)
    upper = np.percentile(boot_means, 100 - (100 - ci) / 2)
    return np.mean(boot_means), lower, upper

# Bootstrap and aggregate for original plot
results = []
for year in sorted(df["rounded_year"].unique()):
    subset = df[df["rounded_year"] == year]
    row = {"year": year}
    for cat in ["avg_soundness", "avg_excitement", "avg_reproducibility"]:
        mean, lower, upper = bootstrap_ci(subset[cat].dropna())
        row[f"{cat}_mean"] = mean
        row[f"{cat}_lower"] = lower
        row[f"{cat}_upper"] = upper
    results.append(row)

boot_df = pd.DataFrame(results)
boot_df = boot_df.sort_values(by="year", key=lambda x: x.replace("until 2010", "0000"))

#  Plot original grouped bar chart 
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(boot_df["year"]))
width = 0.25

ax.bar(x - width, boot_df["avg_soundness_mean"], width,
       yerr=[boot_df["avg_soundness_mean"] - boot_df["avg_soundness_lower"],
             boot_df["avg_soundness_upper"] - boot_df["avg_soundness_mean"]],
       capsize=5, label="soundness", color="skyblue")

ax.bar(x, boot_df["avg_excitement_mean"], width,
       yerr=[boot_df["avg_excitement_mean"] - boot_df["avg_excitement_lower"],
             boot_df["avg_excitement_upper"] - boot_df["avg_excitement_mean"]],
       capsize=5, label="excitement", color="salmon")

ax.bar(x + width, boot_df["avg_reproducibility_mean"], width,
       yerr=[boot_df["avg_reproducibility_mean"] - boot_df["avg_reproducibility_lower"],
             boot_df["avg_reproducibility_upper"] - boot_df["avg_reproducibility_mean"]],
       capsize=5, label="reproducibility", color="gold")

ax.set_xticks(x)
ax.set_xticklabels(boot_df["year"], rotation=0)
ax.set_title("Reviewer Scores For Different Average Citing Years (EMNLP2023)")
ax.set_ylabel("Average Score")
ax.set_xlabel("Rounded Average Year")
ax.set_ylim(1, 4)
ax.legend()

# Add sample size labels
for i, year in enumerate(boot_df["year"]):
    count = df[df["rounded_year"] == year].shape[0]
    ax.text(i, 1.05, f'n={count}', ha='center', fontsize=8, rotation=90)

plt.tight_layout()
plt.show()

# compute and plot the overall mean score 
mean_results = []
for year in sorted(df["rounded_year"].unique()):
    subset = df[df["rounded_year"] == year]
    mean, lower, upper = bootstrap_ci(subset["avg_score"].dropna())
    mean_results.append({
        "year": year,
        "mean": mean,
        "lower": lower,
        "upper": upper,
        "n": len(subset)
    })

mean_df = pd.DataFrame(mean_results)
mean_df = mean_df.sort_values(by="year", key=lambda x: x.replace("until 2010", "0000"))

# Plot overall mean score with dashed line 
fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(mean_df["year"]))
width = 0.4

ax.bar(x, mean_df["mean"], width,
       yerr=[mean_df["mean"] - mean_df["lower"], mean_df["upper"] - mean_df["mean"]],
       capsize=5, color="mediumseagreen")

# Add dashed line at highest mean value
max_mean = mean_df["mean"].max()
ax.axhline(max_mean, color="black", linestyle="--", linewidth=1)
ax.text(len(x) - 0.5, max_mean + 0.05, f"Highest Mean: {max_mean:.2f}", va='bottom', ha='right', fontsize=9, color="black")

ax.set_xticks(x)
ax.set_xticklabels(mean_df["year"], rotation=0)
ax.set_title("Overall Reviewer Score by Citing Year For EMNLP (Total)")
ax.set_ylabel("Average Score")
ax.set_xlabel("Rounded Average Year")
ax.set_ylim(1, 4)

# Add sample size labels
for i, row in mean_df.iterrows():
    ax.text(x[i], 1.05, f'n={row["n"]}', ha='center', fontsize=8, rotation=90)

plt.tight_layout()
plt.show()

from scipy.stats import chi2_contingency

def chi_square_test(df, score_column, year_column="rounded_year", bins=[1, 2, 3, 4, 5]):
    # Bin scores into discrete categories
    binned_scores = pd.cut(df[score_column], bins=bins, right=False, include_lowest=True)
    contingency_table = pd.crosstab(df[year_column], binned_scores)

    # Perform chi-square test
    chi2, p, dof, expected = chi2_contingency(contingency_table)
    
    print(f"Chi-square test for {score_column}:")
    print(f"Chi2 statistic: {chi2:.3f}, p-value: {p:.4f}, degrees of freedom: {dof}")
    return chi2, p, dof, expected


chi_square_test(df, "avg_soundness")
chi_square_test(df, "avg_excitement")
chi_square_test(df, "avg_reproducibility")
chi_square_test(df, "avg_score")