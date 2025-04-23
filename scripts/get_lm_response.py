import csv
import requests

input_csv_path = 'shuffled_NeurIPSwithoutLabels.csv'
output_csv_path = 'NeurIPS_gemma2b_A.csv'

# LM Studio API 
lm_studio_api_url = 'http://localhost:1234/v1/chat/completions'

# Prompt
question = "Does this peer review explicitly suggest the authors of the paper to cite any specific literature?"  

'''
Prompt A "Does this peer review explicitly suggest the authors of the paper to cite any specific literature?"
Prompt B "Does this peer review suggest the authors of the paper to refer to any other literature?"
Prompt C "Does this peer review suggest the authors of the paper to refer to any other additional literature? Answer yes or no at the beginning."
Prompt D “Does this peer review suggest the authors of the paper to refer to specific literature that are not already discussed in the original paper?"
Prompt E “Does this peer review suggest the authors of the paper to refer to specific literature that are not already discussed in the original paper? Note that sometimes the reviewers mention some literature in their reviews but those could be already included in the original paper."
'''

# send prompt and reviews to LM Studio and get a response
def send_to_lm_studio(context, question):
    payload = {
        "model": "gemma-2b-it", 
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Context: {context}\nQuestion: {question}"}
        ]
    }
    headers = {
        "Content-Type": "application/json"
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
        fieldnames = reader.fieldnames + ['response']  # Add a new column for the response

        with open(output_csv_path, mode='w', encoding='utf-8', newline='') as output_file:
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)  
            writer.writeheader()

            for row in reader:
                entry_id = row.get("id", "").strip()  # ensure the "id" field is correctly retrieved

                if not entry_id:
                    print("Warning: Missing ID for a row. Skipping.")
                    continue

                # all relevant columns for context
                context_columns = [
                    "summary",
                    "strengths",
                    "weaknesses",
                    "questions",
                    "limitations",
                    "flag_for_ethics_review",
                    "rating"
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
