import pandas as pd

def remove_duplicates_and_sort(df):
    # Remove duplicate rows based on Latitude and Longitude
    df = df.drop_duplicates(subset=['Latitude', 'Longitude'])
    
    # Sort the DataFrame by Timestamp
    df_sorted = df.sort_values(by='Timestamp')
    
    return df_sorted

if __name__ == "__main__":
    # Initial input file path
    input_file = '../Location_data/Rahil/Data4/Rahil_gnss_data4.csv'  # Replace with your actual file path
    
    # Load the GNSS data once
    df = pd.read_csv(input_file)
    
    # Process the DataFrame through multiple iterations
    for i in range(5):  # Replace 5 with however many iterations you want
        df = remove_duplicates_and_sort(df)
    
    # Delete the last 3 rows
    df = df.iloc[:-3]
    
    # Save the final cleaned and sorted DataFrame to a single output file
    final_output_file = '../Location_data/Rahil/Data4/Rahil_final_data4.csv'
    df.to_csv(final_output_file, index=False)
    print(f"Final cleaned, sorted, and truncated CSV saved to {final_output_file}")