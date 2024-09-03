import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points
import folium
from shapely import wkt

# Step 1: Clean and Sort GNSS Data
def remove_duplicates_and_sort(df):
    df = df.drop_duplicates(subset=['Latitude', 'Longitude'])
    df_sorted = df.sort_values(by='Timestamp')
    return df_sorted

def clean_gnss_data(input_file, output_file, iterations=5):
    df = pd.read_csv(input_file)
    for _ in range(iterations):
        df = remove_duplicates_and_sort(df)
    df = df.iloc[:-3]
    df.to_csv(output_file, index=False)
    print(f"Cleaned and sorted CSV saved to {output_file}")

# Step 2: Map Matching
def fetch_road_network(shapefile_path):
    road_network = gpd.read_file(shapefile_path)
    return road_network

def load_gps_data(file_path):
    gps_data = pd.read_csv(file_path)
    gps_data['geometry'] = gps_data.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
    gps_gdf = gpd.GeoDataFrame(gps_data, geometry='geometry', crs="EPSG:4326")
    return gps_gdf

def find_nearest_road(gps_point, road_network):
    nearest_geom = nearest_points(gps_point, road_network.unary_union)[1]
    return nearest_geom

def match_gps_to_road(gps_gdf, road_network):
    gps_gdf['matched_road'] = gps_gdf['geometry'].apply(lambda point: find_nearest_road(point, road_network))
    return gps_gdf

def perform_map_matching(input_file, road_shapefile, output_file):
    road_network = fetch_road_network(road_shapefile)
    gps_data = load_gps_data(input_file)
    matched_path = match_gps_to_road(gps_data, road_network)
    matched_path.to_csv(output_file, index=False)
    print(f"Map matching completed and saved to {output_file}")

# Step 3: Transform and Save Matched Data
def transform_matched_data(input_csv, output_csv):
    df = pd.read_csv(input_csv)
    if 'matched_road' in df.columns:
        df['Matched_Longitude'] = df['matched_road'].apply(lambda x: x.split(' ')[1].strip('POINT()'))
        df['Matched_Latitude'] = df['matched_road'].apply(lambda x: x.split(' ')[2].strip('POINT()'))
        df = df[['Timestamp', 'Matched_Longitude', 'Matched_Latitude']]
        df.to_csv(output_csv, index=False)
        print(f"Transformed data saved to {output_csv}")
    else:
        print("The 'matched_road' column is not present in the CSV file.")

# Step 4: Visualize on Map
def plot_gnss_data_on_map(data_file, output_map_file, circle_center=None, circle_radius=50):
    df = pd.read_csv(data_file)
    df.columns = df.columns.str.strip()

    if 'Matched_Latitude' in df.columns and 'Matched_Longitude' in df.columns and 'Timestamp' in df.columns:
        df['Matched_Latitude'] = pd.to_numeric(df['Matched_Latitude'], errors='coerce')
        df['Matched_Longitude'] = pd.to_numeric(df['Matched_Longitude'], errors='coerce')
        df.dropna(subset=['Matched_Latitude', 'Matched_Longitude'], inplace=True)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])

        map_center = [df['Matched_Latitude'].mean(), df['Matched_Longitude'].mean()]
        m = folium.Map(location=map_center, zoom_start=15)

        points = df[['Matched_Latitude', 'Matched_Longitude']].values.tolist()
        folium.PolyLine(points, color='blue', weight=2.5, opacity=1).add_to(m)

        for _, row in df.iterrows():
            folium.Marker(
                location=[row['Matched_Latitude'], row['Matched_Longitude']],
                popup=f"Timestamp: {row['Timestamp']}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)

        if circle_center:
            folium.Circle(
                location=circle_center,
                radius=circle_radius,
                color='blue',
                fill=True,
                fill_opacity=0.4
            ).add_to(m)

        m.save(output_map_file)
        print(f"Map saved to {output_map_file}")
    else:
        print("Required columns are missing in the CSV file.")

if __name__ == "__main__":
    # File paths
    raw_gnss_data = '../Location_data/Rahil/Data4/Rahil_gnss_data4.csv'
    cleaned_data_file = '../Location_data/Rahil/Data4/Rahil_final_data4.csv'
    matched_data_file = '../Location_data/Rahil/Data4/matched_gps_to_road.csv'
    final_matched_data_file = '../Location_data/Rahil/Data4/matched_gps_to_road_final.csv'
    road_shapefile = '../Road_data/roads.shp'
    output_map_file = '../output/Rahil/Data4/final/gnss_map.html'
    
    # Coordinates for the circle's center (latitude, longitude)
    circle_center = (22.292576, 73.271293)
    
    # Step 1: Clean and sort GNSS data
    clean_gnss_data(raw_gnss_data, cleaned_data_file)
    
    # Step 2: Perform map matching
    perform_map_matching(cleaned_data_file, road_shapefile, matched_data_file)
    
    # Step 3: Transform and save matched data
    transform_matched_data(matched_data_file, final_matched_data_file)
    
    # Step 4: Plot GNSS data and matched road points on the map
    plot_gnss_data_on_map(final_matched_data_file, output_map_file, circle_center=circle_center, circle_radius=1200)