!pip install PyPDF2

import os
import re
import csv
from tqdm import tqdm  # For progress bar
from PyPDF2 import PdfReader

# path to the submission PDFs
pdf_directory = '/content/drive/MyDrive/Thesis/EMNL2023_submissions'
output_csv_path = '/content/drive/MyDrive/Thesis/EMNL2023_citation_analysis_results.csv'

# extract text from PDF using PdfReader
def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

# Function to process arXiv years
def process_arxiv_years(years, text):
    processed_years = []
    for year in years:
        match = re.search(rf"arXiv:\s?{year}", text)
        if match:
            new_year = int("20" + str(year)[:2])  # Modify arXiv years
            processed_years.append(new_year)
        else:
            processed_years.append(year)
    return processed_years
    
# Function to extract references and publication years
def extract_references_and_years(text):
    # locate the References section
    references_start = re.search(r"\bREFERENCES\b", text)
    if not references_start:
        return []  # No References section found

    references_text = text[references_start.start():]

    # extract years in the form of numbers like 2020, 2021b, etc.
    year_matches = re.findall(r"(?:\s?\(?)(19[0-9]{2}|20([01][0-9]|2[0-5]))(?:\)?[a-zA-Z]*\.?|\s?[a-zA-Z]+\s?\d{4}[\.]?)", references_text)

    # Extract only the numeric year part
    years = [int(match[0]) for match in year_matches]

    # Process arXiv years
    years = process_arxiv_years(years, references_text)

    return years


# process all PDFs and analyze citation years
def analyze_citation_years(pdf_directory, output_csv_path):
    all_years = []
    paper_averages = []
    results = []  

    # get the list of PDF files
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]

    # progress bar
    with tqdm(total=len(pdf_files), unit="file") as pbar:
        for filename in pdf_files:
            pdf_path = os.path.join(pdf_directory, filename)

            # extract text from PDF
            text = extract_text_from_pdf(pdf_path)

            # extract years from the references section
            years = extract_references_and_years(text)

            if years:
                paper_average = sum(years) / len(years)
                paper_averages.append((filename, paper_average))
                print(f"{filename}, Average Year: {paper_average}, Years: {years}")
                # qdd results to csv 
                results.append({
                    'filename': filename,
                    'extracted_years': ', '.join(map(str, years)),
                    'average_year': round(paper_average, 2)
                })

            all_years.extend(years)
            pbar.update(1)

    # calculate overall average year
    if all_years:
        overall_average = sum(all_years) / len(all_years)
        print(f"\nProcessed {len(all_years)} citations across all papers.")
        print(f"Overall average citation year: {overall_average:.2f}")
    else:
        print("No citation years found.")

    # print per-paper averages
    print("\nPer-paper citation averages:")
    for filename, avg in paper_averages:
        print(f"{filename}: {avg:.2f}")

    # save to CSV
    with open(output_csv_path, mode='w', newline='') as file:
        fieldnames = ['filename', 'extracted_years', 'average_year']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for result in results:
            writer.writerow(result)

# run the analysis and save the results to CSV
analyze_citation_years(pdf_directory, output_csv_path)





