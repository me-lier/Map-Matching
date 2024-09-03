import pandas as pd

# Load the CSV file
input_csv = '../Location_data/Rahil/Data4/matched_gps_to_road.csv'  # Replace with your file name
output_csv = '../Location_data/Rahil/Data4/matched_gps_to_road_final.csv'  # Output file name

# Read the CSV into a DataFrame
df = pd.read_csv(input_csv)

# Ensure the 'matched_road' column exists
if 'matched_road' in df.columns:
    # Extract longitude and latitude from 'matched_road'
    df['Matched_Longitude'] = df['matched_road'].apply(lambda x: x.split(' ')[1].strip('POINT()'))
    df['Matched_Latitude'] = df['matched_road'].apply(lambda x: x.split(' ')[2].strip('POINT()'))
    
    # Select only the necessary columns
    df = df[['Timestamp', 'Matched_Longitude', 'Matched_Latitude']]
    
    # Save the transformed data to a new CSV file
    df.to_csv(output_csv, index=False)
    print(f'Transformed data saved to {output_csv}')
else:
    print("The 'matched_road' column is not present in the CSV file.")