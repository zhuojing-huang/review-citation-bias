import pandas as pd
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_recall_curve, auc
import matplotlib.pyplot as plt
from sklearn.metrics import PrecisionRecallDisplay
import numpy as np
import seaborn as sns  


# annotated reviews grouped by venues (EMNLP, NeurIPS, ICLR)
files_groups = {
    "EMNLP": [
        "EMNLPwithLabels.csv", "EMNLP2023_llama8b_A.csv", "EMNLP2023_llama8b_B.csv", 
        "EMNLP2023_llama8b_C.csv", "EMNLP2023_llama8b_D.csv", "EMNLP2023_llama8b_E.csv",
        "EMNLP_llama70b_A.csv","EMNLP_llama70b_B.csv","EMNLP_llama70b_C.csv",
        "EMNLP_llama70b_D.csv","EMNLP_llama70b_E.csv","EMNLP_llama70b_F.csv","EMNLP_llama70b_G.csv"
    ],
    "NeurIPS": [
        "NeurIPSwithLabels.csv", "NeurIPS_llama8b_A.csv", "NeurIPS_llama8b_B.csv", 
        "NeurIPS_llama8b_C.csv", "NeurIPS_llama8b_D.csv", "NeurIPS_llama8b_E.csv",
        "NeurIPS_llama70b_A.csv","NeurIPS_llama70b_B.csv","NeurIPS_llama70b_C.csv",
        "NeurIPS_llama70b_D.csv","NeurIPS_llama70b_E.csv","NeurIPS_llama70b_F.csv","NeurIPS_llama70b_G.csv"
    ],
    "ICLR": [
        "ICLRwithLabels.csv", "ICLR2023_llama8b_A.csv", "ICLR2023_llama8b_B.csv", 
        "ICLR2023_llama8b_C.csv", "ICLR2023_llama8b_D.csv", "ICLR2023_llama8b_E.csv",
        "ICLR_llama70b_A.csv","ICLR_llama70b_B.csv","ICLR_llama70b_C.csv",
        "ICLR_llama70b_D.csv","ICLR_llama70b_E.csv","ICLR_llama70b_F.csv","ICLR_llama70b_G.csv"
    ]
}

# load and align data
def load_and_align(files):
    dataframes = {}
    for file in files:
        df = pd.read_csv(file)
        dataframes[file] = df
    return dataframes

# acc, recall, precision, f1
def compute_metrics(reference_df, compare_df, file_name, group_name):
    merged_df = reference_df.merge(compare_df, on="id", suffixes=("_ref", "_pred"))
    
    true_label_col = "citation_suggestions_ref" if "citation_suggestions_ref" in merged_df.columns else "citation_suggestions"
    pred_label_col = "binary_label" if "binary_label" in merged_df.columns else "citation_suggestions_pred"
    
    if not true_label_col or not pred_label_col:
        print(f"Skipping {file_name} due to missing columns.")
        return None, None, None, None
    
    y_true = merged_df[true_label_col].astype(int)
    y_pred_probs = merged_df[pred_label_col].astype(float)
    y_pred = (y_pred_probs >= 0.5).astype(int)
    
    accuracy = accuracy_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    plot_precision_recall_curve(y_true, y_pred_probs, file_name, group_name)
    
    return accuracy, recall, f1, y_pred_probs

# process each group
def process_group(group_name, files):
    dataframes = load_and_align(files)
    reference_df = dataframes[files[0]]
    
    results = []
    for file, df in dataframes.items():
        if file != files[0]:
            accuracy, recall, f1, _ = compute_metrics(reference_df, df, file, group_name)
            results.append((file, accuracy, recall, f1))
    
    results_df = pd.DataFrame(results, columns=["File", "Accuracy", "Recall", "F1"])
    return results_df

# plots
def plot_results(results_df, group_name):
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    metrics = ["Accuracy", "Recall", "F1"]
    colors = ['b', 'g', 'r']
    
    for i, metric in enumerate(metrics):
        ax = axes[i]
        bars = ax.bar(results_df["File"], results_df[metric], color=colors[i])
        
        ax.set_yticks(np.arange(0, 1.1, 0.1))
        ax.set_ylim(0, 1.1)
        
        max_value = results_df[metric].max()
        max_index = results_df[metric].idxmax()
        max_file = results_df["File"][max_index]
        
        ax.axhline(max_value, color='gray', linestyle='dashed', linewidth=1)
        ax.text(max_index, max_value + 0.02, f"{max_value:.2f}", ha='center', fontsize=10, fontweight='bold')
        
        ax.set_title(f"{group_name} {metric} Comparison")
        ax.set_ylabel(metric)
        ax.tick_params(axis='x', rotation=90)
    
    plt.tight_layout()
    plt.show()

# store PR curves per venue
pr_curve_data = {"EMNLP": [], "NeurIPS": [], "ICLR": []}

def plot_precision_recall_curve(y_true, y_pred_probs, file_name, group_name):
    precision, recall, _ = precision_recall_curve(y_true, y_pred_probs)
    pr_auc = auc(recall, precision)
    pr_curve_data[group_name].append((precision, recall, pr_auc, file_name))


def plot_top_5_venue_pr_curves(group_name):
    plt.figure(figsize=(8, 6))
    
    # sort PR curves by auc and select top 5
    sorted_curves = sorted(pr_curve_data[group_name], key=lambda x: x[2], reverse=True)[:5]
    
    # determine the highest auc value
    best_auc = sorted_curves[0][2]
    
    # blue colors palette for other curves
    color_palette = sns.color_palette("Blues", len(sorted_curves))
    
    for i, (precision, recall, pr_auc, file_name) in enumerate(sorted_curves):
        color = 'red' if pr_auc == best_auc else color_palette[i]
        legend_name = "_".join(file_name.split("_")[1:3])  # shorten legend names
        plt.plot(recall, precision, label=f'{legend_name} (AUC={pr_auc:.2f})', color=color, linewidth=2)
    
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title(f'Top 5 Precision-Recall Curves for {group_name}')
    plt.legend(loc='best', title='Model', frameon=False, fontsize=6, ncol=2)
    plt.grid(True)
    plt.show()

for group_name, files in files_groups.items():
    results_df = process_group(group_name, files)
    plot_results(results_df, group_name)
    plot_top_5_venue_pr_curves(group_name)