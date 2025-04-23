import json
import csv

def json_to_csv(json_file, csv_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    csv_data = []
    headers = set()

    # define ordered keys for the content section (have to manually check and order)
    ordered_content_keys = [
        "summary_of_the_paper",
        "strength_and_weaknesses",
        "clarity,_quality,_novelty_and_reproducibility",
        "summary_of_the_review",
        "confidence",
        "correctness",
        "technical_novelty_and_significance",
        "empirical_novelty_and_significance",
        "flag_for_ethics_review",
        "recommendation"
    ]

    # flatten each record
    for record in data:
        flat_record = {}

        # extract top-level fields
        for key, value in record.items():
            if key == "content" and isinstance(value, dict):
                # handle nested 'content' dictionary
                for sub_key in ordered_content_keys:
                    content_value = value.get(sub_key, "")
                    if isinstance(content_value, list):
                        # Cconvert lists to a comma-separated string
                        content_value = ", ".join(content_value)
                    flat_record[sub_key] = content_value
                    headers.add(sub_key)
            else:
                # top-level fields
                flat_record[key] = value
                headers.add(key)

        csv_data.append(flat_record)

    # rearrange columns: id, content keys, other metadata
    headers = ["id"] + ordered_content_keys + sorted(h for h in headers if h not in ["id"] + ordered_content_keys)

    # write to csv
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(csv_data)

    print(f"JSON data has been successfully converted to CSV and saved as {csv_file}.")

json_file = 'ICLR2023.json'  # input json path
csv_file = 'ICLR2023.csv'    # output csv path

json_to_csv(json_file, csv_file)
