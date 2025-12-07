import pandas as pd
import re

# Load the enriched dataset
items_df = pd.read_csv('/Users/alexandrecagnin/Kaggle_datas/items_enriched.csv')

def extract_year(date_str):
    """Extract year from various date formats"""
    if pd.isna(date_str):
        return None
    
    date_str = str(date_str)
    
    # Look for 4-digit year pattern
    year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
    
    if year_match:
        return int(year_match.group())
    
    return None

# Apply year extraction to Publication_Date column
print("Extracting years from Publication_Date column...")
items_df['Publication_Date'] = items_df['Publication_Date'].apply(extract_year)

# Convert to Int64 (nullable integer) to avoid .0 decimals in CSV
items_df['Publication_Date'] = items_df['Publication_Date'].astype('Int64')

# Save back to the same file (overwriting)
items_df.to_csv('/Users/alexandrecagnin/Kaggle_datas/items_enriched.csv', index=False)

# Display statistics
total = len(items_df)
with_year = items_df['Publication_Date'].notna().sum()
missing = total - with_year

print(f"\n✓ Successfully updated items_enriched.csv")
print(f"Books with publication year: {with_year}/{total} ({with_year/total*100:.2f}%)")
print(f"Missing years: {missing}/{total} ({missing/total*100:.2f}%)")

# Show sample of updated dates
print("\nSample of updated Publication_Date column (first 10 non-null values):")
print(items_df[items_df['Publication_Date'].notna()]['Publication_Date'].head(10).to_list())
