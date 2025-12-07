import pandas as pd
import requests
import time

# Load the enriched dataset
items_df = pd.read_csv('/Users/alexandrecagnin/Kaggle_datas/items_enriched.csv',
                       dtype={'ISBN Valid': str, 'Publication_Date': 'Int64'})

def get_author_from_google_books(isbn=None, title=None):
    """Get author from Google Books API"""
    try:
        if isbn:
            query = f"isbn:{isbn}"
        elif title:
            query = f"intitle:{title}"
        else:
            return None
        
        url = "https://www.googleapis.com/books/v1/volumes"
        params = {"q": query, "maxResults": 1}
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                volume_info = data['items'][0].get('volumeInfo', {})
                authors = volume_info.get('authors', [])
                if authors:
                    # Return first author or join multiple authors
                    return authors[0] if len(authors) == 1 else ', '.join(authors[:3])
        
        return None
    except:
        return None

def get_author_from_openlibrary(isbn=None, title=None):
    """Get author from OpenLibrary API"""
    try:
        if isbn:
            url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                book_key = f"ISBN:{isbn}"
                if book_key in data:
                    authors = data[book_key].get('authors', [])
                    if authors:
                        # Extract author names
                        author_names = [a.get('name', '') for a in authors if 'name' in a]
                        if author_names:
                            return author_names[0] if len(author_names) == 1 else ', '.join(author_names[:3])
        else:
            # Search by title
            url = "https://openlibrary.org/search.json"
            params = {'title': title, 'limit': 1}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('docs') and len(data['docs']) > 0:
                    doc = data['docs'][0]
                    author_name = doc.get('author_name', [])
                    if author_name:
                        return author_name[0] if len(author_name) == 1 else ', '.join(author_name[:3])
        
        return None
    except:
        return None

def find_author(isbn=None, title=None):
    """Try both APIs to find author"""
    # Try Google Books first
    author = get_author_from_google_books(isbn, title)
    if author:
        return author, "Google Books"
    
    time.sleep(0.2)
    
    # Try OpenLibrary as fallback
    author = get_author_from_openlibrary(isbn, title)
    if author:
        return author, "OpenLibrary"
    
    time.sleep(0.2)
    
    return None, None

# Filter books with missing authors
missing_authors = items_df['Author'].isna()
books_to_process = items_df[missing_authors].copy()

total_missing = len(books_to_process)
print(f"Searching authors for {total_missing} books...")
print(f"Estimated time: {total_missing * 0.4 / 60:.1f} minutes with rate limiting.\n")

found_count = 0
not_found_count = 0

for idx, row in books_to_process.iterrows():
    isbn = row['ISBN Valid'] if pd.notna(row['ISBN Valid']) else None
    title = row['Title'] if pd.notna(row['Title']) else None
    
    author, source = find_author(isbn, title)
    
    if author:
        items_df.at[idx, 'Author'] = author
        found_count += 1
        if found_count % 50 == 0:
            print(f"Progress: {found_count + not_found_count}/{total_missing} - Found {found_count} authors")
    else:
        not_found_count += 1
    
    time.sleep(0.4)  # Rate limiting

# Save updated dataset
items_df.to_csv('/Users/alexandrecagnin/Kaggle_datas/items_enriched.csv', index=False)

# Final statistics
final_missing = items_df['Author'].isna().sum()
total = len(items_df)

print(f"\n{'='*80}")
print("AUTHOR ENRICHMENT COMPLETE")
print(f"{'='*80}")
print(f"Authors found via API: {found_count}")
print(f"Not found: {not_found_count}")
print(f"\nFinal statistics:")
print(f"Books WITH author: {total - final_missing}/{total} ({(total-final_missing)/total*100:.2f}%)")
print(f"Books with NO author: {final_missing}/{total} ({final_missing/total*100:.2f}%)")
print(f"Improvement: Reduced missing authors from {total_missing} to {final_missing}")
print(f"\n✓ Updated items_enriched.csv")

# Show sample results
print(f"\nSample of newly found authors (first 10):")
print("=" * 80)
newly_found = items_df.loc[books_to_process.index][items_df.loc[books_to_process.index, 'Author'].notna()]
sample = newly_found[['Title', 'Author']].head(10)
for idx, row in sample.iterrows():
    title = row['Title'][:60] + '...' if len(str(row['Title'])) > 60 else row['Title']
    print(f"Title: {title}")
    print(f"Author: {row['Author']}\n")
