import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely.ops import nearest_points

def convert_shapefile_to_geojson(shapefile_path, geojson_path):
    # Load the shapefile
    gdf = gpd.read_file(shapefile_path)
    
    # Save to GeoJSON format
    gdf.to_file(geojson_path, driver='GeoJSON')

def fetch_road_network(shapefile_path):
    # Load the road network shapefile
    road_network = gpd.read_file(shapefile_path)
    
    return road_network

def load_gps_data(file_path):
    # Load the GPS data
    gps_data = pd.read_csv(file_path)
    
    # Convert GPS data into a GeoDataFrame
    gps_data['geometry'] = gps_data.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
    gps_gdf = gpd.GeoDataFrame(gps_data, geometry='geometry', crs="EPSG:4326")  # Assuming WGS84 (EPSG:4326)
    
    return gps_gdf

def match_gps_to_road(gps_gdf, road_network):
    # Function to find the nearest road segment for a given GPS point
    def find_nearest_road(gps_point, road_network):
        nearest_geom = nearest_points(gps_point, road_network.unary_union)[1]
        return nearest_geom
    
    # Apply the function to map GPS points to the nearest road segments
    gps_gdf['matched_road'] = gps_gdf['geometry'].apply(lambda point: find_nearest_road(point, road_network))
    
    return gps_gdf

def main():
    # Convert shapefile to GeoJSON (if needed)
    convert_shapefile_to_geojson('../Road_data/roads.shp', '../Road_data/roads.geojson')

    # Load the GPS data
    gps_data = load_gps_data('../Location_data/Rahil/Data3/Rahil_final_data3.csv')
    
    # Load the road network shapefile
    road_network = fetch_road_network('../Road_data/roads.shp')
    
    # Perform map matching
    matched_path = match_gps_to_road(gps_data, road_network)
    
    # Optionally, save the matched path to a file
    matched_path.to_csv('../Location_data/Rahil/Data3/matched_gps_to_road.csv', index=False)
    print("Map matching completed and saved to 'matched_gps_to_road.csv'.")

if __name__ == "__main__":
    main()