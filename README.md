# ZIP Code Elevation Processing

## Overview
This project calculates the average elevation for all ZIP codes (ZCTAs) in the United States using high-resolution elevation data. It outputs a CSV file with ZIP codes and their corresponding average elevations, which can be used for studying correlations between elevation and health outcomes like skin cancer.

## Data Sources
1. **Elevation Data**:
   - Source: [USGS National Map Elevation Data](https://www.usgs.gov/)
   - AWS Bucket: [USGS Elevation AWS Bucket](https://prd-tnm.s3.amazonaws.com/index.html?prefix=)
   - Resolution: ~30 meters (~1/9 arc-second)
   - Format: GeoTIFF files

2. **ZIP Code Data (ZCTAs)**:
   - Source: [U.S. Census Bureau TIGER/Line Shapefiles](https://www2.census.gov/geo/tiger/TIGER2024/ZCTA520/)
   - Format: Shapefiles (.shp)

## Usage Instructions

### Step 1: Set Up the Conda Environment
This project requires specific dependencies that can be installed using a [Conda environment](https://www.anaconda.com/download).

1. Open an Anaconda Prompt and use the provided `environment.yml` file to recreate the environment:
   ```bash
   conda env create -f environment.yml
   ```

2. Activate the environment:
   ```bash
   conda activate elevation_analysis_env
   ```

### Step 2: Download Elevation Data
1. Ensure that the `tif_links.txt` file is in the project directory (it should be by default when cloning the repository). This file contains the URLs of the required elevation GeoTIFF files.

2. Run the download script in the conda environment to fetch the elevation data:
   ```bash
   python path/to/download_elevation_map.py
   ```
   This script downloads the ZIP Code shapefile archive and the elevation tiles dataset. The ZIP Code archive will automatically unzip. Ensure sufficient storage (~500GB) is available for the elevation tiles which will install to the `elevation_tiles` directory.

### Step 3: Calculate ZIP Code Elevations
1. Run the elevation processing script in the conda environment:
   ```bash
   python path/to/process_elevations.py
   ```
   This script generates the `zip_code_elevations.csv` file, which contains the average elevation for each ZIP code.

## Output
The final output is a CSV file `zip_code_elevations.csv`, containing:
- `ZIP Code`: The ZIP code (ZCTA).
- `Average Elevation`: The average elevation above sea level in meters for the corresponding ZIP code.

## Notes
1. The elevation data requires significant storage (~500GB).
2. Processing time may vary depending on hardware and network speeds, but can take multiple days due to the size of the dataset.
3. Both scripts will pick up downloading/processing where they left off when run again in the event that the program was previously terminated early. 
