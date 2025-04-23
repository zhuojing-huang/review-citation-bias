import json

with open("ICLR2023.json", "r", encoding="utf-8") as f1, open("ICLR2023_decisions.json", "r", encoding="utf-8") as f2:
    json1_list = json.load(f1)  # json1 contains multiple submissions
    json2_list = json.load(f2)  # json2 contains multiple decisions

# ensure json_list are lists
if not isinstance(json1_list, list):
    json1_list = [json1_list]
if not isinstance(json2_list, list):
    json2_list = [json2_list]

# create a mapping of submission IDs to decisions
json2_map = {}
for json2 in json2_list:
    # for each decision entry, extract the submission ID(s) from the invitations
    submission_ids = [inv.split("/")[3] for inv in json2.get("invitations", []) if "Submission" in inv]

    # map the submission ID to its decision and comment
    for submission_id in submission_ids:
        json2_map[submission_id] = {
            "decision": {"value": json2["content"].get("decision", {}).get("value", "None")},
            "comment": {"value": json2["content"].get("comment", {}).get("value", "None")}
        }

# update review json with corresponding decisions
for json1 in json1_list:
    invitations = json1.get("invitations", [])
    # extract the submission ID from the invitations
    submission_ids = [inv.split("/")[3] for inv in invitations if "Submission" in inv]

    # check if any of the submission IDs have corresponding decisions in json2_map
    matched = False
    for submission_id in submission_ids:
        if submission_id in json2_map:
            # update content with the matching decision and comment
            json1["content"].update(json2_map[submission_id])
            matched = True
            break  # stop once a match is found

    if not matched:
        json1["content"].update({
            "decision": {"value": "None"},
            "comment": {"value": "None"}
        })

with open("ICLR2023_with_decision.json", "w", encoding="utf-8") as f:
    json.dump(json1_list, f, indent=4, ensure_ascii=False)

print(f"Updated {len(json1_list)} submissions saved.")
