import pandas as pd
import re
import ast

# load both lists of suggested papers and cited papers
df1 = pd.read_csv('ICLR2023_suggestion_full_ab.csv')
df2 = pd.read_csv('ICLR2023_citation_extracted_clean.csv')


def extract_field(x, field):
    if pd.isna(x):
        return None
    try:
        return ast.literal_eval(x).get(field)
    except (ValueError, SyntaxError):
        return None


# extract title directly if paper_details is already a dict
df1['title'] = df1['paper_details'].apply(lambda x: extract_field(x, 'title'))

def extract_submission_id(inv_list):
    match = re.search(r'Paper\d+', str(inv_list))
    if match:
        return match.group(0).replace('Paper', 'Submission')
    return None

df1['submission_id'] = df1['invitation'].apply(extract_submission_id)

''' # for API2
# Extract Submission ID from invitations (e.g., "Submission1404")
def extract_submission_id(inv_list):
    match = re.search(r'Submission\d+', str(inv_list))
    return match.group(0) if match else None

df1['submission_id'] = df1['invitations'].apply(extract_submission_id)

'''
# normalize submission ID in df2 (e.g., "submission1404.pdf" -> "Submission1404")
df2['submission_id'] = df2['PDF File'].str.extract(r'(submission\d+)', expand=False).str.capitalize()

# merge the two df on submission_id
merged_df = pd.merge(df1, df2, on='submission_id', how='inner')

# normalize text (lowercase, strip whitespace)
def normalize_text(text):
    if isinstance(text, str):
        return text.lower().strip()  # Convert to lowercase and strip spaces
    return ""

# extract 4-grams from a string
def get_ngrams(text, n=4):
    normalized_text = normalize_text(text)  # Normalize the text before processing
    words = re.findall(r'\w+', normalized_text)  # Extract words
    return set(tuple(words[i:i+n]) for i in range(len(words) - n + 1))



# check for at least one shared 4-gram
def has_4gram_match(title, reference):
    title_ngrams = get_ngrams(title, n=4)
    reference_ngrams = get_ngrams(reference, n=4)
    return not title_ngrams.isdisjoint(reference_ngrams)

# apply 4-gram matching
merged_df['title_in_reference'] = merged_df.apply(
    lambda row: has_4gram_match(row['title'], row['Reference']), axis=1
)

# Keep only one row per submission_id
# filter rows where 'title_in_reference' is TRUE
filtered_df = merged_df[merged_df['title_in_reference'] == True]

# drop duplicates based on 'submission_id' column
filtered_df = filtered_df.drop_duplicates(subset='submission_id')

def compute_match_percentage(filtered_df, original_df):
    true_matches = filtered_df[filtered_df['title_in_reference'] == True]
    true_count = len(true_matches)
    total_ids = original_df['submission_id'].nunique()
    percentage = (true_count / total_ids) * 100 if total_ids else 0
    print(f"Matched: {true_count} / {total_ids} ({percentage:.2f}%)\n")

    print("Matched Titles:")
    for idx, row in true_matches.iterrows():
        print(f"- {row['submission_id']}: {row['title']}")


compute_match_percentage(filtered_df, df1)


# save to csv
def save_to_csv(df, filename):
    df.to_csv(filename, index=False) 

