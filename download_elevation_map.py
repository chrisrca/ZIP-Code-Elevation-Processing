import os
import requests
import zipfile

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths for ZCTA and COUNTY ZIP files
zcta_zip_url = "https://www2.census.gov/geo/tiger/TIGER2024/ZCTA520/tl_2024_us_zcta520.zip"
county_zip_url = "https://www2.census.gov/geo/tiger/TIGER2024/COUNTY/tl_2024_us_county.zip"

zcta_zip_filename = os.path.join(script_dir, "tl_2024_us_zcta520.zip")
county_zip_filename = os.path.join(script_dir, "tl_2024_us_county.zip")

extract_folder = os.path.join(script_dir)
tif_links_file = os.path.join(script_dir, "tif_links.txt")
elevation_folder = os.path.join(script_dir, "elevation_tiles")

# List of required files for each ZIP
REQUIRED_FILES = {
    "zcta": [
        "tl_2024_us_zcta520.cpg",
        "tl_2024_us_zcta520.dbf",
        "tl_2024_us_zcta520.prj",
        "tl_2024_us_zcta520.shp",
        "tl_2024_us_zcta520.shp.ea.iso.xml",
        "tl_2024_us_zcta520.shp.iso.xml",
        "tl_2024_us_zcta520.shx"
    ],
    "county": [
        "tl_2024_us_county.cpg",
        "tl_2024_us_county.dbf",
        "tl_2024_us_county.prj",
        "tl_2024_us_county.shp",
        "tl_2024_us_county.shp.ea.iso.xml",
        "tl_2024_us_county.shp.iso.xml",
        "tl_2024_us_county.shx"
    ]
}

# Function to check if all required files exist
def all_files_exist(folder, file_list):
    return all(os.path.exists(os.path.join(folder, file)) for file in file_list)

# Function to download ZIP files
def download_zip(url, save_path):
    if os.path.exists(save_path):
        print(f"Skipping download, {save_path} already exists.")
        return

    print(f"Downloading {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Downloaded {save_path}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        exit(1)

# Function to extract ZIP files
def extract_zip(zip_path, extract_to, required_files):
    if all_files_exist(extract_to, required_files):
        print(f"Skipping extraction, all required files already exist in {extract_to}.")
        return

    print(f"Extracting {zip_path} to {extract_to}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Extraction complete.")
    except Exception as e:
        print(f"Failed to extract {zip_path}: {e}")
        exit(1)

# Function to download TIF files
def download_files(url_file, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    with open(url_file, "r") as file:
        urls = file.readlines()
    for url in urls:
        url = url.strip()
        if not url:
            continue
        filename = os.path.basename(url)
        save_path = os.path.join(save_dir, filename)
        if os.path.exists(save_path):
            print(f"Skipping {filename}, already exists.")
            continue
        print(f"Downloading {filename}...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            with open(save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"Downloaded {filename} to {save_dir}.")
        except Exception as e:
            print(f"Failed to download {filename}: {e}")

# Download and extract ZCTA data
download_zip(zcta_zip_url, zcta_zip_filename)
extract_zip(zcta_zip_filename, extract_folder, REQUIRED_FILES["zcta"])

# Download and extract COUNTY data
download_zip(county_zip_url, county_zip_filename)
extract_zip(county_zip_filename, extract_folder, REQUIRED_FILES["county"])

# Download elevation TIF files
download_files(tif_links_file, elevation_folder)
