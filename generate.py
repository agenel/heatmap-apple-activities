import os
import gpxpy
import folium
from folium.plugins import HeatMap
import pandas as pd

def extract_gpx_coordinates(folder_path):
    all_coords = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".gpx"):
                gpx_path = os.path.join(root, file)
                with open(gpx_path, 'r') as gpx_file:
                    gpx = gpxpy.parse(gpx_file)
                    for track in gpx.tracks:
                        for segment in track.segments:
                            for point in segment.points:
                                all_coords.append((point.latitude, point.longitude))

    return all_coords

def create_folium_heatmap(coordinates, output_html="cycling_heatmap.html"):
    print(f"Total GPS points collected: {len(coordinates)}")
    if not coordinates:
        print("No GPS data found.")
        return

    # Center the map around the first point
    map_center = coordinates[0]
    fmap = folium.Map(location=map_center, zoom_start=13, tiles='CartoDB positron')

    # Add heatmap layer
    HeatMap(coordinates, radius=8, blur=15).add_to(fmap)

    # Save to HTML file
    fmap.save(output_html)
    print(f"Heatmap saved to: {output_html}")

if __name__ == "__main__":
    gpx_folder = "workout-routes"  # change to your actual GPX folder path
    coordinates = extract_gpx_coordinates(gpx_folder)
    create_folium_heatmap(coordinates)
