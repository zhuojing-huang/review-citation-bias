import pandas as pd

# excel path
excel_file =  "ICLRwithLables.xlsx" 

# specific sheet
sheet_name = "Sheet1"
df = pd.read_excel(excel_file, sheet_name=sheet_name)

# save as csv
csv_file = "ICLRwithLabels.csv" 
df.to_csv(csv_file, index=False)

print(f"Sheet '{sheet_name}' has been converted to {csv_file}.")
