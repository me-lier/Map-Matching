import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import nearest_points
import folium
from streamlit_folium import st_folium
import zipfile
import os
import io
import shutil

# Step 1: Clean and Sort GNSS Data
def remove_duplicates_and_sort(df):
    df = df.drop_duplicates(subset=['Latitude', 'Longitude'])
    df_sorted = df.sort_values(by='Timestamp')
    return df_sorted

def clean_gnss_data(df, iterations=5):
    for _ in range(iterations):
        df = remove_duplicates_and_sort(df)
    df = df.iloc[:-3]
    return df

# Step 2: Map Matching
def fetch_road_network(shapefile_path):
    road_network = gpd.read_file(shapefile_path)
    return road_network

def load_gps_data(df):
    df['geometry'] = df.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
    gps_gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
    return gps_gdf

def find_nearest_road(gps_point, road_network):
    nearest_geom = nearest_points(gps_point, road_network.unary_union)[1]
    return nearest_geom

def match_gps_to_road(gps_gdf, road_network):
    gps_gdf['matched_road'] = gps_gdf['geometry'].apply(lambda point: find_nearest_road(point, road_network))
    return gps_gdf

# Step 3: Transform and Save Matched Data
def transform_matched_data(df):
    df['Matched_Longitude'] = df['matched_road'].apply(lambda x: x.x)
    df['Matched_Latitude'] = df['matched_road'].apply(lambda x: x.y)
    df = df[['Timestamp', 'Matched_Longitude', 'Matched_Latitude']]
    return df

# Step 4: Visualize on Map
def plot_gnss_data_on_map(df, circle_center=None, circle_radius=50):
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
    return m

# Streamlit app
def main():
    st.title("GNSS Data Processing and Visualization")
    
    # File upload for GNSS data
    uploaded_gnss_file = st.file_uploader("Upload your GNSS CSV file", type="csv")
    
    if uploaded_gnss_file is not None:
        df = pd.read_csv(uploaded_gnss_file)
        
        # Clean and process GNSS data
        st.write("### Step 1: Clean and sort GNSS data")
        cleaned_df = clean_gnss_data(df)
        st.write("Cleaned Data", cleaned_df)
        
        # Upload ZIP file containing shapefile components
        uploaded_shapefile_zip = st.file_uploader("Upload your Road Network Shapefile (ZIP)", type="zip")
        if uploaded_shapefile_zip:
            with zipfile.ZipFile(uploaded_shapefile_zip, 'r') as z:
                # Create a temporary directory
                shapefile_dir = 'temp_shapefile'
                os.makedirs(shapefile_dir, exist_ok=True)
                
                # Extract all files from the ZIP
                z.extractall(shapefile_dir)
                
                # Locate the shapefile (assume it's named 'roads.shp')
                shapefile_path = os.path.join(shapefile_dir, 'roads.shp')
                if os.path.isfile(shapefile_path):
                    st.write("### Step 2: Perform map matching")
                    road_network = fetch_road_network(shapefile_path)
                    gps_gdf = load_gps_data(cleaned_df)
                    matched_gdf = match_gps_to_road(gps_gdf, road_network)
                    
                    # Remove the geometry column before displaying
                    matched_df = matched_gdf.drop(columns=['geometry', 'matched_road'])
                    st.write("Matched Data", matched_df)
                    
                    # Transform matched data
                    st.write("### Step 3: Transform and save matched data")
                    transformed_df = transform_matched_data(matched_gdf)
                    st.write("Transformed Data", transformed_df)
                    
                    # Plot GNSS data on map
                    st.write("### Step 4: Plot GNSS data on the map")
                    circle_center = st.text_input("Enter Circle Center as (latitude,longitude)", "22.292576,73.271293")
                    circle_radius = st.slider("Circle Radius (meters)", 50, 2000, 1200)
                    
                    if circle_center:
                        lat, lon = map(float, circle_center.split(","))
                        m = plot_gnss_data_on_map(transformed_df, circle_center=(lat, lon), circle_radius=circle_radius)
                        st_folium(m, width=800, height=600)
                else:
                    st.error("Shapefile 'roads.shp' not found in the uploaded ZIP.")
                
                # Clean up temporary directory
                shutil.rmtree(shapefile_dir)

if __name__ == "__main__":
    main()