import pandas as pd

# Load the data
items_df = pd.read_csv('/Users/alexandrecagnin/Kaggle_datas/items.csv')

# Filter to borrowed books
interactions_df = pd.read_csv('/Users/alexandrecagnin/Kaggle_datas/interactions.csv')
borrowed_items = set(interactions_df['i'].unique())
items_df = items_df[items_df['i'].isin(borrowed_items)]

# Clean ISBN Valid column
def clean_isbn(isbn_str):
    if pd.isna(isbn_str):
        return None
    
    isbns = str(isbn_str).split(';')
    
    for isbn in isbns:
        isbn = isbn.strip()
        digits = ''.join(filter(str.isdigit, isbn))
        if len(digits) >= 13 and (digits.startswith('978') or digits.startswith('979')):
            return digits[:13]
    
    return None

items_df['ISBN Valid'] = items_df['ISBN Valid'].apply(clean_isbn)

# Get books with missing ISBNs
missing_isbn_books = items_df[items_df['ISBN Valid'].isna()][['i', 'Title', 'Author', 'Publisher']].copy()

print(f"Total books with missing ISBN: {len(missing_isbn_books)}\n")
print("=" * 100)
print(f"{'ID':<6} {'Title':<60} {'Author':<30}")
print("=" * 100)

for idx, row in missing_isbn_books.iterrows():
    title = str(row['Title'])[:58] if pd.notna(row['Title']) else 'N/A'
    author = str(row['Author'])[:28] if pd.notna(row['Author']) else 'N/A'
    print(f"{row['i']:<6} {title:<60} {author:<30}")
