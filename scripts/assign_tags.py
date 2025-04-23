import os
import pandas as pd

# path to the annotated data
folder_path = r'C:\Users\zoehu\OneDrive - stud.uni-goettingen.de\Thesis\review-citation-bias\annotated_data'

# go through each file in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):  # Process only CSV files
        file_path = os.path.join(folder_path, file_name)

        df = pd.read_csv(file_path)
        
        # check if the "response" column exists (only LM annotated versions have "response" column)
        if 'response' in df.columns:
            # add the "binary_label" column
            df['binary_label'] = df['response'].apply(lambda x: 1 if 'yes' in str(x).lower() else 0)
            
            # Save the updated DataFrame back to the file
            df.to_csv(file_path, index=False)
            print(f"Updated file: {file_name}")
        else:
            print(f"'response' column not found in {file_name}")
