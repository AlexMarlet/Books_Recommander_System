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
missing_isbn_books = items_df[items_df['ISBN Valid'].isna()][['i', 'Title', 'Author', 'Publisher', 'Subjects']].copy()

# Export to CSV
output_file = '/Users/alexandrecagnin/Kaggle_datas/books_missing_isbn.csv'
missing_isbn_books.to_csv(output_file, index=False)

print(f"Exported {len(missing_isbn_books)} books with missing ISBNs to: {output_file}")
