import os
import re
import pandas as pd

def process_csv_files(directory):
    # regex to capture:
    # - Full years (1900-2025) exactly 4 digits
    # - 'YY format (e.g., '22 → 2022)
    # - arXiv-style two-digit years (e.g., 2205 → 2022)
    pattern = re.compile(r"(?<=\b)(19[0-9]{2}|20(0[0-9]|1[0-9]|2[0-4]))\b|(?:'(\d{2}))|(?:abs\/|arxiv\.org\/pdf\/|arXiv:|arXiv )(\d{2})(\d{2})")

    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath)
            
            if "response" in df.columns:
                # regex transformation
                def extract_years(text):
                    matches = [
                        match[0] if match[0] and len(match[0]) == 4 else  # Full year (e.g., 1999, 2020)
                        f"20{match[3]}" if match[3] else  # arXiv-style (e.g., 2205 → 2022)
                        (f"{'19' if int(match[2]) > 24 else '20'}{match[2]}" if match[2] else None)  # 'YY format (e.g., '22 → 2022)
                        for match in pattern.findall(text)
                    ]

                    # Join valid years
                    return ", ".join(filter(None, matches)) if matches else ""

                df["suggested_years"] = df["response"].astype(str).apply(extract_years)

                output_filepath = os.path.join(directory, f"extracted_{filename}")
                df.to_csv(output_filepath, index=False)
                print(f"Processed: {filename} -> {output_filepath}")
            else:
                print(f"Skipping {filename}: No 'response' column found.")

process_csv_files(r"C:\Users\zoehu\OneDrive - stud.uni-goettingen.de\Thesis\review data\model response")
