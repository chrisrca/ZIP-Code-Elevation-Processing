import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np
import os
import csv
from tqdm import tqdm

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths
tract_path = os.path.join(script_dir, "tl_2024_us_tract.shp")
elevation_dir = os.path.join(script_dir, "elevation_tiles")
output_csv = os.path.join(script_dir, "tract_elevations.csv")

# Function to check if a bounding box intersects a TIF file
def bbox_intersects_tif(bbox, tif_path):
    with rasterio.open(tif_path) as src:
        tif_bounds = src.bounds
        return not (
            bbox[2] < tif_bounds.left or
            bbox[0] > tif_bounds.right or
            bbox[3] < tif_bounds.bottom or
            bbox[1] > tif_bounds.top
        )

# Load tract shapefile
tracts = gpd.read_file(tract_path)

# Check for an existing CSV file and read completed tracts
completed_tracts = set()
if os.path.exists(output_csv):
    with open(output_csv, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            completed_tracts.add(row[0])  # Store completed tract IDs

# Open the CSV file in append mode
with open(output_csv, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # If the file is newly created, write the header
    if not os.path.exists(output_csv) or os.stat(output_csv).st_size == 0:
        writer.writerow(['Tract ID', 'Average Elevation'])

    # Loop through each tract with a progress bar
    total_tracts = len(tracts)
    for _, row in tqdm(tracts.iterrows(), total=total_tracts, desc="Processing Census Tracts"):
        tract_id = row['GEOID']  # Adjust field name if necessary
        
        # Skip already processed tracts
        if tract_id in completed_tracts:
            continue

        geometry = row.geometry

        # Find TIF files intersecting the tract geometry
        bbox = geometry.bounds
        tif_files = [
            os.path.join(elevation_dir, tif)
            for tif in os.listdir(elevation_dir)
            if bbox_intersects_tif(bbox, os.path.join(elevation_dir, tif))
        ]

        if len(tif_files) > 0:
            valid_elevations = []
            
            for tif in tif_files:
                try:
                    with rasterio.open(tif) as src:
                        out_image, out_transform = mask(src, [geometry], crop=True)
                        data = out_image[0].flatten()
                        nodata = src.nodata
                        valid_data = data[data != nodata]

                        # Store valid elevation values
                        if valid_data.size > 0:
                            valid_elevations.extend(valid_data)
                except Exception as e:
                    print(f"Warning: Skipping {tif} due to error - {e}")

            # Compute the final average elevation across all valid points
            if valid_elevations:
                final_avg_elevation = np.mean(valid_elevations)
                writer.writerow([tract_id, final_avg_elevation])
                csvfile.flush()  # Ensure data is written immediately
