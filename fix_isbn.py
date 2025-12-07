import pandas as pd

# Load the CSV - ISBN might be stored as float
items_df = pd.read_csv('/Users/alexandrecagnin/Kaggle_datas/items_enriched.csv')

print("Fixing ISBN Valid column to remove .0 decimals...")

# Function to clean ISBN
def clean_isbn_format(isbn):
    if pd.isna(isbn):
        return None
    
    # Convert to string and remove .0 if present
    isbn_str = str(isbn)
    
    # Remove .0 at the end
    if isbn_str.endswith('.0'):
        isbn_str = isbn_str[:-2]
    
    # Return as string (13 digits)
    return isbn_str

# Apply to ISBN Valid column
items_df['ISBN Valid'] = items_df['ISBN Valid'].apply(clean_isbn_format)

# Also ensure Publication_Date is integer without decimals
items_df['Publication_Date'] = items_df['Publication_Date'].astype('Int64')

# Save back to CSV
items_df.to_csv('/Users/alexandrecagnin/Kaggle_datas/items_enriched.csv', index=False)

print("✓ Successfully fixed ISBN Valid column")
print("\nSample ISBNs (first 10 non-null):")
sample_isbns = items_df[items_df['ISBN Valid'].notna()]['ISBN Valid'].head(10).tolist()
for i, isbn in enumerate(sample_isbns, 1):
    print(f"{i}. {isbn}")
