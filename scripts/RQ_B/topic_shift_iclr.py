import pandas as pd
import ast
import re

# load csv that contains field of study info from S2
df_suggestion = pd.read_csv("ICLR2023_suggestion_full_ab.csv")

# extract 'title' from 'paper_details'
def extract_title(detail):
    try:
        data = ast.literal_eval(detail)
        return data.get("title", None)
    except:
        return None

df_suggestion['title'] = df_suggestion['paper_details'].apply(extract_title)

def extract_submission_id(invitation):
    if pd.isna(invitation):
        return None
    match = re.search(r'Paper(\d+)', invitation)
    return match.group(1) if match else None

df_suggestion['paper_id'] = df_suggestion['invitation'].apply(extract_submission_id)

#print(df_suggestion['paper_id'].head())

# drop rows with missing paper_id or title
df_suggestion_clean = df_suggestion.dropna(subset=['title', 'paper_id'])


# Load and match with "ICLR2023_recommended_topics.csv"
df_topics = pd.read_csv("ICLR2023_recommended_topics.csv")
df_topics['pure_titles'] = df_topics['pure_titles'].str.strip().str.lower()
df_suggestion_clean['title'] = df_suggestion_clean['title'].str.strip().str.lower()


# Merge on title
df_merged = pd.merge(df_topics, df_suggestion_clean[['title', 'paper_id']], 
                     left_on='pure_titles', right_on='title', how='left')


#print(df_merged["title"].head())

# Load and process "ICLR2023_submissions.csv"
df_submissions = pd.read_csv("ICLR2023_submissions.csv")

# Use 'number' column directly as paper_id (convert to string for consistency)
df_submissions['paper_id'] = df_submissions['number'].astype(str)

# Merge everything and prepare final output
df_final = pd.merge(df_merged, df_submissions[['paper_id', 'closest_area']], on='paper_id', how='left')

# Rename columns
df_final = df_final.rename(columns={
    'closest_area': 'paper_area',
    'topic 1': 'suggested_area'
})

# Remove text in parentheses for both columns
df_final['paper_area'] = df_final['paper_area'].str.replace(r'\s*\(.*?\)', '', regex=True)
df_final['suggested_area'] = df_final['suggested_area'].str.replace(r'\s*\(.*?\)', '', regex=True)

# Keep only necessary columns
df_final_output = df_final[['paper_id', 'paper_area', 'suggested_area']]

print(df_final_output["paper_area"].head())
df_final_output.to_csv("ICLR2023_topic_shift.csv", index=False)



import plotly.graph_objects as go
import random

def plot_sankey(df, source_col='suggested_area', target_col='paper_area'):
    # Normalize and strip whitespace (prevent matching issues)
    df[source_col] = df[source_col].str.strip().str.title()
    df[source_col] = df[source_col].str.strip().replace({"Deep Learning And Representational Learning": "Deep Learning And Representational Learning "}) # add space to prevent loop in sankey diagram
    df[target_col] = df[target_col].str.strip().str.title()

    focus_areas = {"Deep Learning And Representational Learning"} #applications deep learning and representational learning reinforcement learning

    # keep only rows where paper_area is in focus areas
    df_filtered = df[df[target_col].isin(focus_areas)].dropna(subset=[source_col, target_col])

    if df_filtered.empty:
        print("No data found where paper_area matches the focus areas.")
        return

    # Get unique labels and map to indexes
    all_labels = pd.unique(df_filtered[[source_col, target_col]].values.ravel())
    label_to_index = {label: i for i, label in enumerate(all_labels)}

    # Generate random colors for each label
    def random_color():
        return f"rgba({random.randint(50, 200)}, {random.randint(50, 200)}, {random.randint(50, 200)}, 0.8)"

    label_colors = [random_color() for _ in all_labels]

    # Count flows
    flow_data = df_filtered.groupby([source_col, target_col]).size().reset_index(name='count')

    sources = flow_data[source_col].map(label_to_index)
    targets = flow_data[target_col].map(label_to_index)
    values = flow_data['count']

    # Plot Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
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

    fig.update_layout(title_text="Flow of Recommended Field to Paper Field", font_size=18, width=800, height=850) 
    fig.show()


plot_sankey(df_final_output)