'''pip install PyPDF2'''

import os
import re
import csv
from tqdm import tqdm  
from PyPDF2 import PdfReader

# path to pdf folders 
pdf_directory = "/content/drive/MyDrive/Thesis/ICLR2013_submissions_pdfs"
output_csv_path = "/content/drive/MyDrive/Thesis/ICLR2013_submissions_list.csv"

# extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def extract_references(text):
    references = []

    # Locate the References section
    match = re.search(r"\bREFERENCES\b", text, re.IGNORECASE)
    if not match:
        return []

    # Extract text after "REFERENCES"
    references_text = text[match.end():].strip()

    # Stop at "Appendix" or "Acknowledgments", case-insensitive
    stop_match = re.search(r"\b(Appendix|Acknowledgments)\b", references_text, re.IGNORECASE)
    if stop_match:
        references_text = references_text[:stop_match.start()].strip()

    # Process references by detecting boundaries correctly
    lines = references_text.split("\n")
    references = []
    current_ref = ""

    ref_boundary_pattern = re.compile(r".*(\d{4}[a-z]?\.|https?://\S+)$")

    for i, line in enumerate(lines):
        line = line.strip()

        if current_ref:
            current_ref += " " + line
        else:
            current_ref = line

        if ref_boundary_pattern.match(line):  # If the current line ends with YYYY. or a URL
            references.append(" ".join(current_ref.split()))
            current_ref = ""

    # Add the last reference if it exists
    if current_ref:
        references.append(" ".join(current_ref.split()))

    return references

# Process all PDFs in the directory
all_references = []
pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith(".pdf")]

for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
    pdf_path = os.path.join(pdf_directory, pdf_file)
    text = extract_text_from_pdf(pdf_path)

    if text:
        references = extract_references(text)

        # Print the first two references for each PDF
        print(f"\n {pdf_file} - First 2 References:")
        for ref in references[:2]: 
            print(f"  - {ref}")

        all_references.extend([(pdf_file, ref) for ref in references])

# save the titles to csv 
with open(output_csv_path, mode="w", newline="", encoding="utf-8-sig", errors="replace") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["PDF File", "Reference"])  # Header row
    writer.writerows(all_references)

print(f"\n Extraction completed! Results saved to {output_csv_path}")