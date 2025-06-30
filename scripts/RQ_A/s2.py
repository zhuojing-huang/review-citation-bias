import pandas as pd
import requests
import time
import random
from tqdm import tqdm

# Replace with your Semantic Scholar API Key
S2_API_KEY = "yourAPIkey"

HEADERS = {"Authorization": f"Bearer {S2_API_KEY}"}

def request_with_retries(url, params=None, max_retries=10, backoff_factor=1):
    """Perform a GET request with retries and an API key."""
    retries = 0
    while retries < max_retries:
        response = requests.get(url, params=params, headers=HEADERS)
        if response.status_code == 200:
            return response
        elif response.status_code == 429:  # Rate limit
            wait_time = backoff_factor * (1 ** retries) + random.uniform(0, 1)
            print(f"Rate limited. Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
            retries += 1
        else:
            print(f"Request failed ({response.status_code}): {response.text}")
            return None
    print("Max retries reached. Skipping request.")
    return None

def get_paper_id(title_or_url):
    """Get the Semantic Scholar paper ID from a title or arXiv URL."""
    if isinstance(title_or_url, str) and "arxiv.org" in title_or_url:
        arxiv_id = title_or_url.split("/")[-1].replace(".pdf", "")  
        return f"ARXIV:{arxiv_id}"
    
    search_url = "https://api.semanticscholar.org/graph/v1/paper/search/match"
    params = {"query": title_or_url, "limit": 1}
    response = request_with_retries(search_url, params=params)
    
    if response:
        data = response.json()
        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]["paperId"]
    
    return None  # No match found

def get_paper_details(paper_id):
    """Fetch paper details from Semantic Scholar."""
    if not paper_id:
        return None
    
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
    fields = "title,authors,abstract,fieldsOfStudy"
    response = request_with_retries(url, params={"fields": fields})
    
    if response:
        return response.json()
    return None

def process_csv(input_csv, output_csv):
    """Step 1: Retrieve paper IDs and save them first."""
    df = pd.read_csv(input_csv)
    df = df.dropna(how="all").reset_index(drop=True)
    
    if "paper_id" not in df.columns:
        df["paper_id"] = None
    
    for index in tqdm(range(len(df)), desc="Retrieving paper IDs", unit="paper"):
        row = df.iloc[index]
        if pd.isna(row["paper_id"]):
            paper_id = get_paper_id(row["paper_info"])
            df.at[index, "paper_id"] = paper_id if paper_id else None
            time.sleep(1)  # Avoid rate limits

    # Save after retrieving paper IDs
    df.to_csv(output_csv, index=False)
    print("Paper IDs saved. Now fetching details...")

    """Step 2: Retrieve paper details separately"""
    if "paper_details" not in df.columns:
        df["paper_details"] = None
    
    tqdm.pandas(desc="Fetching details")
    df["paper_details"] = df["paper_id"].progress_apply(lambda pid: get_paper_details(pid) if pid else None)

    df.to_csv(output_csv, index=False)
    print("Processing complete. Output saved.")

# Example usage:
process_csv("EMNLP2023_suggested_citation_400.csv", "EMNLP2023_suggested_citation_400_output_ab.csv")
