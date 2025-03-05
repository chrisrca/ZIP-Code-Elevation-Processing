import os
import requests
import zipfile
import shutil
import geopandas as gpd
import pandas as pd  # ✅ Fix: Import pandas
import rasterio
from rasterio.mask import mask
import numpy as np
import subprocess
import tempfile
import csv
from tqdm import tqdm

# Define directories
script_dir = os.path.dirname(os.path.abspath(__file__))
tracts_dir = os.path.join(script_dir, "tracts")
elevation_dir = os.path.join(script_dir, "elevation_tiles")
output_csv = os.path.join(script_dir, "county_weighted_elevation.csv")

# Census tract download URL template
BASE_URL = "https://www2.census.gov/geo/tiger/TIGER2024/TRACT/"
STATE_FIPS = [f"{i:02d}" for i in range(1, 57)]  # 01-56 for all states (excluding territories)

# Ensure tracts directory exists
os.makedirs(tracts_dir, exist_ok=True)

# Function to download and extract Census Tract files
def download_and_extract_tracts():
    for state in tqdm(STATE_FIPS, desc="Downloading Census Tract Shapefiles"):
        zip_filename = f"tl_2024_{state}_tract.zip"
        zip_path = os.path.join(tracts_dir, zip_filename)
        shapefile_path = os.path.join(tracts_dir, f"tl_2024_{state}_tract.shp")

        # Skip if already extracted
        if os.path.exists(shapefile_path):
            continue

        # Download file
        url = BASE_URL + zip_filename
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(zip_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)

                # Extract the ZIP file
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(tracts_dir)

                # Remove ZIP file after extraction
                os.remove(zip_path)
            else:
                print(f"Failed to download {zip_filename}: {response.status_code}")

        except Exception as e:
            print(f"Error downloading {zip_filename}: {e}")

# Run the download function
download_and_extract_tracts()

# Merge all state tract files into one nationwide file
print("Merging Census Tract Shapefiles...")
all_tracts = gpd.GeoDataFrame()
for state in STATE_FIPS:
    shapefile_path = os.path.join(tracts_dir, f"tl_2024_{state}_tract.shp")
    if os.path.exists(shapefile_path):
        gdf = gpd.read_file(shapefile_path)
        all_tracts = pd.concat([all_tracts, gdf])  # ✅ Fix: Ensure pandas is imported

# Save merged tracts to one file
merged_tract_file = os.path.join(script_dir, "tl_2024_us_tract.shp")
all_tracts.to_file(merged_tract_file)
print("✅ Merged nationwide Census Tract shapefile saved.")

# Define path to population CSV
population_csv = os.path.join(script_dir, "census_population.csv")

# Run the elevation script (modify path as needed)
print("Running elevation analysis...")
subprocess.run(["python3", os.path.join(script_dir, "elevation_script.py")])

print("✅ All processes complete.")
