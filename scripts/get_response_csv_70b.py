import csv
import requests

input_csv_path = 'shuffled_ICLRwithoutLabels.csv'
output_csv_path = 'test.csv'

# LM API URL 
lm_studio_api_url = 'http://services.gipplab.org:8081/v1/chat/completions'

# bearer token from curl request
authorization_token = '9c89c616-649e-4d77-a6ad-1b1e525f94b5'

# prompt: adjust accordingly during the experiment
question = """Does this peer review explicitly say the paper is missing relevant literature? Or should the paper compare to relevant baselines/benchmarks? 
 Answer with yes or no at the very beginning, and give brief explanation."""



def send_to_lm_studio(context, question):
    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct", 
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Context: {context}\nQuestion: {question}"}
        ],
        "stream": False,
        "max_tokens": 500
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {authorization_token}"
    }
    response = requests.post(lm_studio_api_url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def process_reviews(input_csv_path, output_csv_path):
    output_data = []
    with open(input_csv_path, mode='r', encoding='utf-8') as input_file:
        reader = csv.DictReader(input_file) 
        fieldnames = reader.fieldnames + ['response']  # add a new column for the response

        with open(output_csv_path, mode='w', encoding='utf-8', newline='') as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)  
            writer.writeheader()

            for row in reader:
                entry_id = row.get("id", "").strip()  # ensure the "id" field is correctly retrieved

                if not entry_id:
                    print("Warning: Missing ID for a row. Skipping.")
                    continue

                # IMPORTNAT: all relevant columns for context; adjust according to venues
                context_columns = [
                    "summary_of_the_paper",
                    "strength_and_weaknesses",
                    "clarity,_quality,_novelty_and_reproducibility",
                    "summary_of_the_review"
                ]
                context = "\n".join([f"{col}: {row.get(col, '').strip()}" for col in context_columns if row.get(col)])

                print(f"Processing entry ID: {entry_id}")

                # send to LM Studio
                response = send_to_lm_studio(context, question)

                # add the response to the review
                row['response'] = response if response else "Failed to get response"
                writer.writerow(row)

                if response:
                    print(f"Response for ID {entry_id}: {response}\n")
                else:
                    print(f"Failed to get response for ID {entry_id}\n")

if __name__ == "__main__":
    try:
        process_reviews(input_csv_path, output_csv_path)
    except Exception as e:
        print(f"An error occurred: {e}")
