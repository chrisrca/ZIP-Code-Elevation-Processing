import os
import requests
import zipfile

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths
zip_url = "https://www2.census.gov/geo/tiger/TIGER2024/ZCTA520/tl_2024_us_zcta520.zip"
zip_filename = os.path.join(script_dir, "tl_2024_us_zcta520.zip")
extract_folder = os.path.join(script_dir)
tif_links_file = os.path.join(script_dir, "tif_links.txt")
elevation_folder = os.path.join(script_dir, "elevation_tiles")

# List of required files to check before extraction
REQUIRED_FILES = [
    "tl_2024_us_zcta520.cpg",
    "tl_2024_us_zcta520.dbf",
    "tl_2024_us_zcta520.prj",
    "tl_2024_us_zcta520.shp",
    "tl_2024_us_zcta520.shp.ea.iso.xml",
    "tl_2024_us_zcta520.shp.iso.xml",
    "tl_2024_us_zcta520.shx"
]

# Function to check if all required files exist
def all_files_exist(folder, file_list):
    return all(os.path.exists(os.path.join(folder, file)) for file in file_list)

# Function to download the ZIP file
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

# Function to extract the ZIP file only if required files are missing
def extract_zip(zip_path, extract_to):
    if all_files_exist(extract_to, REQUIRED_FILES):
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

download_zip(zip_url, zip_filename)
extract_zip(zip_filename, extract_folder)
download_files(tif_links_file, elevation_folder)
