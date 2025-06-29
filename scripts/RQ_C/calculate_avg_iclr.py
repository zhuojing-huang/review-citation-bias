import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("ICLR2023_accept_score.csv")  ### change manually for different ICLR subsets
categories = ["technical_novelty_and_significance", "empirical_novelty_and_significance", "recommendation"] # numerical coloumns; the actual scores

for cat in categories:
    for i in range(1, 10):
        col = f"reviewer{i}_{cat}"
        if col in df.columns:
            df[col] = df[col].astype(str).str.extract(r"^(\d)").astype(float)
    cols = [f"reviewer{i}_{cat}" for i in range(1, 10) if f"reviewer{i}_{cat}" in df.columns]
    df[f"avg_{cat}"] = df[cols].mean(axis=1)


def custom_round_year(year): # round averaged years to closest integer
    if year < 2010.5:
        return "until 2010"
    elif 2021 <= year < 2022:
        return "2021"
    else:
        return str(int(np.ceil(year)))

df["rounded_year"] = df["average_year"].apply(custom_round_year)


# Bootstrapping
def bootstrap_ci(data, n_bootstrap=1000, ci=95):
    boot_means = [data.sample(frac=1, replace=True).mean() for _ in range(n_bootstrap)]
    lower = np.percentile(boot_means, (100 - ci) / 2)
    upper = np.percentile(boot_means, 100 - (100 - ci) / 2)
    return np.mean(boot_means), lower, upper

# apply for each year and category
results = []
for year in sorted(df["rounded_year"].unique()):
    subset = df[df["rounded_year"] == year]
    row = {"year": year}
    for cat in ["avg_technical_novelty_and_significance", "avg_empirical_novelty_and_significance"]:
        mean, lower, upper = bootstrap_ci(subset[cat].dropna())
        row[f"{cat}_mean"] = mean
        row[f"{cat}_lower"] = lower
        row[f"{cat}_upper"] = upper
    results.append(row)

# convert to df
boot_df = pd.DataFrame(results)
boot_df = boot_df.sort_values(by="year", key=lambda x: x.replace("until 2010", "0000"))

# plotting with Error Bars
fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(boot_df["year"]))
width = 0.35
ax.bar(x - width/2,
       boot_df["avg_technical_novelty_and_significance_mean"],
       width,
       yerr=[boot_df["avg_technical_novelty_and_significance_mean"] - boot_df["avg_technical_novelty_and_significance_lower"],
             boot_df["avg_technical_novelty_and_significance_upper"] - boot_df["avg_technical_novelty_and_significance_mean"]],
       capsize=5, label="Technical Novelty", color="skyblue")

ax.bar(x + width/2,
       boot_df["avg_empirical_novelty_and_significance_mean"],
       width,
       yerr=[boot_df["avg_empirical_novelty_and_significance_mean"] - boot_df["avg_empirical_novelty_and_significance_lower"],
             boot_df["avg_empirical_novelty_and_significance_upper"] - boot_df["avg_empirical_novelty_and_significance_mean"]],
       capsize=5, label="Empirical Novelty", color="salmon")


ax.set_xticks(x)
ax.set_xticklabels(boot_df["year"], rotation=0)
ax.set_title("Reviewer Scores For Different Average Citing Years (ICLR2023)")
ax.set_ylabel("Average Score")
ax.set_xlabel("Rounded Average Year")
ax.set_ylim(1, 4)
ax.legend()
# add sample size labels on top of bars
for i, year in enumerate(boot_df["year"]):
    count = df[df["rounded_year"] == year].shape[0]
    ax.text(i, 1.05, f'n={count}', ha='center', fontsize=8, rotation=90)

# add horizontal dashed lines for min and max across all bars (both categories)
# compute min and max for each category
tech_min = boot_df["avg_technical_novelty_and_significance_mean"].min()
tech_max = boot_df["avg_technical_novelty_and_significance_mean"].max()
emp_min = boot_df["avg_empirical_novelty_and_significance_mean"].min()
emp_max = boot_df["avg_empirical_novelty_and_significance_mean"].max()

# highlight min and max values on top of bars
tech_vals = boot_df["avg_technical_novelty_and_significance_mean"]
emp_vals = boot_df["avg_empirical_novelty_and_significance_mean"]

# get indices of min/max
tech_min_idx = tech_vals.idxmin()
tech_max_idx = tech_vals.idxmax()
emp_min_idx = emp_vals.idxmin()
emp_max_idx = emp_vals.idxmax()

# Technical min and max
ax.text(x[boot_df.index.get_loc(tech_min_idx)] - width/2,
        tech_vals[tech_min_idx] + 0.1,
        f"min: {tech_vals[tech_min_idx]:.2f}",
        ha='center', fontsize=8, color="black")

ax.text(x[boot_df.index.get_loc(tech_max_idx)] - width/2,
        tech_vals[tech_max_idx] + 0.1,
        f"max: {tech_vals[tech_max_idx]:.2f}",
        ha='center', fontsize=8, color="black")

# Empirical min and max
ax.text(x[boot_df.index.get_loc(emp_min_idx)] + width/2,
        emp_vals[emp_min_idx] + 0.17,
        f"min: {emp_vals[emp_min_idx]:.2f}",
        ha='center', fontsize=8, color="black")

ax.text(x[boot_df.index.get_loc(emp_max_idx)] + width/2,
        emp_vals[emp_max_idx] + 0.2,
        f"max: {emp_vals[emp_max_idx]:.2f}",
        ha='center', fontsize=8, color="black")



plt.tight_layout()
plt.show()

# Bootstrapping for Recommendation Only 
recom_results = []
for year in sorted(df["rounded_year"].unique()):
    subset = df[df["rounded_year"] == year]
    mean, lower, upper = bootstrap_ci(subset["avg_recommendation"].dropna())
    recom_results.append({
        "year": year,
        "mean": mean,
        "lower": lower,
        "upper": upper
    })

recom_df = pd.DataFrame(recom_results)

# sort manually with 'before 2005' first
boot_df = boot_df.sort_values(by="year", key=lambda x: x.replace("until 2010", "0000"))
recom_df = recom_df.sort_values(by="year", key=lambda x: x.replace("until 2010", "0000"))

# Plotting Recommendation with Error Bars 
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
ax.set_title("Final Recommendation Scores For Different Average Citing Years (ICLR2023)")
ax.set_ylabel("Average Score")
ax.set_xlabel("Rounded Average Year")
ax.set_ylim(1, 10)

# Add sample size labels on top of bars
for i, year in enumerate(recom_df["year"]):
    count = df[df["rounded_year"] == year].shape[0]
    ax.text(i, 1.05, f'n={count}', ha='center', fontsize=8, rotation=90)

# Add dashed lines for "2021" and "until 2010"
highlight_years = ["2021", "until 2010"]
for i, row in recom_df.iterrows():
    if row["year"] in highlight_years:
        bar_index = recom_df.index.get_loc(i)
        mean_val = row["mean"]
        ax.axhline(y=mean_val, color="gray", linestyle="--", linewidth=1)
        ax.text(
            x=bar_index + 0.25, y=mean_val + 0.1,
            s=f"{mean_val:.2f}",
            color="black", fontsize=8
        )

# Add trend line connecting all bar heights
ax.plot(x, recom_df["mean"].to_numpy(), color="darkgreen", linestyle="--", marker="o")


plt.tight_layout()
plt.show()

from scipy.stats import chi2_contingency

def chi_square_test(df, score_column, year_column="rounded_year", bins=[1, 2, 3, 4, 5,6,7]):
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


chi_square_test_sep(df, "avg_technical_novelty_and_significance")
chi_square_test_sep(df, "avg_empirical_novelty_and_significance")
chi_square_test(df, "avg_recommendation")