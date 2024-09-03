import pandas as pd
import folium

def plot_gnss_data_on_map2(data_file, output_map_file, circle_center=None, circle_radius=50):
    # Load the GNSS data
    df = pd.read_csv(data_file)
    
    # Clean column names (in case of extra spaces)
    df.columns = df.columns.str.strip()
    
    # Print column names to confirm
    print("Columns in DataFrame:", df.columns)

    # Convert Latitude and Longitude to numeric
    if 'Latitude' in df.columns and 'Longitude' in df.columns and 'Timestamp' in df.columns:
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        
        # Drop rows with NaN values after conversion
        df.dropna(subset=['Latitude', 'Longitude'], inplace=True)
        
        # Convert Timestamp to datetime
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Get the start and end points
        start_point = df.iloc[0]
        end_point = df.iloc[-1]
        
        # Create a map centered around the mean of the coordinates
        map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
        m = folium.Map(location=map_center, zoom_start=15)

        # Add a polyline representing the path
        points = df[['Latitude', 'Longitude']].values.tolist()
        folium.PolyLine(points, color='blue', weight=2.5, opacity=1).add_to(m)
        
        # Add all GNSS points to the map
        for _, row in df.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"Timestamp: {row['Timestamp']}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
        
        # Add start point to the map
        folium.Marker(
            location=[start_point['Latitude'], start_point['Longitude']],
            popup=f"Start Point: {start_point['Timestamp']}",
            icon=folium.Icon(color='green', icon='play')
        ).add_to(m)
        
        # Add end point to the map
        folium.Marker(
            location=[end_point['Latitude'], end_point['Longitude']],
            popup=f"End Point: {end_point['Timestamp']}",
            icon=folium.Icon(color='red', icon='stop')
        ).add_to(m)

        # Add a circle around a specific point (if provided)
        if circle_center:
            folium.Circle(
                location=circle_center,
                radius=circle_radius,  # Radius in meters
                color='blue',
                fill=True,
                fill_opacity=0.4
            ).add_to(m)

        # Save the map to an HTML file
        m.save(output_map_file)
        print(f"Map saved to {output_map_file}")
    else:
        print("Required columns are missing in the CSV file.")

if __name__ == "__main__":
    # File paths
    data_file = '../Location_data/Rahil/Data4/matched_gps_to_road_final.csv'
    output_map_file = '../output/Rahil/Data4/final/gnss_map.html'
    
    # Coordinates for the circle's center (latitude, longitude)
    circle_center = (22.292576, 73.271293)  # Example coordinates
    
    # Plot GNSS data on the map with a circle of 100 meters radius
    plot_gnss_data_on_map(data_file, output_map_file, circle_center=circle_center, circle_radius=1200)