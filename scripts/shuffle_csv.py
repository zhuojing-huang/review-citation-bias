import pandas as pd
import random

def shuffle_csv_rows(input_file, output_file):
    """
    Shuffles the rows of a CSV file and writes the result to a new file.

    Parameters:
    - input_file (str): Path to the input CSV file.
    - output_file (str): Path to save the shuffled CSV file.
    """
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Shuffle the DataFrame rows
    shuffled_df = df.sample(frac=1, random_state=random.randint(0, 10000)).reset_index(drop=True)
    
    # Write the shuffled DataFrame to a new CSV file
    shuffled_df.to_csv(output_file, index=False)

# Example usage
shuffle_csv_rows('NeurIPSwithoutLabels.csv', 'shuffled_NeurIPSwithoutLabels.csv')
