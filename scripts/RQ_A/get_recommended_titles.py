import csv
import requests
import time
import json
import os

input_csv_path = 'ICLR2017_suggest_to_cite.csv'
output_csv_path = 'extracted_ICLR2017_v5.csv'

# LM API URL 
lm_studio_api_url = 'https://chat-ai.academiccloud.de/v1/chat/completions'

# Bearer token from curl request
authorization_token = 'a023e1ca1303dede4cabd22cd7e17108'

# Prompt
question = """
Extract paper titles suggested by the reviewers from the text. Sometimes they exist in the form of links. 
If titles do not directly exist, extract author and year information, but only do so when the titles are not directly available. 
Do not give me extra text including punctuation and numbering.
"""

def load_processed_ids(output_csv_path):
    """Loads already processed IDs from the output CSV to avoid redundant API calls."""
    processed_ids = set()
    if os.path.exists(output_csv_path):
        with open(output_csv_path, mode='r', encoding='utf-8') as output_file:
            reader = csv.DictReader(output_file)
            processed_ids = {row['id'].strip() for row in reader if row.get('id')}
    return processed_ids

def send_to_lm_studio(context, question, max_retries=10, backoff_factor=2):
    payload = {
        "model": "meta-llama-3.1-70b-instruct",
        "temperature": 0.2, 
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Context: {context}\nQuestion: {question}"}
        ]
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {authorization_token}"
    }
    
    for attempt in range(max_retries):
        response = requests.post(lm_studio_api_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        elif response.status_code in [500, 501, 502, 503, 504]:  # Handle server errors
            print(f"Retry {attempt + 1}/{max_retries} due to {response.status_code} error.")
            time.sleep(backoff_factor * (attempt + 1))  # Exponential backoff
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break
    
    return None

def process_reviews(input_csv_path, output_csv_path, sleep_time=1):
    processed_ids = load_processed_ids(output_csv_path)
    count = 0
    
    with open(input_csv_path, mode='r', encoding='utf-8') as input_file:
        reader = csv.DictReader(input_file)
        fieldnames = reader.fieldnames + ['paper_info']  # Add a new column for the response
        file_exists = os.path.exists(output_csv_path)
        
        with open(output_csv_path, mode='a', encoding='utf-8', newline='') as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            for row in reader:
                entry_id = row.get("id", "").strip()
                if not entry_id:
                    print("Warning: Missing ID for a row. Skipping.")
                    continue
                
                if entry_id in processed_ids:
                    print(f"Skipping already processed ID: {entry_id}")
                    continue
                
                # Extract context
                context_columns = ["review"]
                context = "\n".join([f"{col}: {row.get(col, '').strip()}" for col in context_columns if row.get(col)])
                
                print(f"Processing entry ID: {entry_id} ({count + 1})")
                
                # Send request to LM Studio
                response = send_to_lm_studio(context, question)
                row['paper_info'] = response if response else "Failed to get response"
                writer.writerow(row)
                
                if response:
                    print(f"Response for ID {entry_id}: {response}\n")
                else:
                    print(f"Failed to get response for ID {entry_id}\n")
                
                count += 1
                time.sleep(sleep_time)  # Sleep to avoid hitting rate limits

def retry_failed_responses(output_csv_path, sleep_time=2):
    """Reprocess rows where 'Failed to get response' was recorded."""
    temp_output_path = output_csv_path + ".tmp"
    
    with open(output_csv_path, mode='r', encoding='utf-8') as input_file, \
         open(temp_output_path, mode='w', encoding='utf-8', newline='') as output_file:
        
        reader = csv.DictReader(input_file)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            if row.get("paper_info", "").strip() == "Failed to get response":
                entry_id = row.get("id", "").strip()
                context_columns = ["review"]
                context = "\n".join([f"{col}: {row.get(col, '').strip()}" for col in context_columns if row.get(col)])
                
                print(f"Retrying failed response for ID: {entry_id}")
                response = send_to_lm_studio(context, question)
                row['paper_info'] = response if response else "Failed to get response"
                time.sleep(sleep_time)
            
            writer.writerow(row)
    
    os.replace(temp_output_path, output_csv_path)  # Replace old file with updated one

if __name__ == "__main__":
    try:
        process_reviews(input_csv_path, output_csv_path, sleep_time=2)
        print("Initial processing complete. Retrying failed responses...")
        retry_failed_responses(output_csv_path, sleep_time=2)
        print("Retrying failed responses complete.")
    except Exception as e:
        print(f"An error occurred: {e}")
