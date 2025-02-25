import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np
import os
import subprocess
import tempfile
import csv
from tqdm import tqdm

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths
zip_path = os.path.join(script_dir, "tl_2024_us_zcta520.shp")
elevation_dir = os.path.join(script_dir, "elevation_tiles")
output_csv = os.path.join(script_dir, "zip_code_elevations.csv")

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

# Load ZIP code shapefile
zips = gpd.read_file(zip_path)

# Check for an existing CSV file and read completed ZIP codes
completed_zip_codes = set()
if os.path.exists(output_csv):
    with open(output_csv, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header
        for row in reader:
            completed_zip_codes.add(row[0])  # Store completed ZIP codes

# Open the CSV file in append mode
with open(output_csv, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)

    # If the file is newly created, write the header
    if not os.path.exists(output_csv) or os.stat(output_csv).st_size == 0:
        writer.writerow(['ZIP Code', 'Average Elevation'])

    # Loop through each ZIP code with a progress bar
    total_zip_codes = len(zips)
    for _, row in tqdm(zips.iterrows(), total=total_zip_codes, desc="Processing ZIP Codes"):
        zip_code = row['ZCTA5CE20']
        
        # Skip already processed ZIP codes
        if zip_code in completed_zip_codes:
            continue

        geometry = row.geometry

        # Find TIF files intersecting the ZIP code geometry
        bbox = geometry.bounds
        tif_files = [
            os.path.join(elevation_dir, tif)
            for tif in os.listdir(elevation_dir)
            if bbox_intersects_tif(bbox, os.path.join(elevation_dir, tif))
        ]

        if len(tif_files) > 0:
            # Create a temporary file for the merged raster
            with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as temp_tif:
                merged_tif_path = temp_tif.name

            # Use GDAL to merge the TIF files
            gdal_merge_script = os.path.join(os.environ['CONDA_PREFIX'], "Scripts", "gdal_merge.py")
            gdal_merge_command = [
                "python", gdal_merge_script,
                "-o", merged_tif_path,
                "-n", "0",  # Specify nodata value
                "-a_nodata", "0"
            ] + tif_files
            subprocess.run(gdal_merge_command, check=True)

            # Clip the merged raster to the ZIP code geometry
            with rasterio.open(merged_tif_path) as src:
                out_image, out_transform = mask(src, [geometry], crop=True)
                data = out_image[0].flatten()
                nodata = src.nodata
                valid_data = data[data != nodata]

                # Calculate average elevation
                if valid_data.size > 0:
                    avg_elevation = np.mean(valid_data)
                    writer.writerow([zip_code, avg_elevation])
                    csvfile.flush()  # Ensure data is written immediately

            # Delete the temporary merged raster
            os.remove(merged_tif_path)
