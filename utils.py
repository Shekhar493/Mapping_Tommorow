import streamlit as st
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point
import folium

@st.cache_data
def fetch_osm_data(place_name, tags):
    """
    Fetches POIs from OpenStreetMap based on tags.
    Cached by Streamlit to avoid re-downloading on every rerun.
    """
    try:
        gdf = ox.features_from_place(place_name, tags)
        # Keep only points
        if not gdf.empty:
             gdf = gdf[gdf.geometry.type == 'Point']
             # Ensure CRS is 4326 for plotting
             if gdf.crs != "EPSG:4326":
                 gdf = gdf.to_crs(epsg=4326)
        return gdf
    except Exception as e:
        st.error(f"Error fetching OSM data: {e}")
        return gpd.GeoDataFrame()

def create_risk_zones():
    """
    Creates hypothetical disaster risk zones.
    """
    # Define disaster-prone points (approximate locations in Pokhara)
    # Seti River Gorge area (Flood Risk)
    flood_center = Point(83.991, 28.228)
    # Sarangkot Slope area (Landslide Risk)
    landslide_center = Point(83.954, 28.243)
    
    # Create GeoDataFrame
    disaster_gdf = gpd.GeoDataFrame(
        {
            "risk_type": ["Flood Risk Zone", "Landslide Risk Zone"],
            "severity": ["High", "High"]
        },
        geometry=[flood_center, landslide_center],
        crs="EPSG:4326"
    )
    
    # Reproject to projected CRS (UTM 45N) for accurate buffering in meters
    disaster_gdf = disaster_gdf.to_crs(epsg=32645)
    
    # Create buffer zones (1.2km for flood, 1km for landslide)
    disaster_gdf["geometry"] = disaster_gdf.geometry.buffer([1200, 1000])
    
    # Reproject back to WGS84
    disaster_gdf = disaster_gdf.to_crs(epsg=4326)
    
    return disaster_gdf

def perform_spatial_analysis(waste_gdf, risk_gdf):
    """
    Finds which waste points fall inside risk zones.
    """
    if waste_gdf.empty or risk_gdf.empty:
        return gpd.GeoDataFrame()
        
    # Spatial join
    joined = gpd.sjoin(waste_gdf, risk_gdf, how="inner", predicate="intersects")
    return joined
