import requests
import pandas as pd

# Census API URL
base_url = "https://api.census.gov/data/2023/acs/acs5"
params = {
    "get": "NAME,B01003_001E",
    "for": "tract:*",
}

# List of state FIPS codes (01 = Alabama, 02 = Alaska, ..., 56 = Wyoming)
state_fips_codes = [f"{i:02d}" for i in range(1, 57)]

# Collect data from all states
all_data = []
for state in state_fips_codes:
    params["in"] = f"state:{state}"
    resp = requests.get(base_url, params=params)

    if resp.status_code == 200:
        try:
            data = resp.json()
            all_data.extend(data[1:])  # Skip the header row
        except requests.exceptions.JSONDecodeError:
            print(f"JSON error for state {state}: {resp.text}")
    else:
        print(f"Failed request for state {state}: {resp.status_code} - {resp.text}")

# Convert to DataFrame
df = pd.DataFrame(all_data, columns=["NAME", "Total_Population", "State", "County", "Tract"])

# Create GEOID (Census Tract Identifier)
df["GEOID"] = df["State"] + df["County"] + df["Tract"]

# Select only GEOID and Total Population
df = df[["GEOID", "Total_Population"]]

# Save to CSV
df.to_csv("census_population.csv", index=False)

print("✅ Census population data saved as 'census_population.csv'")
