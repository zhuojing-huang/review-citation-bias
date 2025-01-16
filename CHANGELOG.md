# Changelog for Peer Review Data

This changelog tracks all changes, updates, and annotations made to the peer review data during the project lifecycle.

---

## **v20250117 - 2025-01-17 (First Release)**
### **2025-01-01**
- Retrieved **EMNLP 2023** and **NeurIPS 2023 & 2024** peer review data using `API2.0_get_data.py` (OpenReview API v2.0).  
  - Files saved:
    - `EMNLP2023.json`
    - `NeurIPS2023.json`
    - `NeurIPS2024.json`

### **2025-01-01**
- Retrieved **ICLR 2023** peer review data using `API1.0_get_data.py` (OpenReview API v1.0).  
  - File saved:
    - `ICLR2023.json`

---

## **Data Conversion**
### **2025-01-13**
- Converted JSON data into CSV format using respective conversion scripts:
  - `EMNLP2023.json` → `EMNLP2023.csv`
  - `NeurIPS2023.json` → `NeurIPS2023.csv`
  - `NeurIPS2024.json` → `NeurIPS2024.csv`
  - `ICLR2023.json` → `ICLR2023.csv`

---

## **Annotation Process**
### **2025-01-13**
- Manually annotated **100 reviews** per venue:
  - **Positive Cases** (`1`): 50 reviews where reviewers suggested citing additional literature.
  - **Negative Cases** (`0`): 50 reviews with no such suggestions.
- Files with annotations saved:
  - `EMNLPwithLabels.csv` (50 positive, 50 negative).
  - `NeurIPSwithLabels.csv` (50 positive, 50 negative).
  - `ICLRwithLabels.csv` (50 positive, 50 negative).

---

## **Shuffling Process**
### **2025-01-13**
- Observed issue: Positive cases were at the beginning, and negative cases were at the end of the labeled CSV files.
- Solution: Used `shuffle_csv.py` to randomize the order of labeled data.
- Shuffled files saved:
  - `shuffled_EMNLPwithoutLabels.csv`
  - `shuffled_NeurIPSwithoutLabels.csv`
  - `shuffled_ICLRwithoutLabels.csv`

---

## **Language Model Evaluation**
### **2025-01-13 to 2025-01-17**
- Sent shuffled review data to language models using **LM Studio** and `get_response_csv.py`.
- Language model responses were appended to the CSV files in a new column (`suggest_citation`).
- Final output files with responses saved in the format of *venue_model_prompt*:
  - `EMNLP2023_llama8b_A.csv`
  - `EMNLP2023_llama8b_B.csv`
  - `EMNLP2023_llama8b_C.csv`

---

### **Notes**
- All raw data files (JSON), intermediate files (annotated CSVs), and final files (with model responses) are versioned and stored securely.
- Annotation and shuffling processes were manually verified for consistency.