# Peer Review Analysis Project

This project provides a framework for analyzing biases induced by citation suggestions from peer review at major AI conferences. It includes tools for retrieving, converting, annotating, and shuffling review data, as well as sending prompts together with review data to open-source large language models to evaluate their performance in suggesting additional citations based on the reviews.

## Data Retrieval

The peer review data for the following conferences was gathered using the **OpenReview API**:
- **EMNLP 2023** and **NeurIPS 2023 & 2024**: Data retrieved using `API2.0_get_data.py`.
- **ICLR 2023**: Data retrieved using `API1.0_get_data.py`.

### Python Files for Data Retrieval
- `API2.0_get_data.py`: Uses OpenReview API v2.0 to fetch peer review data for EMNLP and NeurIPS conferences.
- `API1.0_get_data.py`: Uses OpenReview API v1.0 to fetch peer review data for ICLR.

The retrieved data is defaultly saved in JSON format:
- `EMNLP2023.json`
- `NeurIPS2023.json`
- `NeurIPS2024.json`
- `ICLR2023.json`

## Workflow

### 1. JSON to CSV Conversion
Python scripts are provided to convert the JSON files into CSV format for easier processing for later manual annotation:
- `convert_json_csv_emnlp.py`: Converts EMNLP JSON data to CSV.
- `convert_json_csv_neurips.py`: Converts NeurIPS JSON data to CSV.
- `convert_json_csv_iclr.py`: Converts ICLR JSON data to CSV.

### 2. Manual Annotation
After converting the JSON files to CSV:
1. **Annotate Reviews**: 
   - 50 reviews where reviewers suggest authors cite additional literature are manually marked as **positive cases** (`1`).
   - 50 reviews without such suggestions are manually marked as **negative cases** (`0`).
2. **Distribution**: These 100 labeled cases are evenly distributed across the three venues: EMNLP, NeurIPS, and ICLR, with each of them roughly having 33.3% of the annotated data.
3. Labeled files are saved as:
   - `EMNLPwithLabels.csv`
   - `NeurIPSwithLabels.csv`
   - `ICLRwithLabels.csv`

### 3. Shuffle Labeled Data
The labeled data is shuffled to ensure random distribution:
- **Issue**: Positive cases were originally at the beginning, and negative cases were at the end.
- **Solution**: `shuffle_csv.py` shuffles the labeled data files.
- Resulting files:
  - `shuffled_ICLRwithoutLabels.csv`
  - `shuffled_EMNLPwithoutLabels.csv`
  - `shuffled_NeurIPSwithoutLabels.csv`

### 4. Language Model Response Collection
The shuffled data is used to evaluate language model performance in identifying citation suggestions:
1. `get_response_csv.py` sends each review as a **prompt** to a language model via **LM Studio** API.
2. The model's response is saved in a new column, `suggest_citation`, in the output CSV files.

## File Summary

| File | Description |
|------|-------------|
| `API2.0_get_data.py` | Script to fetch EMNLP and NeurIPS data using OpenReview API v2.0. |
| `API1.0_get_data.py` | Script to fetch ICLR data using OpenReview API v1.0. |
| `EMNLP2023.json` | Raw EMNLP 2023 peer review data in JSON. |
| `NeurIPS2023.json` | Raw NeurIPS 2023 peer review data in JSON. |
| `NeurIPS2024.json` | Raw NeurIPS 2024 peer review data in JSON. |
| `ICLR2023.json` | Raw ICLR 2023 peer review data in JSON. |
| `convert_json_csv_emnlp.py` | Script to convert EMNLP JSON to CSV. |
| `convert_json_csv_neurips.py` | Script to convert NeurIPS JSON to CSV. |
| `convert_json_csv_iclr.py` | Script to convert ICLR JSON to CSV. |
| `shuffle_csv.py` | Script to shuffle labeled data for randomization. |
| `get_response_csv.py` | Script to send reviews to language models and save responses. |
| `shuffled_ICLRwithoutLabels.csv` | Shuffled, unlabeled ICLR data for LM evaluation. |
| `shuffled_EMNLPwithoutLabels.csv` | Shuffled, unlabeled EMNLP data for LM evaluation. |
| `shuffled_NeurIPSwithoutLabels.csv` | Shuffled, unlabeled NeurIPS data for LM evaluation. |

## Usage

### Prerequisites
- Python 3.x
- LM Studio for interacting with language models
- OpenReview API keys for data retrieval

### Steps
1. **Retrieve Data**:
   Run the appropriate script to fetch conference data:
   ```bash
   python API2.0_get_data.py
   python API1.0_get_data.py
   ```
2. **Convert JSON to CSV**:
   Run the conversion scripts:
   ```bash
   python convert_json_csv_emnlp.py
   python convert_json_csv_neurips.py
   python convert_json_csv_iclr.py
   ```
3. **Annotate Reviews**: Manually label 50 positive and 50 negative cases per venue and save labeled CSV files.
4. **Shuffle Labeled Data**:
   ```bash
   python shuffle_csv.py
   ```
5. **Send Prompts to LM**:
   Use `get_response_csv.py` to collect model responses:
   ```bash
   python get_response_csv.py
   ```

## Outputs
The final output is a set of CSV files with an additional `suggest_citation` column containing language model responses. These can be analyzed to assess the models' ability to detect citation suggestions in peer reviews.
