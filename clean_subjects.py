import pandas as pd

# Load the enriched dataset
items_df = pd.read_csv('/Users/alexandrecagnin/Kaggle_datas/items_enriched.csv')

# Replace -- with ; in Subjects column
print("Replacing '--' with ';' in Subjects column...")
items_df['Subjects'] = items_df['Subjects'].str.replace('--', ';', regex=False)

# Save back to the same file
items_df.to_csv('/Users/alexandrecagnin/Kaggle_datas/items_enriched.csv', index=False)

print("✓ Successfully updated items_enriched.csv")

# Show sample of updated Subjects
print("\nSample of updated Subjects column (first 5 non-null values):")
subjects_sample = items_df[items_df['Subjects'].notna()]['Subjects'].head(5)
for idx, subject in enumerate(subjects_sample, 1):
    print(f"{idx}. {subject}")
