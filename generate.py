import os
import gpxpy
import folium
from folium.plugins import HeatMap
import pandas as pd
from datetime import datetime
import streamlit as st
import pickle

# Set page to wide mode
st.set_page_config(layout="wide")

CACHE_FILE = "processed_gps_data.pkl"

def load_or_process_data(folder_path):
    # Check if cache file exists
    if os.path.exists(CACHE_FILE):
        st.info("Loading cached GPS data...")
        with open(CACHE_FILE, 'rb') as f:
            return pickle.load(f)
    
    st.info("Processing GPX files (this may take a while)...")
    all_coords = []
    all_times = []
    
    # First count total GPX files
    total_files = sum(1 for root, _, files in os.walk(folder_path) 
                     for file in files if file.endswith(".gpx"))
    
    processed_files = 0
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".gpx"):
                processed_files += 1
                progress = processed_files / total_files
                progress_bar.progress(progress)
                status_text.text(f"Processing GPX files: {processed_files}/{total_files} files")
                
                gpx_path = os.path.join(root, file)
                with open(gpx_path, 'r') as gpx_file:
                    gpx = gpxpy.parse(gpx_file)
                    for track in gpx.tracks:
                        for segment in track.segments:
                            for point in segment.points:
                                all_coords.append((point.latitude, point.longitude))
                                all_times.append(point.time)
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    # Save processed data
    st.info("Saving processed data for future use...")
    data = {
        'coordinates': all_coords,
        'timestamps': all_times
    }
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(data, f)
    
    return data

@st.cache_data
def create_folium_heatmap(coordinates, output_html="cycling_heatmap.html"):
    if not coordinates:
        print("No GPS data found.")
        return

    # Center the map around the first point
    map_center = coordinates[0]
    fmap = folium.Map(location=map_center, zoom_start=13, tiles='CartoDB positron')

    # Add heatmap layer
    HeatMap(coordinates, radius=8, blur=15).add_to(fmap)
    
    # Add fullscreen control
    folium.plugins.Fullscreen(
        position="topright",
        title="Expand me",
        title_cancel="Exit me",
        force_separate_button=True,
    ).add_to(fmap)

    # Save to HTML file
    fmap.save(output_html)

def main():
    st.title("Apple Fitness Activity Heatmap")
    
    gpx_folder = "workout-routes"  # change to your actual GPX folder path
    
    # Load or process data
    data = load_or_process_data(gpx_folder)
    coordinates = data['coordinates']
    timestamps = data['timestamps']
    
    if not coordinates:
        st.error("No GPS data found.")
        return
    
    # Convert timestamps to datetime objects
    timestamps = [pd.to_datetime(ts) for ts in timestamps]
    
    # Create time window selector
    min_date = min(timestamps).date()
    max_date = max(timestamps).date()
    
    st.write("Select time window:")
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input("Start date", min_date, min_value=min_date, max_value=max_date)
    with col2:
        end_date = st.date_input("End date", max_date, min_value=min_date, max_value=max_date)
    
    # Filter coordinates based on selected time window
    filtered_coords = []
    for coord, ts in zip(coordinates, timestamps):
        if start_date <= ts.date() <= end_date:
            filtered_coords.append(coord)
    
    st.write(f"Showing {len(filtered_coords)} points from {len(coordinates)} total points")
    
    # Create and display the heatmap
    if filtered_coords:
        create_folium_heatmap(filtered_coords)
        with open("cycling_heatmap.html", "r") as f:
            st.components.v1.html(f.read(), height=800, width=None)
    else:
        st.warning("No data points in selected time window")

if __name__ == "__main__":
    main()
