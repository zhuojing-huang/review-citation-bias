import pandas as pd
import ast
import re
import plotly.graph_objects as go
import random

# load csv with field of study info from S2
df_suggestion = pd.read_csv("NeurIPS2024_suggestion_full_ab.csv")

def extract_title(detail):
    try:
        data = ast.literal_eval(detail)
        return data.get("title", None)
    except:
        return None

df_suggestion['title'] = df_suggestion['paper_details'].apply(extract_title)

def extract_submission_id(invitations):
    try:
        items = ast.literal_eval(invitations)
        for item in items:
            match = re.search(r'Submission(\d+)', item)
            if match:
                return match.group(1)
    except:
        return None

df_suggestion['paper_id'] = df_suggestion['invitations'].apply(extract_submission_id)
df_suggestion_clean = df_suggestion.dropna(subset=['title', 'paper_id'])

# Load and match with "NeurIPS2024_recommended_topics.csv"
df_topics = pd.read_csv("NeurIPS2024_recommended_topics.csv")

df_merged = pd.merge(df_topics, df_suggestion_clean[['title', 'paper_id']], 
                     left_on='pure_titles', right_on='title', how='left')

# Load and process "NeurIPS2024_submissions.csv"
df_submissions = pd.read_csv("NeurIPS2024_submissions.csv")
df_submissions['paper_id'] = df_submissions['number'].astype(str)

# Merge and prepare final output
df_final = pd.merge(df_merged, df_submissions[['paper_id', 'primary_area']], on='paper_id', how='left')

df_final = df_final.rename(columns={
    'primary_area': 'paper_area',
    'topic 1 ': 'suggested_area'
})

df_final_output = df_final[['paper_id', 'paper_area', 'suggested_area']]
df_final_output.to_csv("NeurIPS2024_topic_shift.csv", index=False)

# Plotting
def plot_sankey(df, source_col='suggested_area', target_col='paper_area'):
    df[source_col] = df[source_col].str.replace("_", " ").str.strip().str.title()
    df[source_col] = df[source_col].str.strip().replace({"Machine Vision": "Machine Vision "}) #add space to prevent looping in graph 
    df[target_col] = df[target_col].str.replace("_", " ").str.strip().str.title()

    focus_areas = {"Machine Vision"}

    # Filter for focus areas
    df_filtered = df[df[target_col].isin(focus_areas)].dropna(subset=[source_col, target_col])

    if df_filtered.empty:
        print("No data found where paper_area matches the focus areas.")
        return

    # Labels and indexes
    all_labels = pd.unique(df_filtered[[source_col, target_col]].values.ravel())
    label_to_index = {label: i for i, label in enumerate(all_labels)}

    def random_color():
        return f"rgba({random.randint(50, 200)}, {random.randint(50, 200)}, {random.randint(50, 200)}, 0.8)"

    label_colors = [random_color() for _ in all_labels]

    flow_data = df_filtered.groupby([source_col, target_col]).size().reset_index(name='count')
    sources = flow_data[source_col].map(label_to_index)
    targets = flow_data[target_col].map(label_to_index)
    values = flow_data['count']

    # Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=1,
            thickness=10,
            line=dict(color="black", width=0.5),
            label=all_labels.tolist(),
            color=label_colors
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color="rgba(150,150,150,0.3)"
        )
    )])

    fig.update_layout(title_text="Flow of Recommended Field to Paper Field", font_size=18,width=800, height=850)
    fig.show()

plot_sankey(df_final_output)
