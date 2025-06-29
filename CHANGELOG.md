# Changelog for Peer Review Data

This changelog tracks all changes, updates, and annotations made to the peer review data during the project lifecycle.

---
## **v20250630 - 2025-06-30 (Final Annotated Dataset Update and Completed Code)**
### **2025-02-16 to 2025-06-30**
- Annotated data for the paper topics are saved under `processed_data\annotated_data_for_topics`
- Annotated data for the titles of recommended papers are saved under `processed_data\annotated_data_for_suggested_papers`
- First completed version of code is saved under `scripts`, with all the folders named after the corresponding research questions. 

---
## **v20250216 - 2025-02-16 (Response Collection Update)**
### **2025-02-04 to 2025-02-16**
#### **Response Collection from llama70b**
- Responses from best models + best prompts are collected for each venue. Data are saved under: `processed_data\processed_data_for_citations_in_review`:
  - `EMNLP2023_llama70b_all`
  - `ICLR2023_llama70b_all`
  - `NeurIPS2023_llama70b_all`
  - `NeurIPS2024_llama70b_all`

---
## **v20250204 - 2025-02-04 (Data & Model Evaluation Update)**
### **2025-01-17 to 2025-02-04**
#### **Data Retrieval**
- Added converted CSV raw review data for **EMNLP 2023**, **NeurIPS 2023 & 2024**, and **ICLR 2023**.
  - Converted CSV files are saved under the path: `raw_data`
    
- Added retrieval of submission PDFs for **EMNLP 2023**, **NeurIPS 2023 & 2024**, and **ICLR 2023** using `API_get_submission_pdf.ipynb`.
  - PDFs stored externally with reference links saved in: `raw_data/all_venues_papers.txt`
    
#### **Annotated Data Revision**
- Annotated data are revisited and the following gold standard was updated under the path `processed_data/annotated_data_for_reviews`:
  - `shuffled_NeurIPSwithoutLabels.csv`
  - `NeurIPSwithLabels.csv`

#### **Response Collection from llama70b**
- Evaluated **llama8b** and **llama70b** models on citation suggestion tasks.
- Responses collected using `get_lm_response.py` (llama8b) and `get_response_csv_70b.py` (llama70b).
- Model responses from llama70b are added to the path `processed_data/annotated_data_for_reviews/` in CSV files:
  - `EMNLP_llama70b_A.csv` ... `EMNLP_llama70b_G.csv`
  - `NeurIPS_llama70b_A.csv` ... `NeurIPS_llama70b_G.csv`
  - `ICLR_llama70b_A.csv` ... `ICLR_llama70b_G.csv`

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
