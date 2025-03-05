import pandas as pd
import geopandas as gpd

# File paths (modify these as needed)
tract_elevations_file = "tract_elevations.csv"
population_data_file = "census_population.csv"
tracts_shapefile = "tl_2024_us_tract.shp"
counties_shapefile = "tl_2024_us_county.shp"
output_csv = "county_weighted_elevations.csv"

# Load tract elevation data
tract_elevations = pd.read_csv(tract_elevations_file, dtype={"Tract ID": str})
tract_elevations.rename(columns={"Tract ID": "GEOID", "Average Elevation": "Elevation"}, inplace=True)

# Load population data
population_data = pd.read_csv(population_data_file, dtype={"GEOID": str})

# Merge elevation and population data
merged_data = pd.merge(tract_elevations, population_data, on="GEOID", how="left")

# Handle missing population values by filling them with the median population
median_population = merged_data["Total_Population"].median()
merged_data["Total_Population"].fillna(median_population, inplace=True)

# Load census tract shapefile (keeping only relevant columns)
tracts = gpd.read_file(tracts_shapefile)[["GEOID", "COUNTYFP", "STATEFP"]]

# Create full County FIPS by combining State FIPS and County FIPS
tracts["County_FIPS"] = tracts["STATEFP"] + tracts["COUNTYFP"]

# Load county shapefile to get county names
counties = gpd.read_file(counties_shapefile)[["STATEFP", "COUNTYFP", "NAME"]]
counties["County_FIPS"] = counties["STATEFP"] + counties["COUNTYFP"]

# Merge county information into the tract data
merged_data = pd.merge(merged_data, tracts[["GEOID", "County_FIPS"]], on="GEOID", how="left")

# Compute population-weighted average elevation for each county
weighted_elevations = merged_data.groupby("County_FIPS").apply(
    lambda x: (x["Elevation"] * x["Total_Population"]).sum() / x["Total_Population"].sum()
).reset_index(name="Weighted_Avg_Elevation")

# Merge with county names
final_results = pd.merge(weighted_elevations, counties[["County_FIPS", "NAME"]], on="County_FIPS", how="left")

# Save to CSV
final_results.to_csv(output_csv, index=False)

print(f"Weighted county elevations saved to {output_csv}")
