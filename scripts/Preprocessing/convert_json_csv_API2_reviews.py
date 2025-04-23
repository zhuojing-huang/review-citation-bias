import json
import csv

def json_to_csv(json_file, csv_file):
    # load json 
    with open(json_file, 'r') as f:
        data = json.load(f)

    # csv
    csv_data = []
    headers = set()

    # collect all possible content keys dynamically
    content_keys = set()
    for record in data:
        if "content" in record and isinstance(record["content"], dict):
            content_keys.update(record["content"].keys())

    # sort the content keys (have to manually check and order the columns for easy processing later)
    ordered_content_keys = [
        "summary",
        "strengths",
        "weaknesses",
        "questions",
        "limitations",
        "flag_for_ethics_review",
        "rating",
        "confidence",
        "Reviewer_Confidence",
        "code_of_conduct",
        "contribution",
        "presentation",
        "soundness"
    ]
    all_content_keys = ordered_content_keys + [key for key in sorted(content_keys) if key not in ordered_content_keys]

    # flatten each record
    for record in data:
        flat_record = {}
        
        # extract top-level fields
        for key, value in record.items():
            if key == "content" and isinstance(value, dict):
                # handle nested 'content' dictionary
                for sub_key in all_content_keys:
                    flat_record[sub_key] = value.get(sub_key, {}).get('value', '')
                    headers.add(sub_key)
            else:
                flat_record[key] = value
                headers.add(key)

        csv_data.append(flat_record)

    # rearrange columns: id, contents, other metadata
    headers = ["id"] + all_content_keys + sorted(h for h in headers if h not in ["id", "content"] + all_content_keys)

    # write to CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_data)

json_file = 'NeurIPS2023.json'  # input json path
csv_file = 'NeurIPS2023.csv'    # output csv path

json_to_csv(json_file, csv_file)
print(f"JSON data has been successfully converted to CSV and saved as {csv_file}.")
