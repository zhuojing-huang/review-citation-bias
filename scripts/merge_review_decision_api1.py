import json

with open('ICLR2023.json', 'r',encoding="utf-8") as f:
    ICLR2023 = json.load(f)

with open('ICLR2023_decisions.json', 'r',encoding="utf-8") as f:
    ICLR2023_decisions = json.load(f)

# merge decisions into reviews based on matching Paper ID
def merge_decisions(ICLR2023, ICLR2023_decisions):
    for review in ICLR2023:
        # Extract Paper ID from the "invitation" field in review JSON
        paper_id = review["invitation"].split("/")[3].replace("Paper", "")

        # flag to check if a matching Paper ID is found
        found = False
        
        for decision in ICLR2023_decisions:
            # extract Paper ID from the "invitation" field in decision JSON 
            decision_paper_id = decision["invitation"].split("/")[3].replace("Paper", "")
            
            # if matching Paper IDs are found, add the decision sections to the review
            if paper_id == decision_paper_id:
                review["content"]["decision"] = decision["content"].get("decision", None)
                review["content"]["metareview:_summary,_strengths_and_weaknesses"] = decision["content"].get("metareview:_summary,_strengths_and_weaknesses", None)
                review["content"]["summary_of_AC-reviewer_meeting"] = decision["content"].get("summary_of_AC-reviewer_meeting", None)
                review["content"]["justification_for_why_not_higher_score"] = decision["content"].get("justification_for_why_not_higher_score", None)
                review["content"]["justification_for_why_not_lower_score"] = decision["content"].get("justification_for_why_not_lower_score", None)
                found = True
                break

        if not found:
            review["content"]["decision"] = None
            review["content"]["metareview:_summary,_strengths_and_weaknesses"] = None
            review["content"]["summary_of_AC-reviewer_meeting"] = None
            review["content"]["justification_for_why_not_higher_score"] = None
            review["content"]["justification_for_why_not_lower_score"] = None

    return ICLR2023

# merge decisions into ICLR2023 reviews
merged_reviews = merge_decisions(ICLR2023, ICLR2023_decisions)

with open('ICLR2023_with_decision.json', 'w') as f:
    json.dump(merged_reviews, f, indent=2)

print("Merged data has been saved to ICLR2023_with_decision.json")
