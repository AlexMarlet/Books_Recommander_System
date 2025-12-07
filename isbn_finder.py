import requests
import time
import pandas as pd

def search_openlibrary_isbn(title, author=None):
    """
    Search for ISBN using OpenLibrary API
    Returns ISBN-13 if found, None otherwise
    """
    try:
        # Build search query
        query = f"title:{title}"
        if author:
            query += f" author:{author}"
        
        url = "https://openlibrary.org/search.json"
        params = {"q": query, "limit": 1}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('docs') and len(data['docs']) > 0:
            book = data['docs'][0]
            
            # Try to get ISBN-13
            if 'isbn' in book:
                for isbn in book['isbn']:
                    if len(isbn) == 13 and (isbn.startswith('978') or isbn.startswith('979')):
                        return isbn
        
        return None
    except Exception as e:
        print(f"OpenLibrary API error: {e}")
        return None


def search_google_books_isbn(title, author=None):
    """
    Search for ISBN using Google Books API
    Returns ISBN-13 if found, None otherwise
    """
    try:
        # Build search query
        query = f"intitle:{title}"
        if author:
            query += f" inauthor:{author}"
        
        url = "https://www.googleapis.com/books/v1/volumes"
        params = {"q": query, "maxResults": 1}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'items' in data and len(data['items']) > 0:
            volume_info = data['items'][0].get('volumeInfo', {})
            
            # Try to get ISBN-13 from industryIdentifiers
            if 'industryIdentifiers' in volume_info:
                for identifier in volume_info['industryIdentifiers']:
                    if identifier['type'] == 'ISBN_13':
                        isbn = identifier['identifier'].replace('-', '')
                        if len(isbn) == 13:
                            return isbn
        
        return None
    except Exception as e:
        print(f"Google Books API error: {e}")
        return None


def find_isbn(title, author=None, use_google=True, use_openlibrary=True):
    """
    Try to find ISBN using available APIs
    Returns (isbn, source) tuple
    """
    # Try Google Books first (usually more reliable)
    if use_google:
        isbn = search_google_books_isbn(title, author)
        if isbn:
            return isbn, "Google Books"
        time.sleep(0.2)  # Rate limiting
    
    # Try OpenLibrary as fallback
    if use_openlibrary:
        isbn = search_openlibrary_isbn(title, author)
        if isbn:
            return isbn, "OpenLibrary"
        time.sleep(0.2)  # Rate limiting
    
    return None, None


# Test the functions
if __name__ == "__main__":
    # Load the items to test
    items_df = pd.read_csv('/Users/alexandrecagnin/Kaggle_datas/items.csv')
    
    # Get a few books with missing ISBNs to test
    test_books = items_df[items_df['ISBN Valid'].isna()].head(5)
    
    print("Testing API functions with books missing ISBNs:\n")
    print("=" * 80)
    
    for idx, row in test_books.iterrows():
        title = row['Title']
        author = row['Author'] if pd.notna(row['Author']) else None
        
        print(f"\nTitle: {title}")
        print(f"Author: {author}")
        
        isbn, source = find_isbn(title, author)
        
        if isbn:
            print(f"✓ Found ISBN: {isbn} (Source: {source})")
        else:
            print("✗ No ISBN found")
        
        print("-" * 80)
        time.sleep(1)  # Rate limiting between requests
